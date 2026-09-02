
import requests, re, html, json
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
def get(url):
    r = requests.get(url, headers=ua, timeout=25)
    return r.status_code, r.text
# 1) fyers-rs auth models source
st, t = get("https://docs.rs/fyers-rs/latest/src/fyers_rs/models/auth.rs.html")
txt = html.unescape(re.sub(r"<[^>]+>", "", t)).replace("\n", "\n")
print("== auth.rs (status", st, ") ==")
print(txt[:2600])
# 2) look for api module list
st2, t2 = get("https://docs.rs/fyers-rs/latest/fyers_rs/")
links = sorted(set(re.findall(r'href="([^"]*.html)"', t2)))
print("== api pages ==")
for l in links[:60]:
    print(l)
