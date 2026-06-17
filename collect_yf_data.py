#!/usr/bin/env python3
"""Collect YF data: bonds, intl indices, commodities, crypto, DXY, top gainers"""
import json, urllib.request, ssl
from datetime import datetime

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
        return {'price': round(closes[-1], 4) if closes else None, 'change': None, 'pct': None}
    except Exception as e:
        return {'error': str(e)}

# Bonds (range=2d)
bonds = ['^IRX', '^FVX', '^TNX', '^TYX']
bond_names = {'^IRX': 'US3M', '^FVX': 'US5Y', '^TNX': 'US10Y', '^TYX': 'US30Y'}
for sym in bonds:
    results[bond_names[sym]] = yf_chart(sym, '2d')

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

# US Top Gainers
try:
    url = 'https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved'
    payload = {"offset":0,"count":10,"scrIds":["day_gainers"]}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as r:
        gainers_data = json.loads(r.read())
    gainers = []
    for item in gainers_data.get('finance',{}).get('result',[{}])[0].get('quotes',[]):
        gainers.append({
            'symbol': item.get('symbol',''),
            'name': item.get('shortName','') or item.get('longName',''),
            'price': round(item.get('regularMarketPrice',0), 2),
            'pct': round(item.get('regularMarketChangePercent',0), 2)
        })
    results['TOP_GAINERS'] = gainers[:10]
except Exception as e:
    # Try most_actives as fallback
    try:
        payload = {"offset":0,"count":10,"scrIds":["most_actives"]}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as r:
            gainers_data = json.loads(r.read())
        gainers = []
        for item in gainers_data.get('finance',{}).get('result',[{}])[0].get('quotes',[]):
            gainers.append({
                'symbol': item.get('symbol',''),
                'name': item.get('shortName','') or item.get('longName',''),
                'price': round(item.get('regularMarketPrice',0), 2),
                'pct': round(item.get('regularMarketChangePercent',0), 2)
            })
        results['TOP_GAINERS'] = gainers[:10]
    except Exception as e2:
        results['TOP_GAINERS'] = {'error': f'primary: {e}, fallback: {e2}'}

with open('/home/hermes_agent/digest/today_yf.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(json.dumps(results, ensure_ascii=False, indent=2)[:500])
