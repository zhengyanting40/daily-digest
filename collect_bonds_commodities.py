import json, os, re
from urllib.request import Request, urlopen
from urllib.error import URLError

digest_dir = "/home/hermes_agent/digest"
os.makedirs(digest_dir, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

def fetch_url(url, timeout=12):
    req = Request(url, headers=headers)
    resp = urlopen(req, timeout=timeout)
    return resp.read().decode('utf-8', errors='replace')

def fetch_yf(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=2d&interval=1d"
    resp = fetch_url(url, timeout=10)
    data = json.loads(resp)
    meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
    quotes = data.get("chart", {}).get("result", [{}])[0].get("indicators", {}).get("quote", [{}])[0]
    closes = quotes.get("close", [None])
    prev_close = meta.get("previousClose", None)
    current = closes[-1] if closes and closes[-1] else prev_close
    return current, prev_close

yf_data = {}

# 美债
bonds = {"^IRX": "3月期美债", "^FVX": "5年期美债", "^TNX": "10年期美债", "^TYX": "30年期美债"}
for sym, name in bonds.items():
    try:
        current, prev = fetch_yf(sym)
        if current and prev and prev != 0:
            chg = round((current - prev) / prev * 100, 2)
            key = "bond_" + sym.replace("^", "")
            yf_data[key] = {"name": name, "price": round(current, 2), "change_pct": chg}
            print(f"{name}: {round(current,2)} ({chg:+.2f}%)")
    except Exception as e:
        print(f"{name}: err - {type(e).__name__}")

# 商品
comm = {"GC=F": "黄金", "CL=F": "原油", "SI=F": "白银", "HG=F": "铜"}
for sym, name in comm.items():
    try:
        current, prev = fetch_yf(sym)
        if current and prev and prev != 0:
            chg = round((current - prev) / prev * 100, 2)
            key = "comm_" + sym.replace("=", "")
            yf_data[key] = {"name": name, "price": round(current, 2), "change_pct": chg}
            print(f"{name}: {round(current,2)} ({chg:+.2f}%)")
    except Exception as e:
        print(f"{name}: err - {type(e).__name__}")

# 加密
crypto = {"BTC-USD": "BTC", "ETH-USD": "ETH"}
for sym, name in crypto.items():
    try:
        current, prev = fetch_yf(sym)
        if current and prev and prev != 0:
            chg = round((current - prev) / prev * 100, 2)
            key = "crypto_" + sym.replace("-", "")
            yf_data[key] = {"name": name, "price": round(current, 2), "change_pct": chg}
            print(f"{name}: {round(current,2)} ({chg:+.2f}%)")
    except Exception as e:
        print(f"{name}: err - {type(e).__name__}")

# 国际指数
indices = {"N225": "日经225", "KS11": "KOSPI", "FTSE": "富时100", "STOXX50E": "斯托克50", "AXJO": "ASX 200", "NSEI": "NIFTY 50"}
for sym, name in indices.items():
    try:
        current, prev = fetch_yf("^" + sym)
        if current and prev and prev != 0:
            chg = round((current - prev) / prev * 100, 2)
            key = "index_" + sym
            yf_data[key] = {"name": name, "price": round(current, 2), "change_pct": chg}
            print(f"{name}: {round(current,2)} ({chg:+.2f}%)")
    except Exception as e:
        print(f"{name}: err - {type(e).__name__}")

# DXY
try:
    current, prev = fetch_yf("DX-Y.NYB")
    if current and prev and prev != 0:
        chg = round((current - prev) / prev * 100, 2)
        yf_data["dxy"] = {"name": "美元指数", "price": round(current, 2), "change_pct": chg}
        print(f"DXY: {round(current,2)} ({chg:+.2f}%)")
except Exception as e:
    print(f"DXY: err - {type(e).__name__}")

with open(f"{digest_dir}/yf_data.json", "w") as f:
    json.dump(yf_data, f, ensure_ascii=False, indent=2)

print(f"\nTotal: {len(yf_data)} items")
