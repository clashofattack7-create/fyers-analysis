
import json, requests
tok = json.load(open(r"D:\dsh\DSH\option-chain-live\.fyers_credentials.json", encoding="utf-8"))["access_token"]
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
for sym in ["NSE:NIFTYBANK-INDEX", "NSE:BANKNIFTY-IND", "NSE:BANKNIFTY-INDEX-", "NSE:BANKNIFTY-INDEX-EQ", "MCX:BANKNIFTY-INDEX"]:
    r = requests.get("https://api-t1.fyers.in/data/options-chain-v3",
                     params={"symbol": sym, "strikecount": 2, "timestamp": "", "greeks": "1"},
                     headers={"Authorization": tok, "User-Agent": ua}, timeout=25)
    try:
        j = r.json()
        print(sym, "->", j.get("code"), "|", (j.get("message") or "")[:45], "| rows:", len((j.get("data") or {}).get("optionsChain") or []))
    except Exception:
        print(sym, "-> non-json", r.status_code)
