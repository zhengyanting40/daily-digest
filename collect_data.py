#!/usr/bin/env python3
"""Complete data collection: MCP + Yahoo Finance + News"""
import json
import urllib.request
import urllib.error
import sys
import os
import re
import ssl
from datetime import datetime

MCP_URL = "http://mcp.finance.sina.com.cn/mcp-http"
AUTH_TOKEN = "0be4facb91bb0744437948d188471694"
OUTPUT_DIR = "/home/hermes_agent/digest"

# Create SSL context that allows HTTPS
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def call_mcp(name, arguments=None):
    if arguments is None:
        arguments = {}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments}
    }
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json", "X-Auth-Token": AUTH_TOKEN}
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if "error" in data and data["error"]:
                return {"error": data["error"]["message"]}
            if "result" in data:
                content = data["result"].get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        try:
                            return json.loads(item["text"])
                        except:
                            return item.get("text", str(content))
                return str(content)
            return data
    except Exception as e:
        return {"error": str(e)}

def yahoo_quote(symbol):
    """Get quote from Yahoo Finance v8 API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            closes = quotes.get("close", [])
            opens = quotes.get("open", [])
            prev_close = meta.get("chartPreviousClose", 0)
            current = closes[-1] if closes else prev_close
            if current is None or current == 0:
                current = prev_close
            reg_price = meta.get("regularMarketPrice", current) or current
            change = reg_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            return {
                "name": meta.get("shortName", symbol),
                "value": round(reg_price, 2) if reg_price else "N/A",
                "change": round(change, 2),
                "change_pct": f"{change_pct:+.2f}%"
            }
    except Exception as e:
        return {"name": symbol, "value": "N/A", "change": "N/A", "change_pct": "N/A", "error": str(e)}

def yahoo_treasury(symbol):
    """Get treasury yield from Yahoo Finance."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
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
                "value": f"{current:.3f}%" if current else "N/A",
                "change": f"{change:+.3f}",
                "change_pct": f"{change_pct:+.2f}%"
            }
    except Exception as e:
        return {"value": "N/A", "change": "N/A", "change_pct": "N/A", "error": str(e)}

def yahoo_top_gainers():
    """Get top gainers from Yahoo Finance."""
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&count=10&scrIds=most_actively_traded"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            rows = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
            gainers = []
            for r in rows[:10]:
                pct = r.get("regularMarketChangePercent", {}).get("raw", 0)
                gainers.append({
                    "name": r.get("shortName", r.get("longName", "N/A")),
                    "symbol": r.get("symbol", ""),
                    "change_pct": f"{pct:+.2f}%",
                    "price": r.get("regularMarketPrice", {}).get("raw", "N/A")
                })
            # Sort by gain percent descending
            gainers.sort(key=lambda x: abs(float(x["change_pct"].replace("%","").replace("+",""))), reverse=True)
            return gainers
    except:
        # Fallback: try day-gainers screener
        try:
            url2 = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=day_gainers&count=10"
            req2 = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2, timeout=15, context=ssl_ctx) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                rows = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
                gainers = []
                for r in rows[:10]:
                    pct = r.get("regularMarketChangePercent", {}).get("raw", 0)
                    gainers.append({
                        "name": r.get("shortName", r.get("longName", "N/A")),
                        "symbol": r.get("symbol", ""),
                        "change_pct": f"{pct:+.2f}%",
                        "price": r.get("regularMarketPrice", {}).get("raw", "N/A")
                    })
                return gainers
        except:
            return []

def parse_mcp_quote(result):
    """Parse MCP quote result to extract value and change."""
    if isinstance(result, dict):
        if "error" in result:
            return {"value": "N/A", "change": "N/A", "change_pct": "N/A", "error": result["error"]}
        # Try common patterns
        name = result.get("name", result.get("stockName", result.get("sec_name", "N/A")))
        price = result.get("currentPrice", result.get("price", result.get("current", result.get("now", "N/A"))))
        change = result.get("priceChange", result.get("change", result.get("changePercent", result.get("chg", "N/A"))))
        chg_pct = result.get("changePercent", result.get("chgPct", result.get("chg_pct", "N/A")))
        
        # Handle change as percent vs absolute
        if chg_pct != "N/A" and isinstance(chg_pct, (int, float)):
            return {"name": name, "value": price, "change": change, "change_pct": f"{chg_pct:+.2f}%"}
        
        # Try to find from open/close diff
        if isinstance(result, dict) and "open" in result and "close" in result:
            try:
                close = float(result.get("close", 0))
                open_ = float(result.get("open", 0))
                if close and open_:
                    chg = close - open_
                    chg_pct_calc = (chg / open_ * 100)
                    return {"name": name, "value": close, "change": chg, "change_pct": f"{chg_pct_calc:+.2f}%"}
            except:
                pass
    
    return result

