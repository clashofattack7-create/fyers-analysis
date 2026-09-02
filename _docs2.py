
import requests, re, html
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"}
t = requests.get("https://docs.rs/fyers-rs/latest/src/fyers_rs/models/auth.rs.html", headers=ua, timeout=25).text
plain = html.unescape(re.sub(r"<[^>]+>", "", t))
for key in ["appIdHash", "sha256", "generate_token", "refresh", "AUTH", "BASE_URL", "authcode", "validate"]:
    idx = 0
    while True:
        i = plain.find(key, idx)
        if i == -1: break
        print("###", key, "@", i)
        print(plain[max(0,i-300):i+500].replace("\r",""))
        print("----")
        idx = i + 1
        if idx > len(plain): break
