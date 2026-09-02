
import requests
APP = "HU97KUI414-200"
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml"}
url = "https://api-t1.fyers.in/api/v3/generate-authcode"
for r in ["https://trade.fyers.in/api-login/redirect-uri/index.html", "https://127.0.0.1:5000/"]:
    resp = requests.get(url, params={"client_id": APP, "redirect_uri": r, "response_type": "code", "state": "s1"}, headers=ua, timeout=20, allow_redirects=False)
    open("resp_%s.html" % ("trade" if "trade" in r else "local"), "w", encoding="utf-8").write(resp.text)
    print(r, resp.status_code, "len", len(resp.text), "ct", resp.headers.get("Content-Type"), "server", resp.headers.get("Server"))
