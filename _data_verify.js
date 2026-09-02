#!/usr/bin/env node
// _data_verify.js - spawn Edge, same-origin fetch options-chain-v3
"use strict";
const { spawn } = require("child_process");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PROFILE = "D:\\dsh\\DSH\\.fyers-edge";
const PORT = 9345;
const TOKEN = process.env.FYERS_AT || "";
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[v]", ...a); }
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
async function waitFor(fn, timeoutMs, pollMs = 500) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    try { const v = await fn(); if (v) return v; } catch {}
    await sleep(pollMs);
  }
  throw new Error("timeout");
}
(async () => {
  spawn(EDGE, ["--user-data-dir=" + PROFILE, "--remote-debugging-port=" + PORT, "--no-first-run", "--no-default-browser-check", "about:blank"], { detached: false, stdio: "ignore" });
  await waitFor(async () => { try { const r = await fetch("http://127.0.0.1:" + PORT + "/json/version"); return r.ok; } catch { return false; } }, 30000, 500);
  const list = await (await fetch("http://127.0.0.1:" + PORT + "/json")).json();
  const target = list.filter((t) => t.type === "page")[0];
  await connect(target.webSocketDebuggerUrl);
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Page.navigate", { url: "https://api-t1.fyers.in/api/v3/profile" });
  await sleep(7000);
  log("origin:", await evalJS("location.href"));
  const r = await evalJS(`fetch('https://api-t1.fyers.in/data/options-chain-v3', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'Authorization': '${TOKEN}'},
    body: JSON.stringify({symbol: 'NSE:NIFTY50-INDEX', strikecount: 3, timestamp: '', greeks: '1'})
  }).then(resp => resp.text().then(t => ({status: resp.status, t: t.slice(0, 500)}))).catch(e => ({err: String(e)}))`);
  log("result:", JSON.stringify(r));
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
