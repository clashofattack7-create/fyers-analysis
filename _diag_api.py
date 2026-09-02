
import json, os, requests

tok = json.load(open(r"D:\dsh\DSH\option-chain-live\.fyers_credentials.json", encoding="utf-8"))
at = tok["access_token"]
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

def probe(label, method, url, headers=None, body=None):
    try:
        r = requests.request(method, url, headers=headers or {}, json=body, timeout=25)
        print(label, "->", r.status_code, "| cf:", r.headers.get("cf-ray", "")[:30], "| body:", r.text[:200].replace("\n"," "))
    except Exception as e:
        print(label, "ERR", str(e)[:150])

body = {"symbol": "NSE:NIFTY50-INDEX", "strikecount": 3, "timestamp": "", "greeks": "1"}

probe("A no-auth chain ", "POST", "https://api-t1.fyers.in/data/options-chain-v3",
      {"Content-Type": "application/json", "User-Agent": ua}, body)
probe("B auth chain     ", "POST", "https://api-t1.fyers.in/data/options-chain-v3",
      {"Content-Type": "application/json", "User-Agent": ua, "Authorization": at}, body)
probe("C auth+appid     ", "POST", "https://api-t1.fyers.in/data/options-chain-v3",
      {"Content-Type": "application/json", "User-Agent": ua, "Authorization": "Bearer " + at}, body)
probe("D auth bearer    ", "POST", "https://api-t1.fyers.in/data/options-chain-v3",
      {"Content-Type": "application/json", "User-Agent": ua, "Authorization": "Bearer " + at}, body)
probe("E profile GET    ", "GET", "https://api-t1.fyers.in/api/v3/profile",
      {"User-Agent": ua, "Authorization": at})
probe("F quotes POST    ", "POST", "https://api-t1.fyers.in/api/v3/quotes",
      {"Content-Type": "application/json", "User-Agent": ua, "Authorization": at},
      {"symbols": "NSE:NIFTY50-INDEX"})
