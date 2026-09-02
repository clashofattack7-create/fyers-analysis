
import json, requests
tok = json.load(open(r"D:\dsh\DSH\option-chain-live\.fyers_credentials.json", encoding="utf-8"))["access_token"]
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
for sym in ["NSE:BANKNIFTY-INDEX", "NSE:BANKNIFTY50-INDEX", "NSE:BANKNIFTY-INDEX-FUT", "NSE:BANKNIFTY25-SEP-FUT"]:
    r = requests.get("https://api-t1.fyers.in/data/options-chain-v3",
                     params={"symbol": sym, "strikecount": 2, "timestamp": "", "greeks": "1"},
                     headers={"Authorization": tok, "User-Agent": ua}, timeout=25)
    try:
        j = r.json()
        msg = j.get("message", "")[:60]
        rows = len((j.get("data") or {}).get("optionsChain") or [])
        print(sym, "->", r.status_code, "code", j.get("code"), "| msg:", msg, "| rows:", rows)
    except Exception as e:
        print(sym, "->", r.status_code, "non-json:", str(e)[:60])
