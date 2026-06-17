#!/usr/bin/env python3
import json

with open('/home/hermes_agent/digest/yf_data.json') as f:
    yf = json.load(f)

with open('/home/hermes_agent/digest/news_data.json') as f:
    caixin_good = json.load(f)['caixin'][:8]

with open('/home/hermes_agent/digest/people_extra.json') as f:
    pe = json.load(f)
    people_good = [it for it in pe if len(it[0]) >= 8][:8]

with open('/home/hermes_agent/digest/eastmoney_extra.json') as f:
    ea = json.load(f)
    east_good = [it for it in ea if len(it[0]) >= 8 and '指数' not in it[0]][:8]

yf_pct = {}
for k, v in yf.items():
    if v.get('price') and v.get('prev_close') and v['prev_close'] > 0:
        yf_pct[k] = ((v['price'] - v['prev_close']) / v['prev_close']) * 100
    else:
        yf_pct[k] = None

ud = lambda v: '' if v is None or v == 0 else ('ud_up' if v > 0 else 'ud_down')
cl = lambda v: '#F85149' if v and v > 0 else ('#3FB950' if v and v < 0 else '')
ps = lambda v: '---' if v is None or v == 0 else '{:.2f}%'.format(abs(v))
vs = lambda v, n=2: '---' if v is None else '{:.{n}f}'.format(v, n=n)
ar = lambda v: ('<span style="color:#F85149">&#9650;</span>' if v and v > 0 else '<span style="color:#3FB950">&#9660;</span>') if v else ''

# Build news section
news_html = ''
for sname, stag, sclass, items in [
    ('caixin', 'caixin', '#7ee787', caixin_good),
    ('people', 'people', '#f97583', people_good),
    ('eastmoney', 'eastmoney', '#79c0ff', east_good),
]:
    news_html += '<div style="margin-bottom:10px"><div style="font-size:14px;color:#8b949e;margin-bottom:4px">' + sname + '</div>\n'
    for t, u in items:
        badge = '<span style="display:inline-block;background:' + sclass + '22;color:' + sclass + ';padding:1px 6px;border-radius:3px;font-size:11px;margin-right:6px;font-weight:500">' + stag + '</span>'
        news_html += '<div class="ni">' + badge + '<a href="' + u + '" target="_blank" rel="noopener">' + t + '</a></div>\n'
    news_html += '</div>'

# Build table rows
def trow(n, l):
    p = yf_pct.get(n)
    return '<tr><td>' + l + '</td><td>' + vs(yf[n]['price']) + '</td><td style="color:' + cl(p) + '">' + ar(p) + ps(p) + '</td></tr>'

indices_rows = trow('Nikkei','日经225') + trow('KOSPI','KOSPI') + trow('FTSE100','FTSE100') + trow('DAX','DAX') + trow('CAC40','CAC40')

bond_rows = ''
for n, l in [('3M Yield','3月期'),('5Y Yield','5年期'),('10Y Yield','10年期'),('30Y Yield','30年期')]:
    p = yf_pct.get(n)
    bond_rows += '<tr><td>' + l + '</td><td>' + vs(yf[n]['price']) + '%</td><td style="color:' + cl(p) + '">' + ar(p) + ps(p) + '</td></tr>'

commodity_rows = ''
for n, l in [('Gold','黄金'),('Crude','原油'),('Silver','白银'),('Copper','铜')]:
    p = yf_pct.get(n)
    commodity_rows += '<tr><td>' + l + '</td><td>$' + vs(yf[n]['price']) + '</td><td style="color:' + cl(p) + '">' + ar(p) + ps(p) + '</td></tr>'

crypto_rows = ''
for n, l in [('BTC','BTC'),('ETH','ETH')]:
    p = yf_pct.get(n)
    crypto_rows += '<tr><td>' + l + '</td><td>$' + vs(yf[n]['price'],0) + '</td><td style="color:' + cl(p) + '">' + ar(p) + ps(p) + '</td></tr>'

data = {
    'indices_rows': indices_rows,
    'bond_rows': bond_rows,
    'commodity_rows': commodity_rows,
    'crypto_rows': crypto_rows,
    'news_html': news_html,
}
import os
os.makedirs('/home/hermes_agent/digest', exist_ok=True)
with open('/home/hermes_agent/digest/html_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False)

print('OK: caixin={} people={} eastmoney={}'.format(len(caixin_good), len(people_good), len(east_good)))
print('Data saved to html_data.json')
