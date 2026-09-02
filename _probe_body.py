
import requests
APP = "HU97KUI414-200"
URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
r = requests.get("https://api-t1.fyers.in/api/v3/generate-authcode",
                 params={"client_id": APP, "redirect_uri": URI, "response_type": "code", "state": "probe"},
                 headers=ua, timeout=20, allow_redirects=False)
print("status:", r.status_code, "ct:", r.headers.get("Content-Type"), "server:", r.headers.get("Server"), "cf:", r.headers.get("cf-ray"))
open("probe_body.html", "w", encoding="utf-8").write(r.text)
print("len:", len(r.text))
print("head:", r.text[:600])
print("tail:", r.text[-400:])
