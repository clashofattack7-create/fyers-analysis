
import re, os, glob
src = r"D:\dsh\DSH\.fyers-edge\Default\Local Storage\leveldb"
pat = re.compile(rb"[\x20-\x7e]{6,}")
hits = {}
for f in glob.glob(src + "\\*"):
    if not (f.endswith(".ldb") or f.endswith(".log")): continue
    data = open(f, "rb").read()
    for m in pat.finditer(data):
        s = m.group().decode("ascii", "ignore")
        low = s.lower()
        if any(k in low for k in ["fyers", "token", "client_id", "clid", "pan", "email", "@", "hu97", "secret"]):
            hits.setdefault(os.path.basename(f), set()).add(s)
out = []
for f, vals in hits.items():
    out.append("=== " + f + " (" + str(len(vals)) + ") ===")
    for v in sorted(vals)[:40]:
        out.append(v[:200])
print("\n".join(out))
