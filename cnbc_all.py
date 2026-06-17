import urllib.request, re, json, ssl, datetime

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

bonds = {
    'US10Y': '10年期美债',
    'US30Y': '30年期美债',
    'US5Y': '5年期美债',
    'US3M': '3月期美债',
}

results = {}
for sym, name in bonds.items():
    html = fetch(f'https://www.cnbc.com/quotes/{sym}')
    if html:
        m = re.search(rf'{sym}.*?(\d+\.\d+)%', html)
        if m:
            val = float(m.group(1))
            results[name] = val
            print(f'{name}: {val}%')
        else:
            print(f'{name}: yield not found')
    else:
        print(f'{name}: FAILED')

# Save for use in HTML update
with open('/home/hermes_agent/digest/cnbc_bond_data.json', 'w') as f:
    json.dump(results, f)

# Also check commodities on CNBC
print('\n--- Commodities ---')
commodities = {
    'gold': ('GC=F', '黄金'),
    'crude': ('CL=F', '原油'),
    'silver': ('SI=F', '白银'),
    'copper': ('HG=F', '铜'),
}
for key, (sym, name) in commodities.items():
    html = fetch(f'https://www.cnbc.com/quotes/{sym}')
    if html:
        m = re.search(rf'{sym}.*?(\d+\.?\d*)', html)
        if m:
            print(f'{name} ({sym}): {m.group(1)}')
        else:
            # Try broader pattern
            nums = re.findall(r'(\d+\.\d+)', html[:3000])
            print(f'{name} ({sym}): nearby nums: {nums[:5]}')
    else:
        print(f'{name}: FAILED')
