#!/usr/bin/env python3
"""Collect YF data: US indices, intl indices, bonds, commodities, crypto, DXY, forex, US top gainers"""
import json, ssl, urllib.request, datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def enc_sym(symbol):
    if symbol.startswith('^'):
        return '%5E' + symbol[1:]
    return symbol.replace('=', '%3D')

def fetch_yf(symbol, rng='2d'):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{enc_sym(symbol)}?range={rng}&interval=1d"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        data = json.loads(r.read().decode('utf-8'))
    res = data['chart']['result'][0]
    closes = [c for c in res['indicators']['quote'][0]['close'] if c is not None]
    ts = res.get('timestamp', [])
    meta = res.get('meta', {})
    return closes, ts, meta

def get_quote(symbol, rng='2d', name='', nd=2):
    """Return dict with price/pct/data_date. Try rng, fallback to 1mo/5d."""
    closes, ts, meta = [], [], {}
    for attempt_rng in [rng, '1mo']:
        try:
            closes, ts, meta = fetch_yf(symbol, attempt_rng)
            if len(closes) >= 2:
                break
        except Exception:
            continue
    item = {'symbol': symbol, 'name': name}
    if len(closes) >= 2:
        price = closes[-1]
        prev = closes[-2]
        pct = (price - prev) / prev * 100 if prev else 0
        item['price'] = round(price, nd)
        item['pct'] = round(pct, 2)
        item['prev'] = round(prev, nd)
        if ts:
            item['data_date'] = datetime.datetime.utcfromtimestamp(ts[-1]).strftime('%Y-%m-%d')
    else:
        item['price'] = None
        item['pct'] = None
        item['data_date'] = ''
    return item

out = {}

# US indices (previous trading day close)
us_names = {'%5EGSPC': 'S&P 500', '%5EIXIC': 'NASDAQ', '%5EDJI': '\u9053\u7434\u65af'}
us_indices = {}
for sym, nm in us_names.items():
    us_indices[nm] = get_quote(sym, '5d', nm, 2)
out['us_indices'] = us_indices
print(f"US: {[(k, v.get('price'), v.get('pct')) for k, v in us_indices.items()]}")

# International indices
intl_map = {'%5EN225': '\u65e5\u7ecf225', '%5EKS11': 'KOSPI', '%5EFTSE': '\u5bcc\u65f6100',
            '%5ESTOXX50E': '\u65af\u6258\u514b50', '%5EAXJO': 'ASX 200', '%5ENSEI': 'NIFTY 50',
            '%5EGDAXI': 'DAX', '%5EFCHI': 'CAC'}
intl_indices = {}
for sym, nm in intl_map.items():
    intl_indices[nm] = get_quote(sym, '5d', nm, 2)
out['intl_indices'] = intl_indices
print(f"Intl: {[(k, v.get('price'), v.get('pct')) for k, v in intl_indices.items()]}")

# Bonds: value from CNBC (preferred), pct from YF
bond_map = {'%5EIRX': ('3\u4e2a\u6708', 'US3M'), '%5EFVX': ('5\u5e74', 'US5Y'),
            '%5ETNX': ('10\u5e74', 'US10Y'), '%5ETYX': ('30\u5e74', 'US30Y')}
bonds = {}
for sym, (nm, cnbc_sym) in bond_map.items():
    q = get_quote(sym, '2d', nm, 4)
    yval = q.get('price')
    # CNBC yield value
    cnbc_val = None
    try:
        curl = f"https://www.cnbc.com/quotes/{cnbc_sym}"
        req = urllib.request.Request(curl, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            ch = r.read().decode('utf-8', errors='replace')
        import re
        m = re.search(rf'{cnbc_sym}.*?(\d+\.\d+)%', ch)
        if m:
            cnbc_val = float(m.group(1))
    except Exception:
        pass
    val = cnbc_val if cnbc_val else (yval if yval else None)
    bonds[nm] = {'price': val, 'pct': q.get('pct'), 'data_date': q.get('data_date', ''),
                 'cnbc': cnbc_val, 'yf': yval}
out['bonds'] = bonds
print(f"Bonds: {[(k, v['price'], v['pct']) for k, v in bonds.items()]}")

# Commodities
com_map = {'GC=F': '\u9ec4\u91d1', 'CL=F': '\u539f\u6cb9', 'SI=F': '\u767d\u94f6', 'HG=F': '\u94dc'}
commodities = {}
for sym, nm in com_map.items():
    commodities[nm] = get_quote(sym, '5d', nm, 2)
out['commodities'] = commodities
print(f"Commodities: {[(k, v.get('price'), v.get('pct')) for k, v in commodities.items()]}")

# Crypto
crypto = {}
for sym, nm in [('BTC-USD', 'BTC'), ('ETH-USD', 'ETH')]:
    crypto[nm] = get_quote(sym, '5d', nm, 2)
out['crypto'] = crypto
print(f"Crypto: {[(k, v.get('price'), v.get('pct')) for k, v in crypto.items()]}")

# DXY
dxy = get_quote('DX-Y.NYB', '5d', 'DXY', 2)
out['dxy'] = dxy
print(f"DXY: {dxy}")

# Forex
fx_map = {'EURUSD=X': 'EUR/USD', 'USDJPY=X': 'USD/JPY', 'CNY=X': 'USD/CNY', 'USDHKD=X': 'USD/HKD'}
forex = {}
for sym, nm in fx_map.items():
    forex[nm] = get_quote(sym, '2d', nm, 4)
out['forex'] = forex
print(f"Forex: {[(k, v.get('price'), v.get('pct')) for k, v in forex.items()]}")

# US Top Gainers (best effort)
top_gainers = []
try:
    screener_url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=day_gainers&count=15"
    req = urllib.request.Request(screener_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        sdata = json.loads(r.read().decode('utf-8'))
    for q in sdata.get('finance', {}).get('result', [{}])[0].get('quotes', []):
        top_gainers.append({
            'name': q.get('shortName') or q.get('longName') or q.get('symbol', ''),
            'symbol': q.get('symbol', ''),
            'price': q.get('regularMarketPrice'),
            'pct': q.get('regularMarketChangePercent'),
        })
except Exception as e:
    print(f"Top gainers failed: {e}")
out['top_gainers'] = top_gainers
print(f"Top gainers: {len(top_gainers)}")

with open('/home/hermes_agent/digest/today_yf.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)
print("YF_DONE")
