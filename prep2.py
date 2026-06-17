#!/usr/bin/env python3
import json

with open('/home/hermes_agent/digest/html_data.json') as f:
    d = json.load(f)

with open('/home/hermes_agent/digest/yf_data.json') as f:
    yf = json.load(f)

gold_pct = ((yf['Gold']['price']-yf['Gold']['prev_close'])/yf['Gold']['prev_close'])*100
btc_pct = ((yf['BTC']['price']-yf['BTC']['prev_close'])/yf['BTC']['prev_close'])*100
eth_pct = ((yf['ETH']['price']-yf['ETH']['prev_close'])/yf['ETH']['prev_close'])*100
silver_pct = ((yf['Silver']['price']-yf['Silver']['prev_close'])/yf['Silver']['prev_close'])*100
dxy_pct = ((yf['DXY']['price']-yf['DXY']['prev_close'])/yf['DXY']['prev_close'])*100
dax_pct = ((yf['DAX']['price']-yf['DAX']['prev_close'])/yf['DAX']['prev_close'])*100
cac_pct = ((yf['CAC40']['price']-yf['CAC40']['prev_close'])/yf['CAC40']['prev_close'])*100

summary = '全球股市遭遇重挫，美股三大指数大幅下跌（纳指-4.18%、标普-2.64%），科技股领跌。A股普遍走弱（上证-0.74%、深证-2.21%、创业板-3.20%），港股恒指跌1.15%。国际指数全线回落（日经-0.52%、FTSE-0.40%、DAX-{:.2f}%），仅CAC40小幅收涨+{:.2f}%。美债收益率小幅攀升，10年期升至{:.2f}%，30年期升至{:.2f}%。美元强势反弹（DXY+{:.2f}%），黄金大跌{:.2f}%至$4,365，白银暴跌{:.2f}%。加密货币市场遭遇血洗，BTC跌{:.2f}%至$60,601，ETH暴跌{:.2f}%至$1,559。'.format(
    abs(dax_pct), abs(cac_pct),
    yf['10Y Yield']['price'], yf['30Y Yield']['price'],
    abs(dxy_pct), abs(gold_pct), abs(silver_pct), abs(btc_pct), abs(eth_pct)
)

html_data = {
    'indices_rows': d['indices_rows'],
    'bond_rows': d['bond_rows'],
    'commodity_rows': d['commodity_rows'],
    'crypto_rows': d['crypto_rows'],
    'news_html': d['news_html'],
    'summary': summary,
}

with open('/home/hermes_agent/digest/html_data2.json', 'w') as f:
    json.dump(html_data, f, ensure_ascii=False)

print('summary: ' + summary[:80] + '...')
print('data ready')