def extract_mcp_fields(data):
    """Extract numeric fields from MCP response lists."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data
    return []

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = {}
    
    # === PHASE 1: MCP Data Collection ===
    print("=" * 60)
    print("PHASE 1: MCP Data Collection")
    print("=" * 60)
    
    # A-share indices - use full symbols
    print("\n-- A-Share Indices --")
    for name, sym, market in [
        ("上证指数", "sh000001", "cn"),
        ("深证成指", "sz399001", "cn"),
        ("创业板指", "sz399006", "cn"),
    ]:
        r = call_mcp("globalStockQuoteRealtime", {"market": market, "symbol": sym})
        print(f"  {name} ({sym}): {json.dumps(r, ensure_ascii=False)[:200]}")
        results[f"cn_{sym}"] = r
    
    # HK index
    print("\n-- HK Indices --")
    hsi = call_mcp("globalStockQuoteRealtime", {"market": "hk", "symbol": "HSI"})
    print(f"  恒生指数: {json.dumps(hsi, ensure_ascii=False)[:200]}")
    results["hk_HSI"] = hsi
    
    # US ETFs
    print("\n-- US ETFs --")
    for name, sym in [("S&P 500(SPY)", "SPY"), ("Nasdaq(QQQ)", "QQQ"), ("Dow(DIA)", "DIA")]:
        r = call_mcp("globalStockQuoteRealtime", {"market": "us", "symbol": sym})
        print(f"  {name}: {json.dumps(r, ensure_ascii=False)[:200]}")
        results[f"us_{sym}"] = r
    
    # A-share sector rankings
    print("\n-- A-Share Sector Rankings --")
    hy = call_mcp("cnVirtualSectorRanking", {"index_type": "hy", "sort": "percent", "asc": "0", "num": "5"})
    print(f"  行业板块: {json.dumps(hy, ensure_ascii=False)[:300]}")
    results["cn_hy_ranking"] = hy
    
    gn = call_mcp("cnVirtualSectorRanking", {"index_type": "gn", "sort": "percent", "asc": "0", "num": "5"})
    print(f"  概念板块: {json.dumps(gn, ensure_ascii=False)[:300]}")
    results["cn_gn_ranking"] = gn
    
    # A-share fund inflow
    fund = call_mcp("cnVirtualSectorRanking", {"sort": "rp_net", "asc": "0", "num": "3"})
    print(f"  资金流入: {json.dumps(fund, ensure_ascii=False)[:300]}")
    results["cn_fund_inflow"] = fund
    
    # A-share limit-up and consecutive boards
    print("\n-- A-Share Limit Up / Lian Ban --")
    limit_up = call_mcp("cnMarketLimitUpPool", {})
    print(f"  涨停池: (received {len(json.dumps(limit_up, ensure_ascii=False))} chars)")
    results["cn_limit_up"] = limit_up
    
    lian_ban = call_mcp("cnStockLianBC", {})
    print(f"  连板股: (received {len(json.dumps(lian_ban, ensure_ascii=False))} chars)")
    results["cn_lian_ban"] = lian_ban
    
    # HK sectors
    print("\n-- HK Sectors --")
    hk_sectors = call_mcp("hkSectorQuotesList", {"type": "hk_plate_rise", "num": "5"})
    print(f"  HK领涨板块: {json.dumps(hk_sectors, ensure_ascii=False)[:300]}")
    results["hk_sectors"] = hk_sectors
    
    # US sectors
    print("\n-- US Sectors --")
    us_sectors = call_mcp("usSectorRanking", {"sort": "percent", "asc": "0", "num": "5"})
    print(f"  US sectors: {json.dumps(us_sectors, ensure_ascii=False)[:300]}")
    results["us_sectors"] = us_sectors
    
    # Forex
    print("\n-- Forex --")
    for sym in ["EURUSD", "USDJPY", "USDCNY", "USDHKD"]:
        r = call_mcp("forexQuoteLatest", {"symbol": sym})
        print(f"  {sym}: {json.dumps(r, ensure_ascii=False)[:150]}")
        results[f"fx_{sym}"] = r
    
    # === PHASE 2: Yahoo Finance Data ===
    print("\n" + "=" * 60)
    print("PHASE 2: Yahoo Finance Data")
    print("=" * 60)
    
    # US indices directly
    print("\n-- US Indices (Yahoo) --")
    for name, sym in [("S&P 500", "^GSPC"), ("Nasdaq", "^IXIC"), ("Dow Jones", "^DJI")]:
        r = yahoo_quote(sym)
        print(f"  {name}: {r}")
        results[f"yahoo_{sym.replace('^','')}"] = r
    
    # International indices
    print("\n-- International Indices --")
    for name, sym in [
        ("日经225", "^N225"), ("KOSPI", "^KS11"), ("富时100", "^FTSE"),
        ("斯托克50", "^STOXX50E"), ("ASX 200", "^AXJO"), ("NIFTY 50", "^NSEI")
    ]:
        r = yahoo_quote(sym)
        print(f"  {name}: {r}")
        results[f"intl_{sym.replace('^','')}"] = r
    
    # US Treasury yields
    print("\n-- US Treasury Yields --")
    for name, sym in [("3-Month", "^IRX"), ("5-Year", "^FVX"), ("10-Year", "^TNX"), ("30-Year", "^TYX")]:
        r = yahoo_treasury(sym)
        print(f"  {name}: {r}")
        results[f"bond_{sym.replace('^','')}"] = r
    
    # DXY (forex index)
    print("\n-- DXY --")
    dxy = yahoo_quote("DXY=X")
    print(f"  DXY: {dxy}")
    results["fx_DXY"] = dxy
    
    # Commodities
    print("\n-- Commodities --")
    for name, sym in [("黄金", "GC=F"), ("原油", "CL=F"), ("白银", "SI=F"), ("铜", "HG=F")]:
        r = yahoo_quote(sym)
        print(f"  {name}: {r}")
        results[f"commod_{sym.replace('=','').replace('F','').lower()}"] = r
    
    # Crypto
    print("\n-- Crypto --")
    btc = yahoo_quote("BTC-USD")
    print(f"  BTC: {btc}")
    results["crypto_btc"] = btc
    eth = yahoo_quote("ETH-USD")
    print(f"  ETH: {eth}")
    results["crypto_eth"] = eth
    
    # US Top Gainers
    print("\n-- US Top Gainers --")
    gainers = yahoo_top_gainers()
    print(f"  Top gainers: {json.dumps(gainers, ensure_ascii=False)[:300]}")
    results["us_top_gainers"] = gainers
    
    # === PHASE 3: News ===
    print("\n" + "=" * 60)
    print("PHASE 3: News")
    print("=" * 60)
    
    news = call_mcp("newsArticleList", {"page": "1", "num": "15"})
    print(f"  News: {json.dumps(news, ensure_ascii=False)[:500]}")
    results["news_mcp"] = news
    
    # === SAVE ALL ===
    print("\n" + "=" * 60)
    print("Saving data...")
    
    with open(f"{OUTPUT_DIR}/mcp_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved to {OUTPUT_DIR}/mcp_data.json")
    
    # Also save a summary for quick reference
    summary = {
        "cn_indices": {},
        "hk_indices": {},
        "us_indices": {},
        "intl_indices": {},
        "cn_sectors_hy": [],
        "cn_sectors_gn": [],
        "cn_fund_inflow": [],
        "cn_top_stocks": [],
        "us_sectors": [],
        "us_top_gainers": results.get("us_top_gainers", []),
        "bonds": {},
        "forex": {},
        "commodities": {},
        "crypto": {},
        "news": []
    }
    
    # Extract indices
    for key, data in results.items():
        if key.startswith("cn_sh000001"):
            summary["cn_indices"]["上证指数"] = data
        elif key.startswith("cn_sz399001"):
            summary["cn_indices"]["深证成指"] = data
        elif key.startswith("cn_sz399006"):
            summary["cn_indices"]["创业板指"] = data
        elif key.startswith("hk_HSI"):
            summary["hk_indices"]["恒生指数"] = data
        elif key.startswith("yahoo_GSPC"):
            summary["us_indices"]["标普500"] = data
        elif key.startswith("yahoo_IXIC"):
            summary["us_indices"]["纳斯达克"] = data
        elif key.startswith("yahoo_DJI"):
            summary["us_indices"]["道琼斯"] = data
        elif key.startswith("intl_N225"):
            summary["intl_indices"]["日经225"] = data
        elif key.startswith("intl_KS11"):
            summary["intl_indices"]["KOSPI"] = data
        elif key.startswith("intl_FTSE"):
            summary["intl_indices"]["富时100"] = data
        elif key.startswith("intl_STOXX50E"):
            summary["intl_indices"]["斯托克50"] = data
        elif key.startswith("intl_AXJO"):
            summary["intl_indices"]["ASX 200"] = data
        elif key.startswith("intl_NSEI"):
            summary["intl_indices"]["NIFTY50"] = data
        elif key.startswith("bond_IRX"):
            summary["bonds"]["3个月"] = data
        elif key.startswith("bond_FVX"):
            summary["bonds"]["5年"] = data
        elif key.startswith("bond_TNX"):
            summary["bonds"]["10年"] = data
        elif key.startswith("bond_TYX"):
            summary["bonds"]["30年"] = data
        elif key.startswith("fx_DXY"):
            summary["forex"]["DXY"] = data
        elif key.startswith("fx_EURUSD"):
            summary["forex"]["EUR/USD"] = data
        elif key.startswith("fx_USDJPY"):
            summary["forex"]["USD/JPY"] = data
        elif key.startswith("fx_USDCNY"):
            summary["forex"]["USD/CNY"] = data
        elif key.startswith("fx_USDHKD"):
            summary["forex"]["USD/HKD"] = data
        elif key.startswith("commod_gc"):
            summary["commodities"]["黄金"] = data
        elif key.startswith("commod_cl"):
            summary["commodities"]["原油"] = data
        elif key.startswith("commod_si"):
            summary["commodities"]["白银"] = data
        elif key.startswith("commod_hg"):
            summary["commodities"]["铜"] = data
        elif key.startswith("crypto_btc"):
            summary["crypto"]["BTC"] = data
        elif key.startswith("crypto_eth"):
            summary["crypto"]["ETH"] = data
    
    # Extract sector rankings
    hy_data = results.get("cn_hy_ranking", [])
    if isinstance(hy_data, list):
        summary["cn_sectors_hy"] = [{"name": s.get("bkname", s.get("name", "N/A")), "change_pct": s.get("chg_pct", s.get("changePercent", s.get("c1", "N/A")))} for s in hy_data[:5] if isinstance(s, dict)]
    
    gn_data = results.get("cn_gn_ranking", [])
    if isinstance(gn_data, list):
        summary["cn_sectors_gn"] = [{"name": s.get("bkname", s.get("name", "N/A")), "change_pct": s.get("chg_pct", s.get("changePercent", s.get("c1", "N/A")))} for s in gn_data[:5] if isinstance(s, dict)]
    
    fund_data = results.get("cn_fund_inflow", [])
    if isinstance(fund_data, list):
        for s in fund_data[:3]:
            if isinstance(s, dict):
                name = s.get("bkname", s.get("name", "N/A"))
                rp_net = s.get("rp_net", 0)
                try:
                    rp_net_val = float(rp_net) if rp_net else 0
                    rp_net_yi = rp_net_val / 1e8
                except:
                    rp_net_yi = 0
                summary["cn_fund_inflow"].append({"name": name, "amount_yi": f"{rp_net_yi:.1f}亿"})
    
    with open(f"{OUTPUT_DIR}/today_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Saved summary to {OUTPUT_DIR}/today_summary.json")
    
    print("\nData collection complete!")

if __name__ == "__main__":
    main()
