
import json, requests
tok = json.load(open(r"D:\dsh\DSH\option-chain-live\.fyers_credentials.json", encoding="utf-8"))["access_token"]
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
def t(sym, ts=""):
    r = requests.get("https://api-t1.fyers.in/data/options-chain-v3",
                     params={"symbol": sym, "strikecount": 2, "timestamp": ts, "greeks": "1"},
                     headers={"Authorization": tok, "User-Agent": ua}, timeout=25)
    try:
        j = r.json()
        return r.status_code, j.get("code"), (j.get("message") or "")[:50], len((j.get("data") or {}).get("optionsChain") or [])
    except Exception:
        return r.status_code, "?", r.text[:40], 0
cases = [
    ("NSE:FINNIFTY-INDEX", ""),
    ("NSE:MIDCPNIFTY-INDEX", ""),
    ("NSE:BANKNIFTY-INDEX", "1788862200"),
    ("NSE:BANKNIFTY-INDEX", "1790676600"),
    ("NSE:BANKNIFTY-INDEX", "1788862200,1790676600"),
]
for sym, ts in cases:
    print(sym, "ts=" + (ts or "''"), "->", t(sym, ts))
