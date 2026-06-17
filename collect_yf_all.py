#!/usr/bin/env python3
"""Collect all market data from YF v8 chart API (no MCP needed)."""
import urllib.request, json, ssl, os, time

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}

# All symbols in one batch
symbols = {
    # HK
    'HSI': '%5EHSI',
    # A-share
    'SH': '000001.SS',
    'SZ': '399001.SZ',
    'CYB': '399006.SZ',
    # US
    'SPX': '%5EGSPC',
    'IXIC': '%5EIXIC',
    'DJI': '%5EDJI',
    # International
    'N225': '%5EN225',
    'KS11': '%5EKS11',
    'FTSE': '%5EFTSE',
    'DAX': '%5EGDAXI',
    'CAC': '%5EFCHI',
    # Treasury
    'IRX': '%5EIRX',
    'FVX': '%5EFVX',
    'TNX': '%5ETNX',
    'TYX': '%5ETYX',
    # Commodities
    'GC': 'GC%3DF',
    'CL': 'CL%3DF',
    'SI': 'SI%3DF',
    'HG': 'HG%3DF',
    # Crypto
    'BTC': 'BTC-USD',
    'ETH': 'ETH-USD',
    # Forex
    'DXY': 'DX-Y.NYB',
    'EURUSD': 'EURUSD%3DX',
}

results = {}
for name, sym in symbols.items():
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + sym + '?range=5d&interval=1d'
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as r:
            d = json.loads(r.read())
            meta = d['chart']['result'][0]['meta']
            price = meta.get('regularMarketPrice')
            prev_close = meta.get('chartPreviousClose')
            currency = meta.get('currency', 'USD')
            results[name] = {'price': price, 'prev_close': prev_close, 'currency': currency}
    except Exception as e:
        results[name] = {'error': str(e)[:60]}

out = '/home/hermes_agent/digest/yf_data.json'
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

for name, data in sorted(results.items()):
    if 'error' in data:
        print('X ' + name + ': ' + data['error'])
    else:
        p = data['price']
        pc = data['prev_close']
        if p and pc and pc > 0:
            chg = ((p - pc) / pc) * 100
            print('OK ' + name + ': ' + str(p) + ' (' + format(chg, '+.2f') + '%)')
        else:
            print('OK ' + name + ': ' + str(p))
