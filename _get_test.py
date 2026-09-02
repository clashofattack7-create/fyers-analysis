
import json, requests
tok = json.load(open(r"D:\dsh\DSH\option-chain-live\.fyers_credentials.json", encoding="utf-8"))["access_token"]
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
params = {"symbol": "NSE:NIFTY50-INDEX", "strikecount": 3, "timestamp": "", "greeks": "1"}
r = requests.get("https://api-t1.fyers.in/data/options-chain-v3", params=params,
                 headers={"Authorization": tok, "User-Agent": ua, "Accept": "application/json"}, timeout=25)
print("status:", r.status_code, "cf:", r.headers.get("cf-ray", "")[:24])
t = r.text
print("body head:", t[:300].replace("\n", " "))
try:
    j = r.json()
    print("json code:", j.get("code"), "| s:", j.get("s"), "| data keys:", list(j.get("data", {}).keys())[:12])
except Exception as e:
    print("json err:", e)
