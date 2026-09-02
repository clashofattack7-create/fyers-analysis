
import re, glob, os
pat = re.compile(rb"(?:YAd{4,8}|YA[A-Z0-9]{4,12})")
seen = set()
for root, dirs, files in os.walk(r"D:\dsh\DSH\.fyers-edge"):
    for f in files:
        p = os.path.join(root, f)
        try:
            data = open(p, "rb").read()
        except Exception:
            continue
        for m in pat.finditer(data):
            s = m.group().decode("ascii", "ignore")
            if s not in seen:
                seen.add(s)
                print(p.split("\\")[-1], s)
