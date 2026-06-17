#!/usr/bin/env python3
"""Collect YF data - fixed bond handling with range=5d"""
import json, urllib.request, ssl

ssl_ctx = ssl.create_default_context()
results = {}

def yf_chart(symbol, range_='2d'):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_}&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as r:
            data = json.loads(r.read())
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        if len(closes) >= 2:
            prev, curr = closes[-2], closes[-1]
            chg = curr - prev
            pct = (chg / prev) * 100 if prev else 0
            return {'price': round(curr, 4), 'change': round(chg, 4), 'pct': round(pct, 2)}
        elif len(closes) == 1:
            return {'price': round(closes[0], 4), 'change': 0, 'pct': 0}
        return {'price': None, 'change': None, 'pct': None}
    except Exception as e:
        return {'error': str(e)}

# Bonds - try 2d first, fallback to 5d
bonds = {'^IRX': 'US3M', '^FVX': 'US5Y', '^TNX': 'US10Y', '^TYX': 'US30Y'}
for sym, name in bonds.items():
    d = yf_chart(sym, '2d')
    if d.get('change') is None:
        d = yf_chart(sym, '5d')
    results[name] = d

# Intl indices (range=5d for weekend gaps)
intl = {'^N225': 'N225', '^KS11': 'KS11', '^FTSE': 'FTSE', '^STOXX50E': 'STOXX50',
        '^AXJO': 'AXJO', '^NSEI': 'NSEI', '^GDAXI': 'GDAXI', '^FCHI': 'FCHI'}
for sym, name in intl.items():
    results[name] = yf_chart(sym, '5d')

# Commodities (range=5d)
commods = {'GC=F': 'GOLD', 'CL=F': 'WTI', 'SI=F': 'SILVER', 'HG=F': 'COPPER'}
for sym, name in commods.items():
    results[name] = yf_chart(sym, '5d')

# Crypto (range=2d)
crypto = {'BTC-USD': 'BTC', 'ETH-USD': 'ETH'}
for sym, name in crypto.items():
    results[name] = yf_chart(sym, '2d')

# DXY (range=5d)
results['DXY'] = yf_chart('DX-Y.NYB', '5d')

# US Top Gainers - try GET approach instead of POST
try:
    import urllib.parse
    url = 'https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=day_gainers&offset=0&count=10'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as r:
        gainers_data = json.loads(r.read())
    gainers = []
    for item in gainers_data.get('finance',{}).get('result',[{}])[0].get('quotes',[]):
        gainers.append({
            'symbol': item.get('symbol',''),
            'name': item.get('shortName','') or item.get('longName',''),
            'price': round(item.get('regularMarketPrice',0), 2)
        })
    results['TOP_GAINERS'] = gainers[:10]
except Exception as e:
    results['TOP_GAINERS'] = {'error': str(e)}

with open('/home/hermes_agent/digest/today_yf.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Print key items
for k in ['US3M','US5Y','US10Y','US30Y','DXY','GOLD','WTI','BTC']:
    v = results.get(k,{})
    print(f'{k}: price={v.get("price")}, chg={v.get("change")}, pct={v.get("pct")}')
