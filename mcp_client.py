#!/usr/bin/env python3
"""MCP Client for Sina Finance - calls MCP tools via Streamable HTTP transport."""
import json
import urllib.request
import urllib.error
import sys
import os

MCP_URL = "http://mcp.finance.sina.com.cn/mcp-http"
AUTH_TOKEN = "0be4be60e19848ae8087d06916cdf1694"

def call_mcp_tool(name, arguments=None):
    """Call an MCP tool and return the result."""
    if arguments is None:
        arguments = {}
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": name,
            "arguments": arguments
        }
    }
    
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "X-Auth-Token": AUTH_TOKEN
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_data = json.loads(resp.read().decode('utf-8'))
            if "error" in response_data and response_data["error"]:
                return {"error": response_data["error"]["message"]}
            
            # Extract content from result
            if "result" in response_data:
                content = response_data["result"].get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        try:
                            return json.loads(item["text"])
                        except (json.JSONDecodeError, KeyError):
                            return item.get("text", str(content))
                return str(content)
            return response_data
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return {"error": f"HTTP {e.code}: {body[:500]}"}
    except Exception as e:
        return {"error": str(e)}

def get_realtime_quote(market, symbol):
    """Get real-time quote for a symbol."""
    return call_mcp_tool("globalStockQuoteRealtime", {
        "market": market,
        "symbol": symbol
    })

def get_hk_sector_quotes():
    """Get HK sector quotes."""
    return call_mcp_tool("hkSectorQuotesList", {})

def get_cn_sector_ranking(index_type="hy", sort="percent", asc="0", num="5"):
    """Get A-share sector ranking."""
    return call_mcp_tool("cnVirtualSectorRanking", {
        "index_type": index_type,
        "sort": sort,
        "asc": asc,
        "num": num
    })

def get_limit_up_pool():
    """Get A-share limit-up pool."""
    return call_mcp_tool("cnMarketLimitUpPool", {})

def get_lian_ban():
    """Get A-share consecutive limit-up stocks."""
    return call_mcp_tool("cnStockLianBC", {})

def get_forex_quote(symbol):
    """Get forex quote."""
    return call_mcp_tool("forexQuoteLatest", {"symbol": symbol})

def main():
    output_path = "/home/hermes_agent/digest"
    
    # === Phase 1: HK + A-share + US indices ===
    print("=== Phase 1: Indices ===")
    
    # HK index
    hsi = get_realtime_quote("hk", "hsi")
    print(f"HSI: {json.dumps(hsi, ensure_ascii=False)[:300]}")
    
    # A-share indices
    sh = get_realtime_quote("cn", "sh")
    print(f"SH: {json.dumps(sh, ensure_ascii=False)[:300]}")
    sz = get_realtime_quote("cn", "sz")
    print(f"SZ: {json.dumps(sz, ensure_ascii=False)[:300]}")
    cy = get_realtime_quote("cn", "cy")
    print(f"CY: {json.dumps(cy, ensure_ascii=False)[:300]}")
    
    # US indices
    spx = get_realtime_quote("us", ".inx")
    print(f"SPX: {json.dumps(spx, ensure_ascii=False)[:300]}")
    ixic = get_realtime_quote("us", ".ixic")
    print(f"IXIC: {json.dumps(ixic, ensure_ascii=False)[:300]}")
    dji = get_realtime_quote("us", ".dji")
    print(f"DJI: {json.dumps(dji, ensure_ascii=False)[:300]}")
    
    # === Phase 2: HK sectors ===
    print("\n=== Phase 2: HK Sectors ===")
    hk_sectors = get_hk_sector_quotes()
    print(f"HK Sectors: {json.dumps(hk_sectors, ensure_ascii=False)[:500]}")
    
    # === Phase 3: A-share sectors ===
    print("\n=== Phase 3: A-share Sectors ===")
    hy_ranking = get_cn_sector_ranking("hy", "percent", "0", "5")
    print(f"HY Ranking: {json.dumps(hy_ranking, ensure_ascii=False)[:500]}")
    
    gn_ranking = get_cn_sector_ranking("gn", "percent", "0", "5")
    print(f"GN Ranking: {json.dumps(gn_ranking, ensure_ascii=False)[:500]}")
    
    fund_inflow = get_cn_sector_ranking("gn", "rp_net", "0", "3")
    print(f"Fund Inflow: {json.dumps(fund_inflow, ensure_ascii=False)[:500]}")
    
    # === Phase 4: Limit-up stocks ===
    print("\n=== Phase 4: Limit-up ===")
    limit_up = get_limit_up_pool()
    print(f"Limit Up: {json.dumps(limit_up, ensure_ascii=False)[:500]}")
    
    lian_ban = get_lian_ban()
    print(f"Lian Ban: {json.dumps(lian_ban, ensure_ascii=False)[:500]}")
    
    # === Phase 5: Forex ===
    print("\n=== Phase 5: Forex ===")
    for sym in ["EURUSD", "USDJPY", "USDCNY", "USDHKD"]:
        result = get_forex_quote(sym)
        print(f"{sym}: {json.dumps(result, ensure_ascii=False)[:200]}")
    
    # Save all data
    all_data = {
        "hsi": hsi,
        "sh": sh,
        "sz": sz,
        "cy": cy,
        "spx": spx,
        "ixic": ixic,
        "dji": dji,
        "hk_sectors": hk_sectors,
        "hy_ranking": hy_ranking,
        "gn_ranking": gn_ranking,
        "fund_inflow": fund_inflow,
        "limit_up": limit_up,
        "lian_ban": lian_ban
    }
    
    with open(f"{output_path}/mcp_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\nData saved to {output_path}/mcp_data.json")

if __name__ == "__main__":
    main()
