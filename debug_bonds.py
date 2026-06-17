#!/usr/bin/env python3
"""Debug YF bond data to see raw response"""
import json, urllib.request, ssl

ssl_ctx = ssl.create_default_context()

for sym in ['^TNX', '^IRX', '^FVX', '^TYX']:
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=2d&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as r:
            data = json.loads(r.read())
        ts = data['chart']['result'][0]['timestamp']
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        print(f'{sym}: {len(closes)} closes')
        for i, (t, c) in enumerate(zip(ts, closes)):
            from datetime import datetime
            print(f'  {i}: {datetime.fromtimestamp(t).strftime("%Y-%m-%d")} close={c}')
    except Exception as e:
        print(f'{sym}: error {e}')
