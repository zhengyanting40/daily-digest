#!/usr/bin/env python3
"""
Fetch financial data from Yahoo Finance v8 chart API.
"""
import json
import time
import urllib.request
import urllib.error
import ssl

OUTPUT = "/home/hermes_agent/digest/yahoo_data.json"

# Create unverified SSL context (some Yahoo endpoints have SSL issues)
ssl_ctx = ssl._create_unverified_context()

def fetch_json(url, retries=3, delay=2):
    """Fetch JSON from URL with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json"
            })
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Retry {attempt+1}/{retries} after error: {e}")
                time.sleep(delay)
            else:
                print(f"  Failed after {retries} retries: {e}")
                return None

def extract_chart_data(chart_data):
    """Extract current_price, previous_close, change, percent_change from chart API response."""
    if not chart_data or "chart" not in chart_data:
        return None
    result = chart_data["chart"].get("result")
    if not result or not result[0]:
        return None
    meta = result[0].get("meta", {})
    
    current_price = meta.get("regularMarketPrice")
    prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")
    
    # Fallback: try to get last close from indicators
    if current_price is None or prev_close is None:
        try:
            closes = result[0]["indicators"]["quote"][0]["close"]
            timestamps = result[0].get("timestamp", [])
            # Filter out None closes
            valid = [(t, c) for t, c in zip(timestamps, closes) if c is not None]
            if len(valid) >= 2:
                if current_price is None:
                    current_price = valid[-1][1]
                if prev_close is None:
                    prev_close = valid[-2][1]
        except (KeyError, IndexError, TypeError):
            pass
    
    if current_price is None:
        return None
    
    change = None
    percent = None
    if prev_close is not None and prev_close != 0:
        change = round(current_price - prev_close, 4)
        percent = round((change / prev_close) * 100, 4)
    
    return {
        "price": current_price,
        "change": change,
        "percent": percent,
        "previous_close": prev_close
    }

def fetch_treasury():
    """Fetch US Treasury yields."""
    print("\n=== Treasury Yields ===")
    symbols = {
        "3m": "^IRX",
        "5y": "^FVX",
        "10y": "^TNX",
        "30y": "^TYX"
    }
    result = {}
    for key, sym in symbols.items():
        encoded_sym = sym.replace("^", "%5E")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_sym}?interval=1d&range=1mo"
        print(f"  Fetching {sym} ({key})...")
        data = fetch_json(url)
        extracted = extract_chart_data(data)
        if extracted:
            result[key] = extracted
            print(f"    Price: {extracted['price']}, Change: {extracted['change']}, %: {extracted['percent']}")
        else:
            # Try alternative API endpoint
            alt_url = f"https://query2.finance.yahoo.com/v8/finance/chart/{encoded_sym}?interval=1d&range=5d"
            data = fetch_json(alt_url)
            extracted = extract_chart_data(data)
            if extracted:
                result[key] = extracted
                print(f"    Price: {extracted['price']}, Change: {extracted['change']}, %: {extracted['percent']}")
            else:
                print(f"    FAILED")
                result[key] = None
        time.sleep(0.5)
    return result

def fetch_indices():
    """Fetch international indices."""
    print("\n=== International Indices ===")
    symbols = {
        "n225": "%5EN225",
        "ks11": "%5EKS11",
        "ftse": "%5EFTSE",
        "stoxx50e": "%5ESTOXX50E",
        "axjo": "%5EAXJO",
        "nsei": "%5ENSEI"  # NIFTY 50
    }
    result = {}
    for key, encoded in symbols.items():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?interval=1d&range=1mo"
        print(f"  Fetching {key} ({encoded})...")
        data = fetch_json(url)
        extracted = extract_chart_data(data)
        if extracted:
            result[key] = extracted
            print(f"    Price: {extracted['price']}, Change: {extracted['change']}, %: {extracted['percent']}")
        else:
            print(f"    FAILED")
            result[key] = None
        time.sleep(0.5)
    return result

def fetch_commodities():
    """Fetch commodities."""
    print("\n=== Commodities ===")
    symbols = {
        "gold": "GC%3DF",
        "crude": "CL%3DF",
        "silver": "SI%3DF",
        "copper": "HG%3DF"
    }
    result = {}
    for key, encoded in symbols.items():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?interval=1d&range=5d"
        print(f"  Fetching {key} ({encoded})...")
        data = fetch_json(url)
        extracted = extract_chart_data(data)
        if extracted:
            result[key] = extracted
            print(f"    Price: {extracted['price']}, Change: {extracted['change']}, %: {extracted['percent']}")
        else:
            print(f"    FAILED")
            result[key] = None
        time.sleep(0.5)
    return result

def fetch_crypto():
    """Fetch cryptocurrencies."""
    print("\n=== Cryptocurrencies ===")
    symbols = {
        "btc": "BTC-USD",
        "eth": "ETH-USD"
    }
    result = {}
    for key, sym in symbols.items():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
        print(f"  Fetching {sym}...")
        data = fetch_json(url)
        extracted = extract_chart_data(data)
        if extracted:
            result[key] = extracted
            print(f"    Price: {extracted['price']}, Change: {extracted['change']}, %: {extracted['percent']}")
        else:
            print(f"    FAILED")
            result[key] = None
        time.sleep(0.5)
    return result

def fetch_gainers():
    """Fetch top gainers from Yahoo Finance by scraping the HTML page."""
    print("\n=== Top Gainers ===")
    url = "https://finance.yahoo.com/markets/stocks/gainers/"
    
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        })
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
            html = resp.read().decode()
    except Exception as e:
        print(f"  HTML scrape failed: {e}")
        # Try the API approach
        return fetch_gainers_api()
    
    gainers = []
    
    # Try to parse the HTML - look for JSON data embedded in the page
    # Yahoo embeds market data in script tags with specific patterns
    
    # Method 1: Look for the stores embedded data
    import re
    
    # Try to find the screener results from embedded app data
    patterns = [
        r'"symbol":\s*"([^"]+)"[^}]*"regularMarketChangePercent":\s*([0-9.-]+)',
        r'"symbol":\s*"([^"]+)"[^}]*"regularMarketPrice":\s*([0-9.]+)',
    ]
    
    # Try to find structured data in the page
    # Look for fin-streamer elements or data-symbol attributes
    fin_streamers = re.findall(
        r'<fin-streamer[^>]*data-symbol="([^"]+)"[^>]*data-field="regularMarketPrice"[^>]*value="([^"]+)"[^>]*>',
        html
    )
    
    # Also look for change percent
    fin_changes = re.findall(
        r'<fin-streamer[^>]*data-symbol="([^"]+)"[^>]*data-field="regularMarketChangePercent"[^>]*value="([^"]+)"[^>]*>',
        html
    )
    
    fin_names = re.findall(
        r'<fin-streamer[^>]*data-symbol="([^"]+)"[^>]*class="[^"]*"[^>]*>([^<]+)</fin-streamer>',
        html
    )
    
    # If we have price data, construct gainers
    if fin_streamers:
        price_map = {}
        for sym, val in fin_streamers:
            price_map.setdefault(sym, {})["price"] = float(val)
        
        for sym, val in fin_changes:
            price_map.setdefault(sym, {})["percent"] = float(val)
        
        for sym, val in fin_names:
            # Skip if not a stock symbol (length check)
            price_map.setdefault(sym, {})["name"] = val.strip()
        
        for sym, data in price_map.items():
            if "price" in data and "percent" in data:
                gainers.append({
                    "symbol": sym,
                    "name": data.get("name", sym),
                    "price": data["price"],
                    "percent": data["percent"]
                })
        
        # Sort by percent descending
        gainers.sort(key=lambda x: x["percent"], reverse=True)
        gainers = gainers[:10]
    
    # If HTML parsing didn't work, try API
    if not gainers:
        print("  HTML parsing got nothing, trying API approach...")
        return fetch_gainers_api()
    
    print(f"  Found {len(gainers)} gainers from HTML")
    for g in gainers:
        print(f"    {g['symbol']}: {g['price']} ({g['percent']}%)")
    return gainers

def fetch_gainers_api():
    """Fetch top gainers using Yahoo Finance screener API."""
    print("  Using screener API...")
    
    # Yahoo Finance v6 screener API
    url = ("https://query1.finance.yahoo.com/v6/finance/quote/marketSummary?"
           "lang=en-US&region=US")
    
    try:
        data = fetch_json(url)
        if data and "marketSummaryResponse" in data:
            quotes = data["marketSummaryResponse"].get("result", [])
            # Filter for stocks and sort by percent change
            gainers = []
            for q in quotes:
                sym = q.get("symbol", "")
                name = q.get("shortName") or q.get("longName", sym)
                price = q.get("regularMarketPrice", {}).get("raw")
                prev_close = q.get("regularMarketPreviousClose", {}).get("raw")
                pct = q.get("regularMarketChangePercent", {}).get("raw")
                
                if price and pct is not None:
                    gainers.append({
                        "symbol": sym,
                        "name": name,
                        "price": price,
                        "percent": round(pct, 2)
                    })
            
            gainers.sort(key=lambda x: x["percent"], reverse=True)
            gainers = gainers[:10]
            
            if gainers:
                print(f"  Found {len(gainers)} gainers from marketSummary")
                for g in gainers:
                    print(f"    {g['symbol']}: {g['price']} ({g['percent']}%)")
                return gainers
    except Exception as e:
        print(f"  marketSummary API failed: {e}")
    
    # Try Yahoo Finance screener API with specific query for top gainers
    # Different endpoint: v1/finance/screener
    screener_url = "https://query1.finance.yahoo.com/v1/finance/screener"
    
    payload = {
        "size": 10,
        "offset": 0,
        "sortField": "percentchange",
        "sortType": "DESC",
        "quoteType": "EQUITY",
        "query": {
            "operator": "and",
            "operands": [
                {"operator": "gt", "operands": ["price", "2"]},
                {"operator": "gt", "operands": ["dayvolume", "100000"]}
            ]
        },
        "userId": "",
        "userIdType": "guid"
    }
    
    try:
        req = urllib.request.Request(screener_url, data=json.dumps(payload).encode(), headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        quotes = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
        gainers = []
        for q in quotes:
            sym = q.get("symbol", "")
            name = q.get("shortName") or q.get("longName", sym)
            price = q.get("regularMarketPrice")
            pct = q.get("regularMarketChangePercent")
            if price and pct is not None:
                gainers.append({
                    "symbol": sym,
                    "name": name,
                    "price": price,
                    "percent": round(pct, 2)
                })
        
        if gainers:
            print(f"  Found {len(gainers)} gainers from screener")
            for g in gainers:
                print(f"    {g['symbol']}: {g['price']} ({g['percent']}%)")
            return gainers
    except Exception as e:
        print(f"  Screener API failed: {e}")
    
    # Last resort: use quotes API for some known top gainers or major movers
    print("  All gainer methods failed.")
    return []

def main():
    print("=" * 60)
    print("Yahoo Finance Data Collector")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)
    
    result = {
        "treasury": fetch_treasury(),
        "indices": fetch_indices(),
        "commodities": fetch_commodities(),
        "crypto": fetch_crypto(),
        "gainers": fetch_gainers(),
        "_metadata": {
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "source": "Yahoo Finance v8 chart API"
        }
    }
    
    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"Data saved to {OUTPUT}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
