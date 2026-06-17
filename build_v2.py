#!/usr/bin/env python3
import json

with open('/home/hermes_agent/digest/yf_data.json') as f:
    yf = json.load(f)

with open('/home/hermes_agent/digest/news_data.json') as f:
    d = json.load(f)
    caixin_good = d['caixin'][:8]

with open('/home/hermes_agent/digest/people_extra.json') as f:
    pe = json.load(f)
    people_good = [it for it in pe if len(it[0])>=8][:8]

with open('/home/hermes_agent/digest/eastmoney_extra.json') as f:
    ea = json.load(f)
    east_good = [it for it in ea if len(it[0])>=8 and '指数' not in it[0] and '行情' not in it[0]][:8]

yf_pct = {}
for k,v in yf.items():
    if v.get('price') and v.get('prev_close') and v['prev_close']>0:
        yf_pct[k] = ((v['price']-v['prev_close'])/v['prev_close'])*100
    else:
        yf_pct[k] = None

def ud(v):
    return '' if v is None or v==0 else ('▲' if v>0 else '▼')
def cl(v):
    return '' if v is None or v==0 else ('#F85149' if v>0 else '#3FB950')
def ps(v):
    return '—' if v is None or v==0 else f'{abs(v):.2f}%'
def vs(v,n=2):
    return '—' if v is None else f'{v:.{n}f}'
def T(n,l):
    p=yf_pct.get(n)
    return f'<tr><td>{l}</td><td>{vs(yf[n]["price"])}</td><td style="color:{cl(p)}">{ud(p)}{ps(p)}</td></tr>'

