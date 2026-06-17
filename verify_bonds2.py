import urllib.request, re, json, ssl, html as html_mod

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f'ERROR: {e}'

# Try CNBC treasury page
print("=== CNBC US Treasury page ===")
html = fetch('https://www.cnbc.com/quotes/US10Y', timeout=10)
if html and 'ERROR' not in html:
    # Look for the yield value
    for pat in [r'US10Y.*?(\d+\.?\d*)%', r'(\d+\.\d+)%.*?10-Year', r'10.*?Year.*?(\d+\.\d+)', r'(\d+\.\d+)%.*?10']:
        matches = re.findall(pat, html)
        if matches:
            print(f'  Pattern "{pat}": {matches[:3]}')
    # Just show some context
    for line in html.split('\n'):
        line = line.strip()
        if '4.4' in line or '4.5' in line or 'yield' in line.lower() or '10Y' in line or 'TNX' in line:
            if len(line) > 20 and len(line) < 200:
                print(f'  Line: {line}')
else:
    print(f'  Failed: {str(html)[:100]}')

# Try marketwatch
print('\n=== MarketWatch Treasury ==')
html2 = fetch('https://www.marketwatch.com/investing/bond/10-year', timeout=10)
if html2 and 'ERROR' not in html2:
    for line in html2.split('\n'):
        line = line.strip()
        if 'yield' in line.lower() or '4.' in line and len(line) < 200:
            line_clean = re.sub(r'<[^>]+>', ' ', line)
            line_clean = html_mod.unescape(line_clean).strip()
            if line_clean and len(line_clean) > 10:
                print(f'  {line_clean[:150]}')
else:
    print(f'  Failed: {str(html2)[:100]}')

# Try a different YF approach - use the quote endpoint
print('\n=== Yahoo Finance quotes API ==')
try:
    url3 = 'https://query2.finance.yahoo.com/v7/finance/quote?symbols=%5ETNX,%5ETYX,%5EFVX,%5EIRX'
    req3 = urllib.request.Request(url3, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req3, timeout=10, context=ssl_ctx) as resp3:
        d = json.loads(resp3.read().decode('utf-8'))
        for q in d.get('quoteResponse', {}).get('result', []):
            print(f'  {q.get("symbol")}: price={q.get("regularMarketPrice")}, prevClose={q.get("regularMarketPreviousClose")}, name={q.get("shortName")}')
except Exception as e:
    print(f'  YF quote API: {e}')

# Try with v6 API  
print('\n=== Yahoo Finance v6 API ==')
try:
    url4 = 'https://query1.finance.yahoo.com/v6/finance/quote/%5ETNX,%5ETYX,%5EFVX,%5EIRX?fields=regularMarketPrice,regularMarketPreviousClose,shortName'
    req4 = urllib.request.Request(url4, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req4, timeout=10, context=ssl_ctx) as resp4:
        d = json.loads(resp4.read().decode('utf-8'))
        for q in d.get('quoteResponse', {}).get('result', []):
            print(f'  {q.get("symbol")}: price={q.get("regularMarketPrice")}')
except Exception as e:
    print(f'  YF v6: {e}')

# Also try with Investing.com
print('\n=== investing.com ===')
try:
    url5 = 'https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield'
    # Use a simpler approach
    req5 = urllib.request.Request(url5, headers={**headers, 'Accept-Language': 'en-US,en;q=0.9'})
    with urllib.request.urlopen(req5, timeout=10, context=ssl_ctx) as resp5:
        text = resp5.read().decode('utf-8', errors='replace')
        # Look for yield value
        for pat in [r'data-testid="last-price".*?>(\d+\.\d+)', r'(\d+\.\d+)%', r'yield.*?(\d+\.\d+)']:
            m = re.search(pat, text)
            if m:
                print(f'  Found yield: {m.group(1)}')
        for line in text.split('\n'):
            if '4.' in line and 'yield' in line.lower() and len(line) < 300:
                line_clean = re.sub(r'<[^>]+>', ' ', line).strip()
                if line_clean:
                    print(f'  {line_clean[:150]}')
except Exception as e:
    print(f'  investing.com: {e}')
