#!/usr/bin/env python3
"""Re-verify treasury yields from YF."""
import urllib.request, json, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {'User-Agent': 'Mozilla/5.0'}

for name, sym in [('3M','%5EIRX'),('5Y','%5EFVX'),('10Y','%5ETNX'),('30Y','%5ETYX')]:
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + sym + '?range=5d&interval=1d'
    req = urllib.request.Request(url, headers=ua)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
        d = json.loads(r.read())
        meta = d['chart']['result'][0]['meta']
        price = meta.get('regularMarketPrice')
        prev = meta.get('chartPreviousClose')
        if price and prev:
            chg = ((price - prev) / prev) * 100
            print(name + ': price=' + str(price) + ' prev=' + str(prev) + ' chg=' + format(chg, '+.2f') + '%')
        else:
            print(name + ': price=' + str(price) + ' prev=' + str(prev))
