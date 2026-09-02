#!/usr/bin/env node
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[form]", ...a); }
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
  const d = await evalJS(`(function(){
    const form = document.querySelector('.login-form') || document.querySelector('form') || document.body;
    const allInputs = Array.from(document.querySelectorAll('input')).map(x => ({
      id: x.id||'', name: x.name||'', type: x.type, ph: x.placeholder||'',
      vis: x.offsetParent !== null, chk: x.checked
    }));
    const btns = Array.from(document.querySelectorAll('button,input[type=submit]')).map(b => ({
      id: b.id||'', txt: (b.textContent||b.value||'').replace(/\s+/g,' ').trim().slice(0,20), vis: b.offsetParent !== null, dis: !!b.disabled
    }));
    const secs = Array.from(document.querySelectorAll('section, .tab-pane, [class*=panel], [class*=form]')).filter(e => e.children.length > 0 && (e.id || (e.className||'').toString())).slice(0,10).map(e => ({
      tag: e.tagName, id: e.id||'', cls: (e.className||'').toString().slice(0,60), vis: e.offsetParent !== null,
      txt: (e.innerText||'').replace(/\s+/g,' ').trim().slice(0,50)
    }));
    return { inputs: allInputs, btns: btns, secs: secs, formHtml: form.outerHTML.slice(0, 4000) };
  })()`);
  console.log(JSON.stringify(d, null, 1));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
