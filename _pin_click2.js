#!/usr/bin/env node
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[click2]", ...a); }
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
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
  const target = (list.filter((t) => t.type === "page")[0]) || null;
  if (!target) throw new Error("no page target");
  await connect(target.webSocketDebuggerUrl);
  await send("Runtime.enable");

  const probe = await evalJS(`(function(){
    const all = Array.from(document.querySelectorAll('*'));
    const hits = all.filter(e => e.offsetParent !== null && (e.textContent||'').toLowerCase().includes('login'));
    return hits.slice(0, 12).map(e => ({
      tag: e.tagName, cls: (e.className||'').toString().slice(0,50),
      txt: (e.textContent||'').replace(/\s+/g,' ').trim().slice(0,40),
      len: (e.textContent||'').length
    }));
  })()`);
  log("login-text elements:", JSON.stringify(probe, null, 0));

  const clicked = await evalJS(`(function(){
    const all = Array.from(document.querySelectorAll('*'));
    const norm = e => (e.textContent||'').replace(/\s+/g,'').toLowerCase();
    const cands = all.filter(e => e.offsetParent !== null && norm(e) === 'login');
    cands.sort((a,b) => (a.textContent||'').length - (b.textContent||'').length);
    const t = cands[0];
    if (!t) return {ok:false, why:'none after normalize'};
    (t.closest('button') || t).dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
    return {ok:true, tag:t.tagName, cls:(t.className||'').toString().slice(0,60)};
  })()`);
  log("normalized click:", JSON.stringify(clicked));

  if (!clicked.ok) {
    // trusted Enter via CDP on the last PIN box
    const box = await evalJS(`(function(){
      const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled && (x.maxLength===1||x.type==='number'));
      const t = vis[vis.length-1]; if (!t) return false; t.focus(); return true;
    })()`);
    if (box) {
      await send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
      await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
      log("trusted Enter sent");
    }
  }

  await sleep(4500);
  const after = await evalJS(`({loc: location.href, body: (document.body ? document.body.innerText.slice(0, 300) : '')})`);
  log("after:", JSON.stringify(after));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
