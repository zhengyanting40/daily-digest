import urllib.request, json, ssl, datetime

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def fetch_bond(symbol, name):
    # Use 2d range to get exactly last 2 trading days
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            r = data['chart']['result'][0]
            quotes = r['indicators']['quote'][0]['close']
            timestamps = r['timestamp']
            closes = [q for q in quotes if q is not None]
            print(f'\n=== {name} ({symbol}) ===')
            print(f'  All closes: {closes}')
            for i, ts in enumerate(timestamps):
                dt = datetime.datetime.fromtimestamp(ts)
                print(f'  [{dt.strftime("%Y-%m-%d")}] close={quotes[i]}')
            if len(closes) >= 2:
                today_c = closes[-1]
                yest_c = closes[-2]
                pct = round(((today_c - yest_c) / yest_c) * 100, 2)
                print(f'  Today: {today_c}, Yesterday: {yest_c}, Change: {pct}%')
            elif len(closes) >= 1:
                print(f'  Only 1 data point: {closes[0]}')
            else:
                print(f'  No data points')
            return closes
    except Exception as e:
        print(f'  ERROR: {e}')
        return None

# Fetch all bonds
fetch_bond('^IRX', '3月期美债')
fetch_bond('^FVX', '5年期美债')
fetch_bond('^TNX', '10年期美债')
fetch_bond('^TYX', '30年期美债')
