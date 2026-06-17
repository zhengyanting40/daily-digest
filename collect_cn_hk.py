#!/usr/bin/env python3
"""Collect A-share, HK data via Sina Finance APIs."""
import urllib.request
import re
import json
import ssl

OUTPUT_DIR = "/home/hermes_agent/digest"
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36", "Referer": "https://finance.sina.com.cn"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode("gbk", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

def fetch_utf8(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

results = {}

# 1. A-share indices via Sina JS API
print("=== A-Share Indices ===")
raw = fetch("https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006")
print(raw[:300])
# Parse: var hq_str_s_sh000001="上证指数,4057.7400,-10.8291,-0.27,6760258,131980191";
indices = {}
for line in raw.split(";"):
    if "hq_str_s_" in line:
        parts = line.split('"')
        if len(parts) >= 2:
            data = parts[1].split(",")
            name = data[0]
            price = data[1]
            change = data[2]
            chg_pct = data[3]
            indices[name] = {"value": price, "change": change, "change_pct": chg_pct + "%"}
            print(f"  {name}: {price} {change} {chg_pct}%")
results["cn_indices"] = indices

# 2. HK index
print("\n=== HK Indices ===")
raw = fetch("https://hq.sinajs.cn/list=hkHSI")
print(raw[:200])
for line in raw.split(";"):
    if "hq_str_hk" in line:
        parts = line.split('"')
        if len(parts) >= 2:
            data = parts[1].split(",")
            # HSI,恒生指数,25180.050,25182.391,25486.760,25174.300,25398.180,215.789,0.857,...
            # name=data[1], open=data[2], high=data[3], low=data[4], last_close=data[5], current=data[6], chg=data[7], chg_pct=data[8]
            name = data[1]
            current = data[6]
            chg = data[7]
            chg_pct = data[8]
            results["hk_index"] = {"name": name, "value": current, "change": chg, "change_pct": f"{float(chg_pct):+.3f}%"}
            print(f"  {name}: {current} {chg} {chg_pct}%")

# 3. A-share industry sectors (hy) using Sina industry ranking page
print("\n=== A-Share Industry Sectors ===")
html = fetch("https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/jg/index.phtml")
rows = re.findall(r'<tr[^>]*>.*?</tr>', html, re.DOTALL)
sectors_hy = []
for row in rows[1:6]:  # Skip header, get top 5
    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
    if len(cells) >= 4:
        name = re.sub(r'<[^>]+>', '', cells[0]).strip()
        chg = re.sub(r'<[^>]+>', '', cells[2]).strip()
        sectors_hy.append({"name": name, "change_pct": chg})
        print(f"  {name}: {chg}")
results["cn_hy_sectors"] = sectors_hy

# 4. A-share concept sectors (gn)
print("\n=== A-Share Concept Sectors ===")
html = fetch("https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/gn/index.phtml")
rows = re.findall(r'<tr[^>]*>.*?</tr>', html, re.DOTALL)
sectors_gn = []
for row in rows[1:6]:
    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
    if len(cells) >= 4:
        name = re.sub(r'<[^>]+>', '', cells[0]).strip()
        chg = re.sub(r'<[^>]+>', '', cells[2]).strip()
        sectors_gn.append({"name": name, "change_pct": chg})
        print(f"  {name}: {chg}")
results["cn_gn_sectors"] = sectors_gn

# 5. HK sectors
print("\n=== HK Sectors ===")
html = fetch("https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/hk_jg/index.phtml")
rows = re.findall(r'<tr[^>]*>.*?</tr>', html, re.DOTALL)
hk_sectors = []
for row in rows[1:6]:
    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
    if len(cells) >= 4:
        name = re.sub(r'<[^>]+>', '', cells[0]).strip()
        chg = re.sub(r'<[^>]+>', '', cells[2]).strip()
        hk_sectors.append({"name": name, "change_pct": chg})
        print(f"  {name}: {chg}")
results["hk_sectors"] = hk_sectors

# 6. Fund flow - try Sina moneyflow page
print("\n=== A-Share Fund Flow ===")
html = fetch("https://vip.stock.finance.sina.com.cn/moneyflow/?page=hy&sort=7")
# Try to find fund flow data from table
rows = re.findall(r'<tr[^>]*>.*?</tr>', html, re.DOTALL)
fund_flow = []
for row in rows[1:6]:
    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
    if len(cells) >= 6:
        name = re.sub(r'<[^>]+>', '', cells[0]).strip()
        inflow = re.sub(r'<[^>]+>', '', cells[6]).strip() if len(cells) > 6 else "N/A"
        fund_flow.append({"name": name, "inflow": inflow})
        print(f"  {name}: 主力净流入 {inflow}")
results["cn_fund_flow"] = fund_flow

# 7. News - try eastmoney
print("\n=== News: East Money ===")
html = fetch_utf8("https://finance.eastmoney.com/")
# Extract news links
news_items = re.findall(r'<a[^>]*href="(https?://finance\.eastmoney\.com/a/[^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)
eastmoney_news = []
seen_titles = set()
for url, title in news_items[:15]:
    title_clean = re.sub(r'<[^>]+>', '', title).strip()
    if title_clean and len(title_clean) > 8 and title_clean not in seen_titles:
        seen_titles.add(title_clean)
        eastmoney_news.append({"title": title_clean, "url": url})
        print(f"  {title_clean[:50]}...")
    if len(eastmoney_news) >= 8:
        break
results["news_eastmoney"] = eastmoney_news

# 8. Forex specific - get more precise change_pct  
print("\n=== Forex (via Sina) ===")
for sym in ["EURUSD", "USDJPY", "USDCNY", "USDHKD", "DXY"]:
    raw = fetch(f"https://hq.sinajs.cn/list=fx_s{sym}")
    print(f"  {sym}: {raw[:200]}")

# Save
with open(f"{OUTPUT_DIR}/cn_hk_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {OUTPUT_DIR}/cn_hk_data.json")
