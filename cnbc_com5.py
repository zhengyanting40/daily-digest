import urllib.request, re, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0"}

def fetch(url, timeout=10):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

# Get full crypto data with pctChange
print('=== CNBC Crypto (Coinbase, June 15 close) ===')
for name, sym in [('BTC', 'BTC.CB='), ('ETH', 'ETH.CB=')]:
    url = f'https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols={sym}&requestMethod=json'
    html = fetch(url)
    if html:
        for m in re.finditer(r'<(\w+)>([^<]*)</\1>', html):
            tag, val = m.group(1), m.group(2)
            if tag in ['last', 'change', 'pctChange', 'open', 'high', 'low', 'previousDay', 'name']:
                print(f'  {name} [{tag}]: {val}')
        print()

# Check if CNBC gold page has price data in __s_data
print('=== Gold page __s_data check ===')
html = fetch('https://www.cnbc.com/quotes/@GC.1', timeout=10)
if html:
    # Search for last/price in __s_data
    idx = html.find('window.__s_data=')
    if idx > 0:
        json_start = html.find('{', idx)
        depth = 0
        for i in range(json_start, min(json_start + 80000, len(html))):
            if html[i] == '{': depth += 1
            elif html[i] == '}': 
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        raw = html[json_start:end]
        try:
            data = json.loads(raw)
            # Search for quote data  
            def find_quotes(d, depth=0):
                if depth > 5: return None
                if isinstance(d, dict):
                    if 'last' in d or 'price' in d:
                        return d
                    for k, v in d.items():
                        r = find_quotes(v, depth+1)
                        if r: return r
                return None
            q = find_quotes(data)
            if q:
                print(f'  Found quote data: {json.dumps(q, indent=2)[:500]}')
            else:
                # Try specific paths
                for path in ['quoteData', 'quotes', 'symbolData']:
                    parts = path.split('.')
                    cur = data
                    for p in parts:
                        if isinstance(cur, dict) and p in cur:
                            cur = cur[p]
                        else:
                            cur = None
                            break
                    if cur:
                        print(f'  {path}: {json.dumps(cur, indent=2)[:300]}')
        except Exception as e:
            print(f'  JSON error: {e}')
else:
    print('  FAILED')
