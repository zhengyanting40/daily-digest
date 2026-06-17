#!/usr/bin/env python3
"""Collect YF data: bonds, commodities, crypto, intl indices, DXY, top gainers"""
import json, urllib.request, ssl, time

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def yf_chart(symbol, range_val='2d'):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_val}&interval=1d'
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        data = json.loads(urllib.request.urlopen(req, context=ssl_ctx, timeout=15).read())
        result = data['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        timestamps = result.get('timestamp', [])
        meta = result.get('meta', {})
        # Filter out None values
        closes = [c for c in closes if c is not None]
        if len(closes) >= 2:
            current = closes[-1]
            prev = closes[-2]
            change = current - prev
            pct = (change / prev) * 100
            return {'price': round(current, 4), 'change': round(change, 4), 'pct': round(pct, 4)}
        elif len(closes) == 1:
            return {'price': round(closes[0], 4), 'change': 0, 'pct': 0, 'note': 'only_one_bar'}
    except Exception as e:
        return {'error': str(e)}

def yf_chart_retry(symbol):
    """Try range=2d first, fallback to 5d, then 1mo"""
    # Try range=2d
    r = yf_chart(symbol, '2d')
    if 'error' not in r and r.get('note') != 'only_one_bar':
        return r
    # Try range=5d
    r = yf_chart(symbol, '5d')
    if 'error' not in r and r.get('note') != 'only_one_bar':
        return r
    # Try range=1mo
    return yf_chart(symbol, '1mo')

data = {}

# Bonds
bonds = ['^IRX', '^FVX', '^TNX', '^TYX']
for b in bonds:
    data[b] = yf_chart_retry(b)
    time.sleep(0.3)

# Commodities
commodities = {'GC=F': 'gold', 'CL=F': 'crude', 'SI=F': 'silver', 'HG=F': 'copper'}
for sym, name in commodities.items():
    r = yf_chart_retry(sym)
    data[name] = r
    time.sleep(0.3)

# Crypto
crypto = {'BTC-USD': 'btc', 'ETH-USD': 'eth'}
for sym, name in crypto.items():
    data[name] = yf_chart_retry(sym)
    time.sleep(0.3)

# International indices
intl = {
    '^N225': 'nikkei', '^KS11': 'kospi', '^FTSE': 'ftse100',
    '^STOXX50E': 'stoxx50', '^AXJO': 'asx200', '^NSEI': 'nifty50',
    '^GDAXI': 'dax', '^FCHI': 'cac40'
}
for sym, name in intl.items():
    data[name] = yf_chart_retry(sym)
    time.sleep(0.3)

# DXY
data['dxy'] = yf_chart_retry('DX-Y.NYB')

# US Top Gainers
try:
    # Try screener API
    url = 'https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrId=day_gainers&count=10'
    req = urllib.request.Request(url, headers=HEADERS)
    resp = json.loads(urllib.request.urlopen(req, context=ssl_ctx, timeout=10).read())
    data['top_gainers'] = []
    for quote in resp.get('finance', {}).get('result', [{}])[0].get('quotes', []):
        data['top_gainers'].append({
            'symbol': quote.get('symbol', ''),
            'name': quote.get('shortName', quote.get('longName', '')),
            'price': quote.get('regularMarketPrice', 0),
            'pct': quote.get('regularMarketChangePercent', 0)
        })
except Exception as e:
    data['top_gainers'] = [{'error': str(e)}]

with open('/home/hermes_agent/digest/today_yf.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("YF data collected successfully")
for k, v in data.items():
    if isinstance(v, dict) and 'price' in v:
        print(f"  {k}: {v['price']} ({v.get('pct',0):+.2f}%)")
    elif k == 'top_gainers' and isinstance(v, list):
        print(f"  top_gainers: {len(v)} stocks")
