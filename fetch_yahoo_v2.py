#!/usr/bin/env python3
"""采集Yahoo Finance数据：美债/国际指数/商品/加密"""
import urllib.request, json, ssl, os

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch(symbol):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        result = data['chart']['result'][0]
        meta = result['meta']
        price = meta.get('regularMarketPrice') or meta.get('chartPreviousClose', 0)
        prev = meta.get('chartPreviousClose', 0)
        chg = round(price - prev, 2)
        pct = round(chg / prev * 100, 2) if prev else 0
        return {'price': price, 'prev': prev, 'chg': chg, 'pct': pct}

data = {}

# 美债
print("=== 美债 ===")
for sym, name in [('%5EIRX', '3个月'), ('%5EFVX', '5年'), ('%5ETNX', '10年'), ('%5ETYX', '30年')]:
    d = fetch(sym)
    data[f'bond_{name}'] = d
    print(f"  {name}: {d['price']:.3f}% ({d['pct']:+.2f}%)")

# 国际指数
print("\n=== 国际指数 ===")
for sym, name in [('%5EN225', '日经225'), ('%5EKS11', 'KOSPI'), ('%5EFTSE', '富时100'),
                   ('%5ESTOXX50E', '欧洲斯托克50'), ('%5EGDAXI', '德国DAX'),
                   ('%5EFCHI', '法国CAC')]:
    d = fetch(sym)
    data[f'index_{name}'] = d
    print(f"  {name}: {d['price']:.2f} ({d['pct']:+.2f}%)")

# 商品
print("\n=== 商品 ===")
for sym, name in [('GC%3DF', '黄金'), ('CL%3DF', '原油'), ('SI%3DF', '白银'), ('HG%3DF', '铜')]:
    d = fetch(sym)
    data[f'commodity_{name}'] = d
    print(f"  {name}: {d['price']:.2f} ({d['pct']:+.2f}%)")

# 加密
print("\n=== 加密 ===")
for sym, name in [('BTC-USD', 'BTC'), ('ETH-USD', 'ETH')]:
    d = fetch(sym)
    data[f'crypto_{name}'] = d
    print(f"  {name}: {d['price']:.2f} ({d['pct']:+.2f}%)")

# 保存
os.makedirs('/home/hermes_agent/digest', exist_ok=True)
with open('/home/hermes_agent/digest/yahoo_latest.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\n已保存到 yahoo_latest.json")
