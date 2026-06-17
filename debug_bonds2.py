#!/usr/bin/env python3
"""Debug YF bond data with range=1mo"""
import json, urllib.request, ssl
from datetime import datetime

ssl_ctx = ssl.create_default_context()

for sym in ['^TNX', '^IRX', '^FVX', '^TYX']:
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1mo&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as r:
            data = json.loads(r.read())
        ts = data['chart']['result'][0]['timestamp']
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        valid = [(t,c) for t,c in zip(ts,closes) if c is not None]
        print(f'{sym}: {len(valid)} valid closes')
        for t, c in valid[-5:]:
            print(f'  {datetime.fromtimestamp(t).strftime("%Y-%m-%d")} close={round(c,4)}')
        if len(valid) >= 2:
            prev, curr = valid[-2][1], valid[-1][1]
            chg = curr - prev
            pct = (chg/prev)*100 if prev else 0
            print(f'  Change: {round(chg,4)} ({round(pct,2)}%)')
    except Exception as e:
        print(f'{sym}: error {e}')
