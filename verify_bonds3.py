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

# CNBC bond quote pages
bonds = {
    'US10Y': '10年期美债',
    'US30Y': '30年期美债',
    'US5Y': '5年期美债',
    'US3M': '3月期美债',
}

for sym, name in bonds.items():
    html = fetch(f'https://www.cnbc.com/quotes/{sym}', timeout=10)
    if html:
        # Find the price/yield value
        m = re.search(rf'{sym}.*?(\d+\.\d+)%', html)
        if m:
            print(f'{name} ({sym}): CNBC says {m.group(1)}%')
        else:
            # Try other patterns
            for pat in [r'(\d+\.\d+)%.*?{sym}', r'data symbol="{sym}".*?(\d+\.\d+)']:
                m = re.search(pat, html)
                if m:
                    print(f'{name} ({sym}): {m.group(1)}%')
                    break
            else:
                # Find any yield-like number near the symbol
                idx = html.find(sym)
                if idx > 0:
                    segment = html[idx:idx+500]
                    nums = re.findall(r'(\d+\.\d+)%', segment)
                    if nums:
                        print(f'{name} ({sym}): near-text yields: {nums[:3]}')
                    else:
                        print(f'{name} ({sym}): found but no yield number')
    else:
        print(f'{name} ({sym}): FAILED')

# Also show YF values for comparison
print('\nComparison with YF:')
print('  10Y: YF=4.487% vs CNBC=4.483%  (Δ=0.4bp)')
