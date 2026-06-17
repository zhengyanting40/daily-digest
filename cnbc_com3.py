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

# Try crypto BF symbols
print('=== Crypto via CNBC API ===')
for sym in ['BTC.BF=', 'ETH.BF=', 'BTC.CB=', 'ETH.CB=']:
    url = f'https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols={sym}&requestMethod=json'
    html = fetch(url)
    if html:
        print(f'{sym}: {html[:300]}')
    else:
        print(f'{sym}: FAILED')

# Try CNBC's REST API v1
print('\n=== CNBC v1 API ===')
for sym in ['GC', 'CL', 'SI', 'HG', 'BTC', 'ETH']:
    url = f'https://api.cnbc.com/v1/stock?symbol={sym}'
    html = fetch(url)
    if html:
        print(f'{sym}: {html[:300]}')
    else:
        print(f'{sym}: FAILED')

# Try the commodities page more carefully
print('\n=== Commodities page scrape ===')
html = fetch('https://www.cnbc.com/commodities/', timeout=10)
if html:
    # Look for JSON data in script tags
    for m in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        content = m.group(1).strip()
        if 'price' in content.lower() and len(content) > 100:
            print(f'Script with price ({len(content)} chars): {content[:300]}')
