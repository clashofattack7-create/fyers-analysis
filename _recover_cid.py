import sqlite3, os, re, glob

PROFILE = r"D:\dsh\DSH\.fyers-edge"

# 1) chromium Login Data / Web Data (autofill)
for db in [os.path.join(PROFILE, "Default", "Login Data"),
           os.path.join(PROFILE, "Default", "Web Data")]:
    if not os.path.exists(db):
        print("missing:", db)
        continue
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print(db, "tables:", [r[0] for r in cur.fetchall()][:25])
        try:
            cur.execute("SELECT username_value, origin_url FROM logins")
            for row in cur.fetchall():
                print("login:", row)
        except Exception as e:
            print("  logins err:", e)
        try:
            cur.execute("SELECT name, value FROM autofill")
            for row in cur.fetchall():
                print("autofill:", row)
        except Exception as e:
            print("  autofill err:", e)
        con.close()
    except Exception as e:
        print("db err:", db, e)

# 2) byte scan for YAxxxx patterns in profile files
pat = re.compile(rb"\bYA[A-Z0-9]{4,10}\b")
seen = {}
for root, dirs, files in os.walk(PROFILE):
    dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("Cache", "Code Cache", "GPUCache")]
    for f in files:
        if not (f.endswith(".ldb") or f.endswith(".log") or f.endswith(".json") or f.endswith("Preferences")):
            continue
        p = os.path.join(root, f)
        try:
            data = open(p, "rb").read()
        except Exception:
            continue
        for m in pat.finditer(data):
            s = m.group().decode("ascii", "ignore")
            seen.setdefault(s, []).append((p, m.start()))
for s, locs in seen.items():
    print("HIT", s, "count", len(locs), "example", locs[0])