h='''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>'''+'每日新闻速递 — 2026年6月6日</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,"Segoe UI","Noto Sans SC",sans-serif;padding:16px}
h1{font-size:28px;color:#f0f6fc;margin-bottom:4px}
.date{font-size:16px;color:#8b949e;margin-bottom:20px}
.s{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px}
.st{font-size:18px;font-weight:600;color:#f0f6fc;margin-bottom:12px}
table{width:100%;border-collapse:collapse;font-size:15px}
th{text-align:left;color:#8b949e;font-weight:500;padding:4px 8px;border-bottom:1px solid #21262d}
td{padding:6px 8px;border-bottom:1px solid #21262d}
tr:last-child td{border-bottom:none}
.tag{display:inline-block;background:#21262d;color:#c9d1d9;padding:2px 8px;border-radius:4px;font-size:13px;margin:2px}
.ni{padding:6px 0;border-bottom:1px solid #21262d;font-size:15px}
.ni:last-child{border-bottom:none}
.ni a{color:#58a6ff;text-decoration:none}
.stag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:11px;margin-right:6px;font-weight:500}
.sc{background:#1f3a3f;color:#7ee787}
.sp{background:#3d1f2e;color:#f97583}
.se{background:#1f2e3d;color:#79c0ff}
.ft{font-size:15px;line-height:1.8}
.footer{text-align:center;font-size:13px;color:#484f58;margin-top:20px;line-height:1.8}
</style></head><body>
<h1>\U0001f4f0 每日新闻速递</h1>
<div class="date">\U0001f4c6 2026年6月6日（周六）· 数据截止6月5日收盘</div>

<div class="s"><div class="st">\U0001f1ed\U0001f1f0 港股</div>
<table><tr><th>指数</th><th>收盘</th><th>涨跌幅</th></tr>
<tr><td>恒生指数</td><td>24,962</td><td style="color:#3FB950">\u25bc1.15%</td></tr></table></div>

<div class="s"><div class="st">\U0001f1e8\U0001f1f3 A股</div>
<table><tr><th>指数</th><th>收盘</th><th>涨跌幅</th></tr>
<tr><td>上证指数</td><td>4,028</td><td style="color:#3FB950">\u25bc0.74%</td></tr>
<tr><td>深证成指</td><td>15,315</td><td style="color:#3FB950">\u25bc2.21%</td></tr>
<tr><td>创业板指</td><td>3,958</td><td style="color:#3FB950">\u25bc3.20%</td></tr>
</table>
<div style="margin-top:10px">
<div style="font-size:14px;color:#8b949e;margin-bottom:4px">领涨行业</div>
<span class="tag">航天装备\u2161 +6.78%</span> <span class="tag">电机\u2161 +3.15%</span> <span class="tag">化学纤维 +3.05%</span>
<span class="tag">金属新材料 +2.98%</span> <span class="tag">数字媒体 +2.92%</span>
</div>
<div style="margin-top:6px">
<div style="font-size:14px;color:#8b949e;margin-bottom:4px">领涨概念</div>
<span class="tag">空中成像 +7.42%</span> <span class="tag">药用玻璃 +5.66%</span> <span class="tag">航天科技集团 +5.41%</span>
<span class="tag">NFC概念 +5.41%</span> <span class="tag">华为机器人 +5.38%</span>
</div>
<div style="margin-top:6px">
<div style="font-size:14px;color:#8b949e;margin-bottom:4px">连板龙头</div>
<span class="tag">泰坦股份 十天五板</span> <span class="tag">大有能源 五天五板</span>
<span class="tag">中重科技 三天三板</span> <span class="tag">方大炭素 三天二板</span>
</div></div>

<div class="s"><div class="st">\U0001f1fa\U0001f1f8 美股（6月5日收盘）</div>
<table><tr><th>指数</th><th>收盘</th><th>涨跌幅</th></tr>
<tr><td>标普500</td><td>7,384</td><td style="color:#3FB950">\u25bc2.64%</td></tr>
<tr><td>纳斯达克</td><td>25,709</td><td style="color:#3FB950">\u25bc4.18%</td></tr>
<tr><td>道琼斯</td><td>50,867</td><td style="color:#3FB950">\u25bc1.35%</td></tr>
</table></div>

<div class="s"><div class="st">\U0001f30d 国际股市</div>
<table><tr><th>指数</th><th>收盘</th><th>涨跌幅</th></tr>'''
h+=T('Nikkei','日经225')
h+=T('KOSPI','KOSPI')
h+=T('FTSE100','FTSE100')
h+=T('DAX','DAX')
h+=T('CAC40','CAC40')
h+='''</table></div>

<div class="s"><div class="st">\U0001f4c4 美债收益率</div>
<table><tr><th>品种</th><th>收益率</th><th>涨跌</th></tr>'''
for n,l in [('3M Yield','3月期'),('5Y Yield','5年期'),('10Y Yield','10年期'),('30Y Yield','30年期')]:
    p=yf_pct.get(n)
    h+=f'<tr><td>{l}</td><td>{vs(yf[n]["price"])}%</td><td style="color:{cl(p)}">{ud(p)}{ps(p)}</td></tr>'
h+='''</table></div>

<div class="s"><div class="st">\U0001f4b1 外汇</div>
<table><tr><th>品种</th><th>汇价</th><th>涨跌</th></tr>
<tr><td>美元指数</td><td>100.07</td><td style="color:#F85149">\u25b20.88%</td></tr>
<tr><td>EUR/USD</td><td>1.1527</td><td style="color:#3FB950">\u25bc1.05%</td></tr>
<tr><td>USD/JPY</td><td>160.29</td><td style="color:#F85149">\u25b20.17%</td></tr>
<tr><td>USD/CNY</td><td>6.7878</td><td>—</td></tr>
<tr><td>USD/HKD</td><td>7.8332</td><td style="color:#3FB950">\u25bc0.02%</td></tr>
</table></div>

<div class="s"><div class="st">\U0001f6e2\ufe0f 商品</div>
<table><tr><th>品种</th><th>价格</th><th>涨跌</th></tr>'''
for n,l in [('Gold','黄金'),('Crude','原油'),('Silver','白银'),('Copper','铜')]:
    p=yf_pct.get(n)
    h+=f'<tr><td>{l}</td><td>${vs(yf[n]["price"])}</td><td style="color:{cl(p)}">{ud(p)}{ps(p)}</td></tr>'
h+='''</table></div>

<div class="s"><div class="st">\u20bf 加密货币</div>
<table><tr><th>品种</th><th>价格</th><th>涨跌</th></tr>'''
for n,l in [('BTC','BTC'),('ETH','ETH')]:
    p=yf_pct.get(n)
    h+=f'<tr><td>{l}</td><td>${vs(yf[n]["price"],0)}</td><td style="color:{cl(p)}">{ud(p)}{ps(p)}</td></tr>'
h+='''</table></div>

<div class="s"><div class="st">\U0001f4f0 要闻</div>'''

for sname,stag,scls,items in [('财新网','caixin','sc',caixin_good),('人民网','people','sp',people_good),('东方财富','eastmoney','se',east_good)]:
    h+=f'<div style="margin-bottom:10px"><div style="font-size:14px;color:#8b949e;margin-bottom:4px">\U0001f4cc {sname}</div>\n'
    for t,u in items:
        h+=f'<div class="ni"><span class="stag {scls}">{stag}</span><a href="{u}" target="_blank" rel="noopener">{t}</a></div>\n'
    h+='</div>'

h+='''</div>

<div class="s"><div class="st">\U0001f4cb 今日总结</div>
<div class="ft">
<strong>\U0001f30f 市场总览</strong><br>
全球股市遭遇重挫，美股三大指数大幅下跌（纳指-4.18%、标普-2.64%），科技股领跌。A股普遍走弱（上证-0.74%、深证-2.21%、创业板-3.20%），港股恒指跌1.15%。国际指数全线回落（日经-0.52%、FTSE-0.40%、DAX-1.38%），仅CAC40小幅收涨+0.88%。美债收益率小幅攀升，10年期升至4.536%，30年期逼近5%。美元强势反弹（DXY+0.88%），黄金大跌2.46%至$4,365，白银暴跌7.87%。加密货币市场遭遇血洗，BTC跌9.15%至$60,601，ETH暴跌16.09%至$1,559。
<br><br>
<strong>\U0001f525 A股热点</strong><br>
行业板块：航天装备\u2161(+6.78%)、电机\u2161(+3.15%)、化学纤维(+3.05%)、金属新材料(+2.98%)领涨；概念板块：空中成像(+7.42%)、药用玻璃(+5.66%)、航天科技集团(+5.41%)、华为机器人(+5.38%)。连板龙头：泰坦股份(十天五板)、大有能源(五天五板)、中重科技(三天三板)。
<br><br>
<strong>\U0001f4cc 要闻聚焦</strong><br>
• 美股遭遇血腥抛售，纳指暴跌4.18%，华尔街集体恐慌<br>
• 深圳宅地单价突破10万元，央企保利竞价300轮斩获新"地王"<br>
• 公募"大姐大"易方达刘晓艳出任基金业协会新会长<br>
• 国家数据局：让公共数据"跑起来""活起来"<br>
• 5月中国机器人产业指数环比升6.4%，工业机器人出口增速超产量<br>
• 1.6万名中国受害者英国追索，6万枚比特币案资产处置有进展<br>
• 物流业稳步回暖，经济活力持续释放<br>
• AI基建催生"算力金属"热潮<br>
</div></div>

<div class="footer">
\u25b2<span style="color:#F85149">红涨</span> \u25bc<span style="color:#3FB950">绿跌</span>（中国惯例：红涨绿跌）<br>
数据来源：新浪财经 · Yahoo Finance · 财新网 · 人民网 · 东方财富<br>
<a href="https://zhengyanting40.github.io/daily-digest/" style="color:#58a6ff;">\U0001f4c2 历史存档</a>
</div>
</body></html>'''

with open('/home/hermes_agent/digest/index.html','w') as f:
    f.write(h)
print(f'HTML: {len(h)} chars')
nc = h.count('<div class="ni">')
print(f'News items: caixin={len(caixin_good)}, people={len(people_good)}, eastmoney={len(east_good)}, total={nc}')
