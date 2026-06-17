#!/usr/bin/env python3
"""Fix DXY, commodities, gold (need longer range for proper prev_close)."""
import json, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

def fetch_yf_chart(symbol, range_d='5d'):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_d}&interval=1d'
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        timestamps = result['timestamp']
        valid = [(ts, c) for ts, c in zip(timestamps, closes) if c is not None]
        if len(valid) >= 2:
            prev_close = valid[-2][1]
            last_close = valid[-1][1]
            pct = ((last_close - prev_close) / prev_close) * 100
            return {'price': round(last_close, 4), 'prev_close': round(prev_close, 4), 'percent': round(pct, 2)}
        elif len(valid) == 1:
            return {'price': round(valid[-1][1], 4), 'prev_close': 0, 'percent': 0}
        return {'error': 'no data'}
    except Exception as e:
        return {'error': str(e)}

# Fix these with 5d range
fixes = {
    'DX-Y.NYB': 'DXY',
    'GC=F': '黄金',
    'CL=F': '原油',
    'SI=F': '白银',
    'HG=F': '铜',
}
results = {}
for sym, name in fixes.items():
    results[f'commodity_{sym}'] = fetch_yf_chart(sym, '5d')
    print(f"  {name}: {results[f'commodity_{sym}']}")

# US Top Gainers
try:
    url = 'https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=10&scrId=day_gainers&formRegion=US'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    screener = json.loads(resp.read().decode())
    gainers = []
    for item in screener.get('finance', {}).get('result', [{}])[0].get('quotes', []):
        gainers.append({
            'symbol': item.get('symbol', ''),
            'name': item.get('shortName', item.get('longName', '')),
            'price': item.get('regularMarketPrice', 0),
            'changePercent': item.get('regularMarketChangePercent', 0),
        })
    results['top_gainers'] = gainers
    print(f"  Top gainers: {len(gainers)} stocks")
except Exception as e:
    results['top_gainers'] = {'error': str(e)}
    print(f"  Top gainers error: {e}")

with open('/home/hermes_agent/digest/today_yf_fix.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fix data saved")
