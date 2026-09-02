
import requests, json
APP = "HU97KUI414-200"
candidates = [
    "https://trade.fyers.in/api-login/redirect-uri/index.html",
    "https://127.0.0.1:5000/",
    "http://127.0.0.1:5000/",
    "https://localhost/",
    "https://localhost:5000/",
    "https://myfyers.in/api-login/redirect-uri/index.html",
    "https://fyers.in/",
    "https://www.fyers.in/",
    "https://login.fyers.in/api-login/redirect-uri/index.html",
]
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
for r in candidates:
    url = "https://api-t1.fyers.in/api/v3/generate-authcode"
    try:
        resp = requests.get(url, params={"client_id": APP, "redirect_uri": r, "response_type": "code", "state": "s1"}, headers=ua, timeout=15, allow_redirects=False)
        loc = resp.headers.get("Location", "")
        body = resp.text[:220].replace("\n", " ")
        print("URI:", r)
        print("  status", resp.status_code, "| loc:", loc[:150])
        print("  body:", body)
    except Exception as e:
        print("URI:", r, "ERR", e)
print("---")
# probe token endpoint
try:
    resp = requests.post("https://api-t1.fyers.in/api/v3/validate-authcode", json={"grant_type": "authorization_code", "appIdHash": "x", "code": "x"}, headers=ua, timeout=15)
    print("validate-authcode:", resp.status_code, resp.text[:260])
except Exception as e:
    print("validate-authcode ERR", e)
