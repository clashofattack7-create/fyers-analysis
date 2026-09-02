#!/usr/bin/env node
// _drive_login.js - trusted-event driver: client ID -> Continue -> stop at OTP/PIN screen
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[drive]", ...a); }
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
async function key(type, params) { await send("Input.dispatchKeyEvent", { type, ...params }); }
async function typeString(str, interval = 60) {
  for (const ch of str) {
    const code = ch.charCodeAt(0);
    await key("rawKeyDown", { key: ch, code: "Key" + ch.toUpperCase(), text: ch, windowsVirtualKeyCode: code, nativeVirtualKeyCode: code });
    await key("char", { key: ch, code: "Key" + ch.toUpperCase(), text: ch, windowsVirtualKeyCode: code, nativeVirtualKeyCode: code });
    await key("keyUp", { key: ch, code: "Key" + ch.toUpperCase(), windowsVirtualKeyCode: code, nativeVirtualKeyCode: code });
    await sleep(interval);
  }
}
async function trustedClickAt(x, y) {
  await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y });
  await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
  await send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
}
async function state() {
  const s = await evalJS(`(function(){
    const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled);
    const btn = Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent !== null);
    const rec = e => { const rc = e.getBoundingClientRect(); return { x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), t: e.tagName }; };
    return {
      body: (document.body ? document.body.innerText.split(String.fromCharCode(10)).join(' | ').slice(0, 300) : ''),
      inputs: vis.map(x => ({ t: x.type, max: x.maxLength, v: (x.value||'').slice(0,8), id: x.id||'', ph: (x.placeholder||'').slice(0,25), rc: rec(x) })),
      radios: Array.from(document.querySelectorAll('input[type=radio]')).map(r => ({ v: r.value, checked: r.checked, rc: rec(r) })),
      buttons: btn.map(b => ({ txt: (b.textContent||'').replace(/\s+/g,' ').trim().slice(0,25), id: b.id||'', dis: !!b.disabled, rc: rec(b) }))
    };
  })()`);
  return s;
}
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
  const target = (list.filter((t) => t.type === "page")[0]) || null;
  if (!target) throw new Error("no page target");
  await connect(target.webSocketDebuggerUrl);
  await send("Runtime.enable");

  const s0 = await state();
  log("state:", JSON.stringify(s0));

  const body = s0.body.toLowerCase();
  if (/enter your 4-digit pin/.test(body)) {
    log("AT PIN SCREEN already");
  } else if (/6-digit otp|confirm otp|enter.{0,6}otp/.test(body)) {
    log("AT OTP SCREEN - needs OTP from user");
  } else {
    const cid = s0.radios.find(r => /client/i.test(r.v));
    if (cid) {
      await trustedClickAt(cid.rc.x, cid.rc.y);
      await sleep(900);
    } else {
      log("no client-id radio found");
    }
    const s1 = await state();
    let input = s1.inputs.find(i => i.ph && /client/i.test(i.ph)) || s1.inputs.find(i => i.t === "text" && i.max !== 1) || s1.inputs.filter(i => i.max !== 1 && i.t !== "number")[0] || null;
    if (!input) { log("no text input to fill; inputs:", JSON.stringify(s1.inputs)); process.exit(1); }
    log("filling input:", JSON.stringify(input));
    const idx = s1.inputs.indexOf(input);
    const focused = await evalJS(`(function(){const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled); const t = vis[${idx}]; if (!t) return false; t.focus(); return document.activeElement === t;})()`);
    log("focus ok:", focused);
    if (focused) {
      await key("rawKeyDown", { key: "Control", code: "ControlLeft", windowsVirtualKeyCode: 17 });
      await key("rawKeyDown", { key: "a", code: "KeyA", windowsVirtualKeyCode: 65 });
      await key("keyUp", { key: "a", code: "KeyA", windowsVirtualKeyCode: 65 });
      await key("keyUp", { key: "Control", code: "ControlLeft", windowsVirtualKeyCode: 17 });
      await key("rawKeyDown", { key: "Backspace", code: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 8 });
      await key("keyUp", { key: "Backspace", code: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 8 });
      await typeString("YA38754");
      await sleep(500);
    }
    const s2 = await state();
    log("after typing id, text input values:", JSON.stringify(s2.inputs.filter(i => i.max !== 1)));
    const cont = s2.buttons.find(b => /^continue/i.test(b.txt)) || s2.buttons.find(b => /login/i.test(b.txt));
    if (cont) {
      log("clicking Continue:", cont.txt, JSON.stringify(cont.rc));
      await trustedClickAt(cont.rc.x, cont.rc.y);
    }
  }
  await sleep(6500);
  const s3 = await state();
  log("final:", JSON.stringify(s3));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
