
import requests, re, html
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"}
def plain(url):
    t = requests.get(url, headers=ua, timeout=25).text
    return html.unescape(re.sub(r"<[^>]+>", "", t))
p = plain("https://docs.rs/fyers-rs/latest/fyers_rs/rest/market_data/index.html")
for key in ["option", "chain", "opt_chain"]:
    i = p.lower().find(key)
    if i >= 0:
        print("###", key)
        print(p[max(0,i-400):i+900])
        print("-----")
# pypi description
try:
    j = requests.get("https://pypi.org/pypi/fyers-apiv3/json", headers=ua, timeout=25).json()
    desc = j["info"]["description"] or ""
    print("### pypi fyers-apiv3 desc len", len(desc))
    for key in ["optionchain", "option-chain", "strikecount"]:
        i = desc.lower().find(key)
        if i >= 0:
            print(desc[max(0,i-300):i+700])
            print("-----")
except Exception as e:
    print("pypi err", e)
