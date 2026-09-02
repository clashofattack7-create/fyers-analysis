
import requests, time
APP = "HU97KUI414-200"
URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
url = "https://api-t1.fyers.in/api/v3/generate-authcode"
for i in range(3):
    try:
        r = requests.get(url, params={"client_id": APP, "redirect_uri": URI, "response_type": "code", "state": "probe%d" % i},
                         headers=ua, timeout=20, allow_redirects=False)
        print("try%d:" % i, r.status_code, "| loc:", (r.headers.get("Location") or "")[:160])
        print("   body:", r.text[:180].replace("\n", " "))
    except Exception as e:
        print("try%d ERR" % i, e)
    time.sleep(3)
