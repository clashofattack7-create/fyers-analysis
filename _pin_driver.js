#!/usr/bin/env node
// _pin_driver.js - inject the Fyers 4-digit PIN into the live .fyers-edge browser
"use strict";

const PORT = 9333;
let ws = null;
let msgId = 0;
const pending = new Map();

function log(...a) { console.log("[pin]", ...a); }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

function connect(url) {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(url);
    ws.onopen = () => resolve();
    ws.onerror = () => reject(new Error("ws connect failed"));
    ws.onmessage = (ev) => {
      let m;
      try { m = JSON.parse(ev.data); } catch { return; }
      if (m.id !== undefined && pending.has(m.id)) {
        const h = pending.get(m.id);
        pending.delete(m.id);
        if (m.error) h.reject(new Error(JSON.stringify(m.error)));
        else h.resolve(m.result);
      }
    };
  });
}

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending.set(id, { resolve, reject });
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
  log("target:", target.url.slice(0, 120));
  await connect(target.webSocketDebuggerUrl);
  await send("Runtime.enable");

  const info = await evalJS(`(function(){
    const vis = Array.from(document.querySelectorAll('input')).filter(i => i.offsetParent !== null && !i.readOnly && !i.disabled);
    return vis.map(i => ({type: i.type, max: i.maxLength, val_len: (i.value||'').length, ph: i.placeholder||'', name: i.name||''}));
  })()`);
  log("visible inputs:", JSON.stringify(info));

  const digits = "8751".split("");
  let filled = 0;
  const boxes = info.filter(i => i.max === 1 || i.type === "number" || i.type === "password");

  if (boxes.length >= 4 && boxes.length <= 6) {
    for (let i = 0; i < Math.min(digits.length, boxes.length); i++) {
      const ok = await evalJS(`(function(){
        const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled);
        const cands = vis.filter(x => x.maxLength === 1 || x.type === 'number' || x.type === 'password');
        const t = cands[${i}];
        if (!t) return false;
        t.focus();
        const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        s.call(t, '${digits[i]}');
        t.dispatchEvent(new Event('input', {bubbles:true}));
        t.dispatchEvent(new Event('change', {bubbles:true}));
        return true;
      })()`);
      if (ok) filled++;
      await sleep(120);
    }
  } else {
    const single = info.find(i => (i.max === 4 || i.max === -1) && i.val_len === 0) || info.find(i => i.type === "password");
    if (single) {
      const idx = info.indexOf(single);
      const ok = await evalJS(`(function(){
        const vis = Array.from(document.querySelectorAll('input')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled);
        const t = vis[${idx}];
        if (!t) return false;
        t.focus();
        const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        s.call(t, '8751');
        t.dispatchEvent(new Event('input', {bubbles:true}));
        t.dispatchEvent(new Event('change', {bubbles:true}));
        return true;
      })()`);
      filled = ok ? 4 : 0;
    }
  }
  log("filled boxes:", filled);

  await sleep(600);
  const clicked = await evalJS(`(function(){
    const els = Array.from(document.querySelectorAll('button, input[type=submit]'));
    const b = els.find(e => /^login\$/i.test((e.textContent||e.value||'').trim()));
    if (!b) return false;
    b.click();
    return true;
  })()`);
  log("login clicked:", clicked);

  await sleep(3500);
  const after = await evalJS(`({loc: location.href, body: (document.body ? document.body.innerText.slice(0, 300) : '')})`);
  log("after:", JSON.stringify(after));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
