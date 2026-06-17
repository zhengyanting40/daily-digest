import urllib.request, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Try multiple sources for 10Y yield

# 1. Yahoo Finance - use different API endpoint
print("=== Source 1: Yahoo Finance v8 chart (range=1mo) ===")
symbols = ['^TNX', '^TYX', '^FVX', '^IRX']
for sym in symbols:
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1mo&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            r = data['chart']['result'][0]
            meta = r['meta']
            quotes = r['indicators']['quote'][0]['close']
            timestamps = r['timestamp']
            print(f'\n{sym}:')
            print(f'  Latest price from meta: {meta.get("regularMarketPrice")}')
            print(f'  Previous close from meta: {meta.get("chartPreviousClose")}')
            print(f'  Currency: {meta.get("currency")}')
            print(f'  Exchange: {meta.get("exchangeName")}')
            print(f'  Instrument type: {meta.get("instrumentType")}')
            # Show last 5 data points
            for i in range(max(0, len(timestamps)-5), len(timestamps)):
                import datetime
                dt = datetime.datetime.fromtimestamp(timestamps[i])
                print(f'  [{dt.strftime("%Y-%m-%d")}] close={quotes[i]}')
    except Exception as e:
        print(f'{sym}: ERROR: {e}')

# 2. Try investing.com or other data sources for comparison
print('\n=== Source 2: Try alternative API ===')
# Try CNBC for bond data
try:
    url2 = 'https://search.cnbc.com/rs/search/combinedcms/view?partnerId=wrss01&id=100987&source=proftitloss'
    req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req2, timeout=10, context=ssl_ctx) as resp2:
        print(f'CNBC bonds: status={resp2.status}')
        content = resp2.read().decode('utf-8')[:500]
        print(content[:500])
except Exception as e:
    print(f'CNBC: {e}')

# 3. Try US Treasury website via a mirror
print('\n=== Source 3: Try to get real-time treasury data ===')
try:
    # Use a known working API
    url3 = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?format=json'
    req3 = urllib.request.Request(url3, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req3, timeout=10, context=ssl_ctx) as resp3:
        d = json.loads(resp3.read().decode('utf-8'))
        print(f'Treasury API: {json.dumps(d, indent=2)[:2000]}')
except Exception as e:
    print(f'Treasury: {e}')
