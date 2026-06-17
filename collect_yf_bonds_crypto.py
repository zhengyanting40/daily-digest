import urllib.request, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Symbols for US bonds, commodities, crypto
symbols = {
    'bonds': {'^IRX': '3月期美债', '^FVX': '5年期美债', '^TNX': '10年期美债', '^TYX': '30年期美债'},
    'commodities': {'GC=F': '黄金', 'CL=F': '原油', 'SI=F': '白银', 'HG=F': '铜'},
    'crypto': {'BTC-USD': 'BTC', 'ETH-USD': 'ETH'},
}

results = {'bonds': {}, 'commodities': {}, 'crypto': {}}

for category, items in symbols.items():
    for sym, name in items.items():
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym, safe="")}?range=5d&interval=1d'
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
                data = json.loads(resp.read().decode())
                meta = data['chart']['result'][0]['meta']
                quotes = data['chart']['result'][0]['indicators']['quote'][0]
                if meta.get('previousClose') and quotes.get('close') and quotes['close'][-1]:
                    prev = meta['previousClose']
                    cur = quotes['close'][-1]
                elif meta.get('regularMarketPrice') and meta.get('previousClose'):
                    cur = meta['regularMarketPrice']
                    prev = meta['previousClose']
                elif meta.get('chartPreviousClose') and quotes.get('close') and quotes['close'][-1]:
                    prev = meta['chartPreviousClose']
                    cur = quotes['close'][-1]
                else:
                    continue
                
                chg = cur - prev
                pct = (chg / prev) * 100
                results[category][sym] = {
                    'name': name,
                    'price': round(cur, 4),
                    'change': round(chg, 4),
                    'percent': round(pct, 2)
                }
        except Exception as e:
            results[category][sym] = {'name': name, 'error': str(e)[:80]}

# US Top Gainers
try:
    url = 'https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&lang=en-US&region=US&scrIds=day_gainers&count=10'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode())
        gainers = []
        for item in data['finance']['result'][0]['quotes']:
            name = item.get('shortName', item.get('longName', ''))
            sym = item.get('symbol', '')
            price = item.get('regularMarketPrice', {}).get('raw', 0)
            pct = item.get('regularMarketChangePercent', {}).get('raw', 0)
            gainers.append({'symbol': sym, 'name': name, 'price': round(price, 2), 'percent': round(pct, 2)})
        results['gainers'] = gainers
except Exception as e:
    results['gainers'] = {'error': str(e)[:80]}

print(json.dumps(results, ensure_ascii=False))
