
import sqlite3, os, glob
p = r"D:\dsh\DSH\.fyers-edge\Default\Network\Cookies"
if os.path.exists(p):
    try:
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        cur = con.cursor()
        try:
            cur.execute("SELECT name, host_key, length(value) FROM cookies WHERE host_key LIKE '%fyers%'")
            rows = cur.fetchall()
            print("COOKIE ROWS:", rows[:30])
        except Exception as e:
            print("cookie query err:", e)
        con.close()
    except Exception as e:
        print("cookie db err:", e)
else:
    print("no cookies db")
# 3) check other stores
for f in glob.glob(r"D:\dsh\DSH\.fyers-edge\Default\Local Storage\leveldb\*.ldb") + glob.glob(r"D:\dsh\DSH\.fyers-edge\Default\Local Storage\leveldb\*.log"):
    print(f, os.path.getsize(f))
