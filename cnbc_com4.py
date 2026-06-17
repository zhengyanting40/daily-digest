import urllib.request, re, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch(url, timeout=10):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

# Get full crypto quote data
print('=== Crypto ===')
for name, sym in [('BTC', 'BTC.CB='), ('ETH', 'ETH.CB=')]:
    url = f'https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols={sym}&requestMethod=json'
    html = fetch(url)
    if html:
        # Extract all fields
        for m in re.finditer(r'<(\w+)>([^<]*)</\1>', html):
            tag, val = m.group(1), m.group(2)
            if tag in ['last', 'change', 'pctChange', 'name', 'symbol', 'cachedTime']:
                print(f'  {name} [{tag}]: {val}')
    else:
        print(f'  {name}: FAILED')

# For commodities, try the futures page data
print('\n=== Commodities from CNBC page data ===')
html = fetch('https://www.cnbc.com/futures-and-commodities/', timeout=10)
if html:
    idx = html.find('window.__s_data=')
    if idx > 0:
        json_start = html.find('{', idx)
        # Find the closing brace by tracking depth
        depth = 0
        for i in range(json_start, min(json_start + 100000, len(html))):
            if html[i] == '{': depth += 1
            elif html[i] == '}': 
                depth -= 1
                if depth == 0:
                    json_end = i + 1
                    break
        raw = html[json_start:json_end]
        try:
            data = json.loads(raw)
            # Navigate to find quotes
            quotes = data.get('quotes', {})
            if not quotes:
                # Try to find it recursively
                def find_key(d, target):
                    if isinstance(d, dict):
                        if target in d:
                            return d[target]
                        for v in d.values():
                            r = find_key(v, target)
                            if r: return r
                    return None
                quotes = find_key(data, 'quotes') or find_key(data, 'quoteData')
            if quotes:
                print(f'  Found quotes data: {str(quotes)[:200]}')
            else:
                # Print top-level keys
                keys = list(data.keys())[:10]
                print(f'  Top keys: {keys}')
                # Look for anything with price data
                for key in keys:
                    val = str(data[key])[:100]
                    if any(x in val.lower() for x in ['gold', 'silver', 'crude', 'oil', 'price']):
                        print(f'  {key}: {val}')
        except Exception as e:
            print(f'  JSON parse error: {e}')
            print(f'  Raw (first 500): {raw[:500]}')

# Try getting commodities from the specific quote pages  
print('\n=== Individual commodity pages ===')
for name, path in [('Gold', '/quotes/@GC.1'), ('Crude', '/quotes/@CL.1')]:
    html = fetch(f'https://www.cnbc.com{path}', timeout=10)
    if html:
        # Try to find JSON-LD
        for m in re.finditer(r'application/ld\+json[^>]*>(.*?)</script>', html, re.DOTALL):
            try:
                ld = json.loads(m.group(1))
                print(f'{name} JSON-LD: {json.dumps(ld, indent=2)[:300]}')
            except:
                pass
    else:
        print(f'{name}: FAILED')
