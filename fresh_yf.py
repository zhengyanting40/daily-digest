#!/usr/bin/env python3
"""Fresh data collection for all markets via YF v8 chart API."""
import urllib.request, json, ssl, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {'User-Agent': 'Mozilla/5.0'}

symbols = {
    'HSI': '%5EHSI', 'SH': '000001.SS', 'SZ': '399001.SZ', 'CYB': '399006.SZ',
    'SPX': '%5EGSPC', 'IXIC': '%5EIXIC', 'DJI': '%5EDJI',
    'N225': '%5EN225', 'KS11': '%5EKS11', 'FTSE': '%5EFTSE', 'DAX': '%5EGDAXI', 'CAC': '%5EFCHI',
    'IRX': '%5EIRX', 'FVX': '%5EFVX', 'TNX': '%5ETNX', 'TYX': '%5ETYX',
    'GC': 'GC%3DF', 'CL': 'CL%3DF', 'SI': 'SI%3DF', 'HG': 'HG%3DF',
    'BTC': 'BTC-USD', 'ETH': 'ETH-USD',
    'DXY': 'DX-Y.NYB', 'EURUSD': 'EURUSD%3DX',
}

results = {}
for name, sym in symbols.items():
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + sym + '?range=5d&interval=1d'
    try:
        req = urllib.request.Request(url, headers=ua)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            d = json.loads(r.read())
            meta = d['chart']['result'][0]['meta']
            results[name] = {
                'price': meta.get('regularMarketPrice'),
                'prev_close': meta.get('chartPreviousClose'),
                'currency': meta.get('currency', 'USD')
            }
    except Exception as e:
        results[name] = {'error': str(e)[:60]}

out = '/home/hermes_agent/digest/yf_data.json'
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

for name in sorted(results.keys()):
    d = results[name]
    if 'error' in d:
        print('X ' + name + ': ' + d['error'])
    else:
        p, pc = d['price'], d['prev_close']
        if p and pc and pc > 0:
            chg = ((p - pc) / pc) * 100
            print('OK ' + name + ': ' + str(p) + ' (' + format(chg, '+.2f') + '%)')
        else:
            print('OK ' + name + ': ' + str(p))
