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

# Try different CNBC quote paths for commodities and crypto
tests = {
    # Commodities
    '黄金': ['/quotes/GC=', '/quotes/@GC.1', '/commodities/gold', '/quotes/?symbol=gc'],
    '原油': ['/quotes/CL=', '/quotes/@CL.1', '/commodities/crude-oil'],
    '白银': ['/quotes/SI=', '/quotes/@SI.1', '/commodities/silver'],
    '铜': ['/quotes/HG=', '/quotes/@HG.1', '/copper'],
    # Crypto
    'BTC': ['/quotes/BTC=', '/quotes/BTC.CB=', '/cryptocurrency/bitcoin'],
    'ETH': ['/quotes/ETH=', '/quotes/ETH.CB=', '/cryptocurrency/ethereum'],
}

for name, paths in tests.items():
    for path in paths:
        html = fetch(f'https://www.cnbc.com{path}', timeout=8)
        if html:
            # Look for price numbers
            nums = re.findall(r'(\d{1,5}(?:,\d{3})*(?:\.\d{1,2})?)', html[:5000])
            # Filter to reasonable numbers
            prices = [n.replace(',','') for n in nums if 10 < float(n.replace(',','')) < 200000]
            if prices:
                print(f'{name} ({path}): prices found: {prices[:5]}')
                break
            else:
                print(f'{name} ({path}): no prices')
        else:
            print(f'{name} ({path}): FAILED')
