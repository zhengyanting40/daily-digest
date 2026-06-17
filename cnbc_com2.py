import urllib.request, re, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"}

def fetch(url, timeout=10):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

# Try CNBC's JSON API endpoints
urls = [
    ('Gold', 'https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols=GC%3D&requestMethod=json'),
    ('Crude', 'https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols=CL%3D&requestMethod=json'),
    ('Silver', 'https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols=SI%3D&requestMethod=json'),
    ('Copper', 'https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols=HG%3D&requestMethod=json'),
]

for name, url in urls:
    html = fetch(url)
    if html:
        print(f'{name}: {html[:500]}')
    else:
        print(f'{name}: FAILED')

# Try CNBC's other API
print('\n--- Try simple HTML scrape ---')
html = fetch('https://www.cnbc.com/commodities/', timeout=10)
if html:
    # Look for gold/silver/crude prices
    for term in ['gold', 'silver', 'crude', 'oil', 'copper']:
        idx = html.lower().find(term)
        if idx > 0:
            seg = html[max(0,idx-100):idx+300]
            seg_clean = re.sub(r'<[^>]+>', ' ', seg)
            print(f'{term}: ...{seg_clean[:200]}...')
else:
    print('commodities page: FAILED')

# Try crypto
print('\n--- Crypto ---')
html2 = fetch('https://www.cnbc.com/cryptocurrency/', timeout=10)
if html2:
    for term in ['bitcoin', 'ethereum', 'btc', 'eth']:
        idx = html2.lower().find(term)
        if idx > 0:
            seg = html2[max(0,idx-100):idx+300]
            seg_clean = re.sub(r'<[^>]+>', ' ', seg)
            print(f'{term}: ...{seg_clean[:200]}...')
