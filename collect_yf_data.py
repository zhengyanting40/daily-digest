#!/usr/bin/env python3
"""Collect YF data: US indices, bonds, commodities, crypto, DXY, forex."""
import json, re, ssl, urllib.request, datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def enc_sym(symbol):
    if symbol.startswith('^'):
        return '%5E' + symbol[1:]
    return symbol.replace('=', '%3D')

def yf_chart(symbol, name, range_val='2d'):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{enc_sym(symbol)}?range={range_val}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read())
        result = data.get('chart',{}).get('result',[{}])[0]
        closes = result.get('indicators',{}).get('quote',[{}])[0].get('close',[])
        timestamps = result.get('timestamp',[])
        # Filter out None values
        closes = [c for c in closes if c is not None]
        if len(closes) < 2:
            # Try longer range
            url2 = f"https://query1.finance.yahoo.com/v8/finance/chart/{enc_sym(symbol)}?range=5d&interval=1d"
            with urllib.request.urlopen(urllib.request.Request(url2, headers={"User-Agent":"Mozilla/5.0"}), timeout=15, context=ctx) as resp2:
                data2 = json.loads(resp2.read())
            result2 = data2.get('chart',{}).get('result',[{}])[0]
            closes = [c for c in result2.get('indicators',{}).get('quote',[{}])[0].get('close',[]) if c is not None]
            timestamps = result2.get('timestamp',[])
            range_val = '5d'
        if len(closes) >= 2:
            price = closes[-1]
            prev = closes[-2]
            pct = (price - prev) / prev * 100 if prev else 0
        elif len(closes) == 1:
            price = closes[0]
            pct = 0
        else:
            return {"name": name, "symbol": symbol, "error": "no data"}
        ts = timestamps[-1] if timestamps else 0
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime('%Y-%m-%d') if ts else ''
        return {"name": name, "symbol": symbol, "price": round(price,2), "pct": round(pct,2), "data_date": dt, "range": range_val}
    except Exception as e:
        return {"name": name, "symbol": symbol, "error": str(e)}

if __name__ == '__main__':
    out = {}
    
    # US indices range=5d
    us_syms = [("^GSPC","S&P 500"),("^IXIC","Nasdaq"),("^DJI","Dow Jones")]
    us_list = []
    for sym, name in us_syms:
        us_list.append(yf_chart(sym, name, '5d'))
    out['us_indices'] = us_list
    
    # International indices range=5d
    intl_syms = [("^N225","日经225"),("^KS11","KOSPI"),("^FTSE","富时100"),("^STOXX50E","斯托克50"),("^AXJO","ASX 200"),("^NSEI","NIFTY 50"),("^GDAXI","DAX"),("^FCHI","CAC")]
    intl_list = []
    for sym, name in intl_syms:
        intl_list.append(yf_chart(sym, name, '5d'))
    out['intl_indices'] = intl_list
    
    # Bonds range=2d fallback 1mo
    bond_syms = [("^IRX","3个月"),("^FVX","5年"),("^TNX","10年"),("^TYX","30年")]
    bond_list = []
    for sym, name in bond_syms:
        d = yf_chart(sym, name, '2d')
        if 'error' in d or d.get('pct') is None:
            d = yf_chart(sym, name, '1mo')
        bond_list.append(d)
    out['bonds'] = bond_list
    
    # Commodities range=5d
    comm_syms = [("GC=F","黄金"),("CL=F","原油"),("SI=F","白银"),("HG=F","铜")]
    comm_list = []
    for sym, name in comm_syms:
        comm_list.append(yf_chart(sym, name, '5d'))
    out['commodities'] = comm_list
    
    # Crypto range=2d
    crypto_syms = [("BTC-USD","BTC"),("ETH-USD","ETH")]
    crypto_list = []
    for sym, name in crypto_syms:
        crypto_list.append(yf_chart(sym, name, '2d'))
    out['crypto'] = crypto_list
    
    # DXY range=5d
    dxy = yf_chart("DX-Y.NYB", "DXY", '5d')
    out['dxy'] = dxy
    
    # Forex range=2d
    fx_syms = [("EURUSD=X","EUR/USD"),("USDJPY=X","USD/JPY"),("CNY=X","USD/CNY"),("USDHKD=X","USD/HKD")]
    fx_list = []
    for sym, name in fx_syms:
        fx_list.append(yf_chart(sym, name, '2d'))
    out['forex'] = fx_list
    
    with open('/home/hermes_agent/digest/today_yf.json','w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    
    # Count success
    ok = sum(1 for v in __import__('itertools').chain(us_list,intl_list,bond_list,comm_list,crypto_list,fx_list,[dxy]) if 'error' not in v)
    total = len(us_list)+len(intl_list)+len(bond_list)+len(comm_list)+len(crypto_list)+len(fx_list)+1
    print(f"YF data saved. {ok}/{total} ok")
