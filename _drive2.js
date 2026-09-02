#!/usr/bin/env node
// _drive2.js - clean client-ID step: radio -> fy_client_id -> clientIdSubmit
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[d2]", ...a); }
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
async function snap() {
  return await evalJS(`(function(){
    const visible = id => { const e = document.getElementById(id); if (!e) return null; const rc = e.getBoundingClientRect(); const st = e.style ? e.style.display : ''; return { dis: st, vis: rc.width > 0 && rc.height > 0, v: ("value" in e) ? e.value : null, txt: (e.innerText||'').replace(/\s+/g,' ').trim().slice(0,30) }; };
    return {
      body: (document.body ? document.body.innerText.split(String.fromCharCode(10)).join(' | ').slice(0, 240) : ''),
      clientId: visible('fy_client_id'),
      clientIdSubmit: visible('clientIdSubmit'),
      mobileSubmit: visible('mobileNumberSubmit'),
      confirmOtp: visible('confirmOtpSubmit'),
      verifyPin: visible('verifyPinSubmit'),
      radioCid: (function(){ const r = document.getElementById('clientId_rb'); return r ? { checked: r.checked, vis: !!r.offsetParent } : null; })()
    };
  })()`);
}
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
  const target = (list.filter((t) => t.type === "page")[0]) || null;
  if (!target) throw new Error("no page target");
  await connect(target.webSocketDebuggerUrl);
  await send("Runtime.enable");

  let s = await snap();
  log("before:", JSON.stringify(s));

  // 1) select Client ID tab natively (radio click dispatches change -> jQuery)
  const radioClicked = await evalJS(`(function(){ const r = document.getElementById('clientId_rb'); if (!r) return false; r.click(); return true; })()`);
  log("radio clicked:", radioClicked);
  await sleep(800);

  // 2) type client id with trusted keys into #fy_client_id
  const filled = await evalJS(`(function(){
    const t = document.getElementById('fy_client_id');
    const cs = getComputedStyle(t);
    if (!t || cs.display === 'none') return { ok: false, why: 'hidden' };
    t.focus();
    return { ok: document.activeElement === t };
  })()`);
  log("input state:", JSON.stringify(filled));
  if (filled && filled.ok) {
    await key("rawKeyDown", { key: "Control", code: "ControlLeft", windowsVirtualKeyCode: 17 });
    await key("rawKeyDown", { key: "a", code: "KeyA", windowsVirtualKeyCode: 65 });
    await key("keyUp", { key: "a", code: "KeyA", windowsVirtualKeyCode: 65 });
    await key("keyUp", { key: "Control", code: "ControlLeft", windowsVirtualKeyCode: 17 });
    await key("rawKeyDown", { key: "Backspace", code: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 8 });
    await key("keyUp", { key: "Backspace", code: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 8 });
    await typeString("YA38754");
    await sleep(400);
  }
  s = await snap();
  log("after typing:", JSON.stringify(s));

  // 3) click #clientIdSubmit natively
  const sub = await evalJS(`(function(){ const b = document.getElementById('clientIdSubmit'); if (!b) return false; b.click(); return true; })()`);
  log("clientIdSubmit clicked:", sub);
  await sleep(6500);
  s = await snap();
  log("after submit:", JSON.stringify(s));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
