#!/usr/bin/env python3
"""采集美债/商品/加密/国际指数数据（非Yahoo Finance源）"""
import requests, re, json, os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

data = {}

# 1. 美债 - 新浪财经海外行情
print("=== 美债 ===")
for symbol in ['US10Y', 'US02Y', 'US05Y', 'US30Y']:
    try:
        r = requests.get(f'https://hq.sinajs.cn/list=gb_{symbol}', 
            headers={**headers, 'Referer': 'https://finance.sina.com.cn'}, timeout=10)
        r.encoding = 'gb2312'
        # Format: var hq_str_gb_US10Y="名称,最新价,涨跌幅,...
        parts = r.text.split('="')
        if len(parts) > 1:
            vals = parts[1].split(',')
            name = vals[0] if len(vals) > 0 else symbol
            price = vals[1] if len(vals) > 1 else '?'
            chg_pct = vals[3] if len(vals) > 3 else '?'
            data[f'bond_{symbol}'] = {'name': name, 'price': price, 'pct': chg_pct}
            print(f"  {symbol}: {price} ({chg_pct})")
    except Exception as e:
        print(f"  {symbol}: {e}")

# 2. 商品 - 新浪期货行情
print("\n=== 商品 ===")
commodities = {'gold': 'hf_CL', 'oil': 'hf_NM', 'silver': 'hf_SI', 'copper': 'hf_HG'}
for name, symbol in commodities.items():
    try:
        r = requests.get(f'https://hq.sinajs.cn/list=nf_{symbol}',
            headers={**headers, 'Referer': 'https://finance.sina.com.cn'}, timeout=10)
        r.encoding = 'gb2312'
        parts = r.text.split('="')
        if len(parts) > 1:
            vals = parts[1].split(',')
            # 格式: 名称,开盘,最高,最低,收盘,涨跌,涨跌幅,...
            price = vals[3] if len(vals) > 3 else '?'
            chg_pct = vals[6] if len(vals) > 6 else '?'
            data[f'commodity_{name}'] = {'name': vals[0], 'price': price, 'pct': chg_pct}
            print(f"  {name}: {price} ({chg_pct})")
    except Exception as e:
        print(f"  {name}: {e}")

# 3. 国际指数 - 新浪港股指数
print("\n=== 国际指数 ===")
indices = {'nikkei': 'hq_ja_5051', 'kospi': 'hq_ko_2019', 'ftse': 'hq_en_1019', 'dax': 'hq_en_1021', 'cac': 'hq_en_1020'}
for name, symbol in indices.items():
    try:
        r = requests.get(f'https://hq.sinajs.cn/list={symbol}',
            headers={**headers, 'Referer': 'https://finance.sina.com.cn'}, timeout=10)
        r.encoding = 'gb2312'
        parts = r.text.split('="')
        if len(parts) > 1:
            vals = parts[1].split(',')
            price = vals[1] if len(vals) > 1 else '?'
            chg_pct = vals[4] if len(vals) > 4 else '?'
            data[f'index_{name}'] = {'name': vals[0], 'price': price, 'pct': chg_pct}
            print(f"  {name}: {price} ({chg_pct})")
    except Exception as e:
        print(f"  {name}: {e}")

# 4. 加密货币
print("\n=== 加密 ===")
for coin in ['btc', 'eth']:
    try:
        r = requests.get(f'https://hq.sinajs.cn/list=hl_{coin}usd',
            headers={**headers, 'Referer': 'https://finance.sina.com.cn'}, timeout=10)
        r.encoding = 'gb2312'
        parts = r.text.split('="')
        if len(parts) > 1:
            vals = parts[1].split(',')
            price = vals[1] if len(vals) > 1 else '?'
            chg_pct = vals[3] if len(vals) > 3 else '?'
            data[f'crypto_{coin}'] = {'name': vals[0], 'price': price, 'pct': chg_pct}
            print(f"  {coin}: {price} ({chg_pct})")
    except Exception as e:
        print(f"  {coin}: {e}")

# 保存
os.makedirs('/home/hermes_agent/digest', exist_ok=True)
with open('/home/hermes_agent/digest/extra_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\n保存 {len(data)} 条数据到 extra_data.json")
