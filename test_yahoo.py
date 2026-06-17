#!/usr/bin/env python3
"""Test Yahoo Finance API access"""
import urllib.request, json, ssl, sys

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Test each endpoint
symbols = {
    '美债10Y': '%5ETNX',
    '日经': '%5EN225',
    '黄金': 'GC%3DF',
    'BTC': 'BTC-USD',
    '原油': 'CL%3DF',
}

for name, sym in symbols.items():
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1d&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            meta = data['chart']['result'][0]['meta']
            price = meta.get('regularMarketPrice', '?')
            prev = meta.get('chartPreviousClose', '?')
            print(f'✅ {name}: price={price}, prevClose={prev}')
    except Exception as e:
        print(f'❌ {name}: {type(e).__name__}: {str(e)[:60]}')
