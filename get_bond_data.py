import urllib.request, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def fetch_prev_close(symbol, name):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3d&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            r = data['chart']['result'][0]
            quotes = r['indicators']['quote'][0]['close']
            timestamps = r['timestamp']
            closes = [(i, q) for i, q in enumerate(quotes) if q is not None]
            print(f'{name} ({symbol}):')
            import datetime
            for idx, val in closes:
                dt = datetime.datetime.fromtimestamp(timestamps[idx])
                print(f'  [{dt.strftime("%Y-%m-%d")}] {val}')
            if len(closes) >= 2:
                today = closes[-1][1]
                prev = closes[-2][1]
                pct = round(((today - prev) / prev) * 100, 2)
                print(f'  Change: {pct}%')
                return today, pct
            elif len(closes) == 1:
                return closes[-1][1], None
    except Exception as e:
        print(f'{name}: ERROR {e}')
    return None, None

# CNBC values (from latest fetch)
cnbc = {
    '^IRX': ('3月期美债', 3.727),
    '^FVX': ('5年期美债', 4.193),
    '^TNX': ('10年期美债', 4.475),
    '^TYX': ('30年期美债', 4.981),
}

print('=== YF previous closes ===')
for sym, (name, cnbc_val) in cnbc.items():
    yf_today, yf_pct = fetch_prev_close(sym, name)
    print(f'  CNBC value: {cnbc_val}%')
    print(f'  YF today: {yf_today}')
    print()

# Now also check commodities from YF
print('=== Commodities from YF ===')
com_symbols = {
    'GC=F': '黄金',
    'CL=F': '原油',
    'SI=F': '白银',
    'HG=F': '铜',
    'BTC-USD': 'BTC',
    'ETH-USD': 'ETH',
}
for sym, name in com_symbols.items():
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=3d&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            r = data['chart']['result'][0]
            quotes = r['indicators']['quote'][0]['close']
            timestamps = r['timestamp']
            closes = [(i, q) for i, q in enumerate(quotes) if q is not None]
            if len(closes) >= 2:
                today = closes[-1][1]
                prev = closes[-2][1]
                pct = round(((today - prev) / prev) * 100, 2)
                import datetime
                dt_today = datetime.datetime.fromtimestamp(timestamps[closes[-1][0]])
                print(f'{name}: ${today:.2f} ({pct:+.2f}%) [{dt_today.strftime("%Y-%m-%d")}]')
            elif len(closes) == 1:
                print(f'{name}: ${closes[-1][1]:.2f}')
    except Exception as e:
        print(f'{name}: ERROR {str(e)[:60]}')
