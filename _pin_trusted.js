#!/usr/bin/env node
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[trusted]", ...a); }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function connect(url) {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(url);
    ws.onopen = () => resolve();
    ws.onerror = () => reject(new Error("ws connect failed"));
    ws.onmessage = (ev) => {
      let m; try { m = JSON.parse(ev.data); } catch { return; }
      if (m.id !== undefined && pending.has(m.id)) {
        const h = pending.get(m.id); pending.delete(m.id);
        if (m.error) h.reject(new Error(JSON.stringify(m.error))); else h.resolve(m.result);
      }
    };
  });
}
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId; pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evalJS(expr) {
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result && r.result.value;
}
async function keyDigit(d) {
  const code = 48 + parseInt(d, 10);
  await send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: d, code: "Digit" + d, text: d, windowsVirtualKeyCode: code, nativeVirtualKeyCode: code });
  await send("Input.dispatchKeyEvent", { type: "char", key: d, code: "Digit" + d, text: d, windowsVirtualKeyCode: code, nativeVirtualKeyCode: code });
  await send("Input.dispatchKeyEvent", { type: "keyUp", key: d, code: "Digit" + d, windowsVirtualKeyCode: code, nativeVirtualKeyCode: code });
}
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
  const target = (list.filter((t) => t.type === "page")[0]) || null;
  if (!target) throw new Error("no page target");
  await connect(target.webSocketDebuggerUrl);
  await send("Runtime.enable");

  const diag = await evalJS(`(function(){
    const btns = Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent !== null);
    const b = btns.find(x => /^login/i.test((x.textContent||'').trim())) || btns[btns.length-1];
    const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled && (x.maxLength === 1 || x.type === 'number'));
    return {
      btnDisabled: b ? !!b.disabled : null,
      btnHtml: b ? b.outerHTML.slice(0, 260) : null,
      boxes: vis.map(x => ({v: x.value, r: (()=>{const rc = x.getBoundingClientRect(); return [Math.round(rc.x+rc.width/2), Math.round(rc.y+rc.height/2)];})()}))
    };
  })()`);
  log("diag:", JSON.stringify(diag));

  const boxes = (diag.boxes || []);
  const digits = "8751".split("");
  if (boxes.length >= 4) {
    for (let i = 0; i < 4; i++) {
      await evalJS(`(function(){const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled && (x.maxLength === 1 || x.type === 'number')); const t = vis[${i}]; if (t) t.focus(); return !!t;})()`);
      // clear then type
      await send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Backspace", code: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 8 });
      await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Backspace", code: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 8 });
      await keyDigit(digits[i]);
      await sleep(250);
    }
  }
  await sleep(800);
  const vals = await evalJS(`Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && (x.maxLength === 1 || x.type === 'number')).map(x => x.value)`);
  log("values now:", JSON.stringify(vals));

  // click login button with trusted mouse events
  const rect = await evalJS(`(function(){
    const btns = Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent !== null);
    const b = btns.find(x => /^login/i.test((x.textContent||'').trim())) || btns[btns.length-1];
    if (!b) return null;
    const rc = b.getBoundingClientRect();
    return {x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), disabled: !!b.disabled, label: (b.textContent||'').trim()};
  })()`);
  log("login rect:", JSON.stringify(rect));
  if (rect) {
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: rect.x, y: rect.y });
    await send("Input.dispatchMouseEvent", { type: "mousePressed", x: rect.x, y: rect.y, button: "left", clickCount: 1 });
    await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: rect.x, y: rect.y, button: "left", clickCount: 1 });
    log("trusted click sent at", rect.x, rect.y, "disabled:", rect.disabled);
  }
  await sleep(5000);
  const after = await evalJS(`({loc: location.href, body: (document.body ? document.body.innerText.slice(0, 320) : '')})`);
  log("after:", JSON.stringify(after));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
