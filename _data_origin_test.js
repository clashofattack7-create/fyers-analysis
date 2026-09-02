#!/usr/bin/env node
// _data_origin_test.js - same-origin POST to /data/options-chain-v3 from api-t1.fyers.in
"use strict";
const PORT = 9344;
const TOKEN = process.env.FYERS_AT || "";
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[data]", ...a); }
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
  if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 300));
  return r.result && r.result.value;
}
(async () => {
  const list = await (await fetch("http://127.0.0.1:" + PORT + "/json")).json();
  const target = (list.filter((t) => t.type === "page")[0]) || null;
  if (!target) throw new Error("no page target on 9344");
  await connect(target.webSocketDebuggerUrl);
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Page.navigate", { url: "https://api-t1.fyers.in/" });
  await sleep(6000);
  const loc = await evalJS("location.href").catch(() => "?");
  log("origin page:", loc);
  const r = await evalJS(`fetch('https://api-t1.fyers.in/data/options-chain-v3', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'Authorization': '${TOKEN}'},
    body: JSON.stringify({symbol: 'NSE:NIFTY50-INDEX', strikecount: 3, timestamp: '', greeks: '1'})
  }).then(resp => resp.text().then(t => ({status: resp.status, t: t.slice(0, 400)}))).catch(e => ({err: String(e)}))`);
  log("result:", JSON.stringify(r));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
