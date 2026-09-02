#!/usr/bin/env node
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
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
  if (!target) { console.log("no page"); process.exit(1); }
  await connect(target.webSocketDebuggerUrl);
  await send("Runtime.enable");
  const s = await evalJS(`(function(){
    const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled);
    const btn = document.querySelector('#verifyPinSubmit');
    return {
      loc: location.href.slice(0, 90),
      body: (document.body ? document.body.innerText.replace(/\n+/g,' | ').slice(0, 260) : ''),
      inputs: vis.map(x => ({t: x.type, max: x.maxLength, v: (x.value||'').slice(0,8), id: x.id || '', ph: (x.placeholder||'').slice(0,20)})),
      pinBtn: btn ? {disabled: !!btn.disabled, text: (btn.textContent||'').trim().slice(0,20)} : null
    };
  })()`);
  console.log(JSON.stringify(s));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
