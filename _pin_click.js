#!/usr/bin/env node
"use strict";
const PORT = 9333;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[click]", ...a); }
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

  // 1) click any visible element whose own trimmed text is exactly "Login" (deepest wins)
  const clicked = await evalJS(`(function(){
    const all = Array.from(document.querySelectorAll('button, a, div, span, p, input[type=submit]'));
    const cands = all.filter(e => e.offsetParent !== null && (e.textContent||'').trim() === 'Login');
    cands.sort((a,b) => (a.textContent||'').length - (b.textContent||'').length);
    const t = cands[0];
    if (!t) return {ok:false, why:'no candidate'};
    const target = t.closest('button') || t.parentElement && /button/i.test(t.parentElement.className||'') ? (t.closest('button') || t) : t;
    target.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
    return {ok:true, tag:t.tagName, cls:(t.className||'').toString().slice(0,60)};
  })()`);
  log("clicked:", JSON.stringify(clicked));

  // 2) if still nothing, try Enter on the last PIN box
  if (!clicked.ok) {
    const pressed = await evalJS(`(function(){
      const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled && (x.maxLength===1||x.type==='number'));
      const t = vis[vis.length-1];
      if (!t) return false;
      t.focus();
      ['keydown','keypress','keyup'].forEach(k => t.dispatchEvent(new KeyboardEvent(k, {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true})));
      return true;
    })()`);
    log("enter pressed:", pressed);
  }

  await sleep(4000);
  const after = await evalJS(`({loc: location.href, body: (document.body ? document.body.innerText.slice(0, 260) : '')})`);
  log("after:", JSON.stringify(after));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
