#!/usr/bin/env python3
"""Fix international indices with range=5d for those that had None prev"""
import json, urllib.request, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

def yf_chart(symbol, range_v='5d'):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_v}&interval=1d'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
        return json.loads(resp.read())

def get_chg(data):
    result = data['chart']['result'][0]
    closes = [c for c in result['indicators']['quote'][0]['close'] if c is not None]
    if len(closes) >= 2:
        prev, curr = closes[-2], closes[-1]
        pct = round(((curr - prev) / prev) * 100, 2) if prev else None
        return curr, prev, pct
    return closes[-1] if closes else None, None, None

fixes = {
    'intl_日经225': '^N225',
    'intl_KOSPI': '^KS11',
    'intl_斯托克50': '^STOXX50E',
    'intl_ASX200': '^AXJO',
    'intl_NIFTY50': '^NSEI',
    'intl_DAX': '^GDAXI',
    'intl_CAC': '^FCHI',
}

with open('/home/hermes_agent/digest/today_yf.json') as f:
    data = json.load(f)

for key, sym in fixes.items():
    try:
        d = yf_chart(sym, '5d')
        price, prev, pct = get_chg(d)
        if prev is not None:
            data[key] = {'price': round(price, 2) if price else None, 'prev': round(prev, 2) if prev else None, 'pct': pct}
            print(f"Fixed {key}: {price} ({pct:+.2f}%)")
        else:
            print(f"Cannot fix {key}: only 1 bar")
    except Exception as e:
        print(f"Failed {key}: {e}")

with open('/home/hermes_agent/digest/today_yf.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Updated today_yf.json")
