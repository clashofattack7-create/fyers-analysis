#!/usr/bin/env node
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[click3]", ...a); }
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

  // 1) re-fill PIN boxes if any digit got lost
  const fill = await evalJS(`(function(){
    const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled && (x.maxLength === 1 || x.type === 'number'));
    const dig = '8751'.split('');
    let n = 0;
    for (let i = 0; i < Math.min(dig.length, vis.length); i++) {
      const t = vis[i];
      const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      s.call(t, dig[i]);
      t.dispatchEvent(new Event('input', {bubbles:true}));
      t.dispatchEvent(new Event('change', {bubbles:true}));
      n++;
    }
    return {boxes: vis.length, filled: n, values: vis.map(v => v.value)};
  })()`);
  log("pin state:", JSON.stringify(fill));

  // 2) click the actual login button (any button whose text starts with login, or btn-classed button in the form)
  const clicked = await evalJS(`(function(){
    const btns = Array.from(document.querySelectorAll('button'));
    const vis = btns.filter(b => b.offsetParent !== null);
    const b = vis.find(x => /^login/i.test((x.textContent||'').trim())) || vis.find(x => /btn/.test(x.className||''));
    if (!b) return {ok:false, total: vis.length, labels: vis.slice(0,5).map(x => (x.textContent||'').trim().slice(0,20))};
    const label = (b.textContent||'').trim();
    b.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
    b.click();
    return {ok:true, tag:b.tagName, label:label, cls:(b.className||'').slice(0,70)};
  })()`);
  log("clicked:", JSON.stringify(clicked));

  await sleep(5000);
  const after = await evalJS(`({loc: location.href, body: (document.body ? document.body.innerText.slice(0, 320) : '')})`);
  log("after:", JSON.stringify(after));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
