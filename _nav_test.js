#!/usr/bin/env node
// _nav_test.js - spawn Edge on the fyers profile, try several app-id forms
"use strict";
const { spawn } = require("child_process");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PROFILE = "D:\\dsh\\DSH\\.fyers-edge";
const PORT = 9344;
let ws = null; let msgId = 0; const pending = new Map();
function log(...a) { console.log("[nav]", ...a); }
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
  return null;
}
(async () => {
  spawn(EDGE, ["--user-data-dir=" + PROFILE, "--remote-debugging-port=" + PORT, "--no-first-run", "--no-default-browser-check", "--window-size=1360,900", "about:blank"], { detached: false, stdio: "ignore" });
  await waitFor(async () => { try { const r = await fetch("http://127.0.0.1:" + PORT + "/json/version"); return r.ok; } catch { return false; } }, 30000, 500);
  const list = await (await fetch("http://127.0.0.1:" + PORT + "/json")).json();
  const target = list.filter((t) => t.type === "page")[0];
  await connect(target.webSocketDebuggerUrl);
  await send("Page.enable");
  await send("Runtime.enable");

  const candidates = ["HU97KUI4I4-200"];
  const uri = encodeURIComponent("https://trade.fyers.in/api-login/redirect-uri/index.html");
  for (const app of candidates) {
    const url = "https://api-t1.fyers.in/api/v3/generate-authcode?client_id=" + encodeURIComponent(app) + "&redirect_uri=" + uri + "&response_type=code&state=t" + Date.now();
    console.log("=== trying app:", app);
    await send("Page.navigate", { url });
    await sleep(9000);
    const loc = await evalJS("location.href").catch(() => "?");
    const body = await evalJS("document.body ? document.body.innerText.split(String.fromCharCode(10)).join(' | ').slice(0, 200) : ''").catch(() => "");
    console.log("loc:", loc);
    console.log("body:", body);
    if (/login to fyers/i.test(body)) { console.log(">>> LOGIN PAGE REACHED with", app); break; }
  }
  process.exit(0);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
