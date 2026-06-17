#!/usr/bin/env python3
"""Get sector data from East Money and Sina alternate endpoints."""
import urllib.request
import json
import re
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
OUTPUT_DIR = "/home/hermes_agent/digest"

def fetch(url, headers=None, timeout=15):
    if headers is None:
        headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

results = {}

# 1. East Money sector ranking API
print("=== East Money Sector Rankings ===")
# East Money industry sector API
url = "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=10&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:90+t:2&fields=f12,f14,f2,f3,f62,f184,f66"
try:
    data = fetch(url)
    print(f"  Raw response (first 500): {data[:500]}")
    if data and data.startswith("{"):
        parsed = json.loads(data)
        items = parsed.get("data", {}).get("diff", [])
        sectors_hy = []
        for item in items[:5]:
            sectors_hy.append({"name": item.get("f14", "N/A"), "change_pct": f"{item.get('f3', 0):+.2f}%"})
            print(f"  {item.get('f14', 'N/A')}: {item.get('f3', 0):+.2f}%")
        results["cn_hy_sectors"] = sectors_hy
except Exception as e:
    print(f"  Error: {e}")

# 2. East Money concept sector API  
print("\n=== East Money Concept Sectors ===")
url = "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=10&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:90+t:3&fields=f12,f14,f2,f3,f62,f184,f66"
try:
    data = fetch(url)
    if data and data.startswith("{"):
        parsed = json.loads(data)
        items = parsed.get("data", {}).get("diff", [])
        sectors_gn = []
        for item in items[:5]:
            sectors_gn.append({"name": item.get("f14", "N/A"), "change_pct": f"{item.get('f3', 0):+.2f}%"})
            print(f"  {item.get('f14', 'N/A')}: {item.get('f3', 0):+.2f}%")
        results["cn_gn_sectors"] = sectors_gn
except Exception as e:
    print(f"  Error: {e}")

# 3. East Money fund flow API
print("\n=== East Money Fund Flow ===")
url = "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=5&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f62&fs=m:90+t:2&fields=f12,f14,f2,f3,f62,f184,f66"
try:
    data = fetch(url)
    if data and data.startswith("{"):
        parsed = json.loads(data)
        items = parsed.get("data", {}).get("diff", [])
        fund_flow = []
        for item in items[:3]:
            inflow = item.get("f62", 0)
            if inflow:
                inflow_yi = inflow / 1e8
            else:
                inflow_yi = 0
            fund_flow.append({"name": item.get("f14", "N/A"), "amount_yi": f"{inflow_yi:.1f}亿"})
            print(f"  {item.get('f14', 'N/A')}: 主力净流入 {inflow_yi:.1f}亿")
        results["cn_fund_flow"] = fund_flow
except Exception as e:
    print(f"  Error: {e}")

# 4. East Money limit up / board stocks
print("\n=== East Money Limit Up ===")
url = "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=15&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6+f:!50&fields=f12,f14,f2,f3,f62,f184,f66,f168"
try:
    data = fetch(url)
    if data and data.startswith("{"):
        parsed = json.loads(data)
        items = parsed.get("data", {}).get("diff", [])
        top_stocks = []
        for item in items[:10]:
            top_stocks.append({
                "name": item.get("f14", "N/A"),
                "code": item.get("f12", ""),
                "change_pct": f"{item.get('f3', 0):+.2f}%",
                "price": item.get("f2", "N/A")
            })
            print(f"  {item.get('f14', 'N/A')}({item.get('f12', '')}): {item.get('f3', 0):+.2f}%")
        results["cn_top_stocks"] = top_stocks
except Exception as e:
    print(f"  Error: {e}")

# 5. HK sectors via Sina alternate
print("\n=== HK Sectors (Sina alt) ===")
url = "https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/hk_jg/index.phtml"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://vip.stock.finance.sina.com.cn/",
    "Cookie": "PHPSESSID=test"
})
try:
    with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
        html = resp.read().decode("gbk", errors="replace")
        print(f"  Response length: {len(html)}")
        print(f"  First 300: {html[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# 6. More news - try Sina finance news
print("\n=== Sina News ===")
url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=10&page=1"
try:
    data = fetch(url)
    if data:
        parsed = json.loads(data)
        items = parsed.get("result", {}).get("data", [])
        sina_news = []
        for item in items[:8]:
            title = item.get("title", "")
            link = item.get("url", item.get("link", ""))
            if title and link:
                sina_news.append({"title": title, "url": link})
                print(f"  {title[:40]}...")
        results["news_sina"] = sina_news
except Exception as e:
    print(f"  Error: {e}")

# 7. Foreign exchange via Sina
print("\n=== Forex (Sina alt) ===")
for sym in ["forex_rmb"]:
    url = f"https://api.exchangerate-api.com/v4/latest/USD"
    try:
        data = fetch(url)
        if data:
            parsed = json.loads(data)
            rates = parsed.get("rates", {})
            cny_rate = rates.get("CNY", "N/A")
            jpy_rate = rates.get("JPY", "N/A")
            eur_rate = rates.get("EUR", "N/A")
            hkd_rate = rates.get("HKD", "N/A")
            print(f"  USD/CNY: {cny_rate}")
            print(f"  USD/JPY: {jpy_rate}")
            print(f"  EUR/USD: {eur_rate}")
            print(f"  USD/HKD: {hkd_rate}")
    except Exception as e:
        print(f"  Error: {e}")

# Save
with open(f"{OUTPUT_DIR}/cn_hk_extra.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved extra data")
