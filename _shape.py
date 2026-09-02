
import json, requests
tok = json.load(open(r"D:\dsh\DSH\option-chain-live\.fyers_credentials.json", encoding="utf-8"))["access_token"]
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
r = requests.get("https://api-t1.fyers.in/data/options-chain-v3",
                 params={"symbol": "NSE:NIFTY50-INDEX", "strikecount": 5, "timestamp": "", "greeks": "1"},
                 headers={"Authorization": tok, "User-Agent": ua}, timeout=25)
j = r.json()
d = j["data"]
print("top keys:", list(d.keys()))
oc = d.get("optionsChain")
print("optionsChain type:", type(oc).__name__, "len:", len(oc) if oc else 0)
if oc:
    print("row0 keys:", list(oc[0].keys()))
    print("row0 sample:", json.dumps(oc[0], default=str)[:700])
