#!/usr/bin/env python3
"""Collect data via Yahoo Finance API (works) and build complete dataset."""
import json
import urllib.request
import urllib.error
import ssl

OUTPUT_DIR = "/home/hermes_agent/digest"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def yf_quote(symbol, name_fallback=""):
    """Get quote from Yahoo Finance v8 chart API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            closes = quotes.get("close", [])
            prev_close = meta.get("chartPreviousClose", 0)
            current = None
            if closes:
                current = closes[-1]
            if current is None:
                current = meta.get("regularMarketPrice", prev_close)
            if current is None:
                current = prev_close
            change = (current - prev_close) if prev_close else 0
            change_pct = (change / prev_close * 100) if prev_close else 0
            return {
                "value": round(float(current), 2) if current else "N/A",
                "change": round(float(change), 2),
                "change_pct": f"{change_pct:+.2f}%"
            }
    except Exception as e:
        return {"value": "N/A", "change": "N/A", "change_pct": "N/A", "error": str(e)}

def yf_treasury(symbol):
    """Get treasury yield from Yahoo Finance with 5d range for accuracy."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            closes = quotes.get("close", [])
            prev_close = meta.get("chartPreviousClose", 0)
            current = closes[-1] if closes else prev_close
            if current is None:
                current = prev_close
            change = (current - prev_close) if prev_close else 0
            change_pct = (change / prev_close * 100) if prev_close else 0
            return {
                "value": f"{float(current):.3f}%" if current else "N/A",
                "change": f"{change:+.4f}" if isinstance(change, (int,float)) else "N/A",
                "change_pct": f"{change_pct:+.2f}%"
            }
    except Exception as e:
        return {"value": "N/A", "change": "N/A", "change_pct": "N/A", "error": str(e)}

def yf_gainers():
    """Get top gainers from Yahoo Finance screener."""
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&count=10&scrIds=day_gainers"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rows = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
            gainers = []
            for r in rows[:10]:
                pct = r.get("regularMarketChangePercent", {}).get("raw", 0)
                if float(pct) > 0:
                    gainers.append({
                        "name": r.get("shortName", r.get("longName", r.get("symbol", "N/A"))),
                        "symbol": r.get("symbol", ""),
                        "change_pct": f"{float(pct):+.2f}%",
                        "price": r.get("regularMarketPrice", {}).get("raw", "N/A")
                    })
            return gainers[:10]
    except Exception as e:
        return [{"error": str(e)}]

def yf_news():
    """Get news from Yahoo Finance."""
    url = "https://query1.finance.yahoo.com/v1/finance/news?count=10"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("finance", {}).get("result", [])[:10]
            news = []
            for item in items:
                news.append({
                    "title": item.get("title", "N/A"),
                    "url": f"https://finance.yahoo.com/news/{item.get('uuid', '')}" if item.get('uuid') else item.get("link", "N/A"),
                    "source": "Yahoo Finance"
                })
            return news
    except:
        return []

# === Collect Everything ===
results = {}

# US Indices
print("=== US Indices ===")
for n, s in [("S&P 500", "^GSPC"), ("Nasdaq", "^IXIC"), ("Dow Jones", "^DJI")]:
    r = yf_quote(s)
    print(f"  {n}: {r}")
    results[f"us_{s}"] = r

# US Sectors via Yahoo
print("\n=== US Sectors ===")
# Try SPDR sector ETFs for sector performance
sectors_data = {}
for s_name, s_sym in [
    ("科技(XLK)", "XLK"), ("金融(XLF)", "XLF"), ("医疗(XLV)", "XLV"), 
    ("能源(XLE)", "XLE"), ("消费(XLY)", "XLY"), ("工业(XLI)", "XLI"),
    ("公用(XLU)", "XLU"), ("地产(XLRE)", "XLRE"), ("材料(XLB)", "XLB"),
    ("必需消费(XLP)", "XLP"), ("通信(XLC)", "XLC")
]:
    r = yf_quote(s_sym)
    if r.get("value") != "N/A":
        sectors_data[s_name] = r
# Sort by change_pct descending
sectors_sorted = sorted(sectors_data.items(), key=lambda x: float(x[1]["change_pct"].replace("%","").replace("+","")), reverse=True)
top_sectors = [{"name": k, "change_pct": v["change_pct"]} for k,v in sectors_sorted[:5]]
print(f"  Top sectors: {top_sectors}")
results["us_sectors"] = top_sectors

# US Top Gainers
print("\n=== US Top Gainers ===")
gainers = yf_gainers()
print(f"  Gainers: {json.dumps(gainers, ensure_ascii=False)[:300]}")
results["us_gainers"] = gainers

# International Indices
print("\n=== International Indices ===")
intl_map = {
    "^N225": "日经225", "^KS11": "KOSPI", "^FTSE": "富时100",
    "^STOXX50E": "斯托克50", "^AXJO": "ASX 200", "^NSEI": "NIFTY 50"
}
intl_data = {}
for sym, name in intl_map.items():
    r = yf_quote(sym)
    print(f"  {name}: {r}")
    intl_data[name] = r
results["international"] = intl_data

# US Treasuries
print("\n=== US Treasuries ===")
bond_map = {"^IRX": "3个月", "^FVX": "5年", "^TNX": "10年", "^TYX": "30年"}
bond_data = {}
for sym, name in bond_map.items():
    r = yf_treasury(sym)
    print(f"  {name}美债: {r}")
    bond_data[name] = r
results["bonds"] = bond_data

# DXY
print("\n=== DXY ===")
dxy = yf_quote("DX-Y.NYB")
print(f"  DXY: {dxy}")
results["forex_DXY"] = dxy

# Forex
print("\n=== Forex ===")
fx_map = {"EURUSD=X": "EUR/USD", "USDJPY=X": "USD/JPY", "USDCNY=X": "USD/CNY", "USDHKD=X": "USD/HKD"}
fx_data = {}
for sym, name in fx_map.items():
    r = yf_quote(sym)
    print(f"  {name}: {r}")
    fx_data[name] = r
results["forex"] = fx_data

# Commodities
print("\n=== Commodities ===")
com_map = {"GC=F": "黄金", "CL=F": "原油", "SI=F": "白银", "HG=F": "铜"}
com_data = {}
for sym, name in com_map.items():
    r = yf_quote(sym)
    print(f"  {name}: {r}")
    com_data[name] = r
results["commodities"] = com_data

# Crypto
print("\n=== Crypto ===")
btc = yf_quote("BTC-USD")
eth = yf_quote("ETH-USD")
print(f"  BTC: {btc}")
print(f"  ETH: {eth}")
results["crypto"] = {"BTC": btc, "ETH": eth}

# News
print("\n=== News ===")
news = yf_news()
print(f"  Got {len(news)} news items")
results["news_yahoo"] = news

# Save
with open(f"{OUTPUT_DIR}/all_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {OUTPUT_DIR}/all_data.json")
