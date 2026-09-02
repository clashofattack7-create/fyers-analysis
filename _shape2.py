
import json, requests
tok = json.load(open(r"D:\dsh\DSH\option-chain-live\.fyers_credentials.json", encoding="utf-8"))["access_token"]
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
def get(ts="", **kw):
    p = {"symbol": "NSE:NIFTY50-INDEX", "strikecount": 6, "timestamp": ts, "greeks": "1"}
    p.update(kw)
    r = requests.get("https://api-t1.fyers.in/data/options-chain-v3", params=p,
                     headers={"Authorization": tok, "User-Agent": ua}, timeout=25)
    return r.status_code, r.json() if r.headers.get("content-type","").startswith("application/json") else r.text[:120]

st, j = get()
oc = j["data"]["optionsChain"]
rows = [r for r in oc if r.get("option_type")]
print("ts-empty: option rows:", len(rows), "keys:", list(rows[0].keys()) if rows else [])
if rows:
    print("CE row:", json.dumps(next((r for r in rows if r["option_type"]=="CE"), rows[0]), default=str)[:400])

# with an expiry timestamp
st2, j2 = get(ts="1788862200")
oc2 = j2["data"]["optionsChain"]
rows2 = [r for r in oc2 if r.get("option_type")]
print("ts-exp: status", st2, "rows:", len(rows2), "keys:", list(rows2[0].keys()) if rows2 else [])
if rows2:
    ce = next((r for r in rows2 if r["option_type"]=="CE"), rows2[0])
    print("CE row:", json.dumps(ce, default=str)[:500])
print("top data keys (exp):", list(j2["data"].keys()))
