#!/usr/bin/env python3
"""Build daily digest HTML from JSON data"""
import json

with open('/home/hermes_agent/digest/today_yf.json') as f:
    yf = json.load(f)
with open('/home/hermes_agent/digest/today_news.json') as f:
    news = json.load(f)

# Determine up/down colors (Chinese convention: ▲ red for up, ▼ green for down)
def updown(val):
    if val > 0: return '<span style="color:#F85149">▲</span>'
    elif val < 0: return '<span style="color:#3FB950">▼</span>'
    else: return '<span style="color:#8b949e">—</span>'

def red_green(val, suffix='%'):
    if val > 0: return f'<span style="color:#F85149">+{val:.2f}{suffix}</span>'
    elif val < 0: return f'<span style="color:#3FB950">{val:.2f}{suffix}</span>'
    else: return f'<span style="color:#8b949e">0.00{suffix}</span>'

def fmt_price(val):
    if val >= 10000:
        return f'{val:,.2f}'
    elif val >= 100:
        return f'{val:.2f}'
    else:
        return f'{val:.4f}'

lines = []
lines.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日新闻速览 - 2026年6月18日</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",sans-serif;background:#0d1117;color:#c9d1d9;padding:16px;max-width:640px;margin:0 auto}
.title{font-size:26px;font-weight:700;color:#f0f6fc;padding:20px 0 8px 0;text-align:center}
.subtitle{font-size:14px;color:#8b949e;text-align:center;padding-bottom:16px;border-bottom:1px solid #30363d;margin-bottom:12px}
.section{border:1px solid #30363d;border-radius:8px;padding:14px;margin-bottom:12px;background:#161b22}
.section-title{font-size:18px;font-weight:600;color:#f0f6fc;margin-bottom:10px;display:flex;align-items:center;gap:6px}
.icon{font-size:20px}
.idx-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #21262d;font-size:17px}
.idx-row:last-child{border-bottom:none}
.idx-name{color:#c9d1d9}
.idx-value{font-weight:600;color:#f0f6fc}
.idx-change{text-align:right;min-width:80px}
.tag{display:inline-block;background:#21262d;color:#c9d1d9;padding:3px 10px;border-radius:4px;margin:2px;font-size:13px}
.tag-red{display:inline-block;background:#2d1517;color:#F85149;padding:3px 10px;border-radius:4px;margin:2px;font-size:13px}
.tag-green{display:inline-block;background:#162b1c;color:#3FB950;padding:3px 10px;border-radius:4px;margin:2px;font-size:13px}
.news-item{padding:6px 0;border-bottom:1px solid #21262d;font-size:14px;line-height:1.6}
.news-item:last-child{border-bottom:none}
.news-item a{color:#58a6ff;text-decoration:none}
.news-item a:hover{text-decoration:underline}
.news-source{display:inline-block;background:#1f2937;color:#8b949e;padding:1px 6px;border-radius:3px;font-size:11px;margin-right:6px}
.summary-text{font-size:14px;line-height:1.8;color:#c9d1d9}
</style>
</head>
<body>
<div class="title">📰 每日新闻速览</div>
<div class="subtitle">2026年6月18日 周四 · 数据截至6月17日收盘</div>
''')

# === 港股 ===
hsi_change = -0.742  # from MCP
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">🇭🇰</span> 港股市场</div>')
lines.append(f'<div class="idx-row"><span class="idx-name">恒生指数</span><span class="idx-value">{fmt_price(24312.16)}</span><span class="idx-change">{updown(hsi_change)} {red_green(hsi_change)}</span></div>')
lines.append('<div style="padding:6px 0;font-size:14px"><strong style="color:#f0f6fc">领涨板块：</strong>')
lines.append('半导体(+7.14%)、资讯科技器材(+0.04%)、建筑(+0.35%)、工业工程(+0.32%)')
lines.append('</div>')
lines.append('</div>')

# === A股 ===
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">🇨🇳</span> A股市场</div>')
lines.append(f'<div class="idx-row"><span class="idx-name">上证指数</span><span class="idx-value">{fmt_price(4108.08)}</span><span class="idx-change">{updown(0.40)} {red_green(0.40)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">深证成指</span><span class="idx-value">{fmt_price(15880.95)}</span><span class="idx-change">{updown(1.31)} {red_green(1.31)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">创业板指</span><span class="idx-value">{fmt_price(4167.05)}</span><span class="idx-change">{updown(1.56)} {red_green(1.56)}</span></div>')
lines.append('<div style="padding:6px 0;font-size:14px"><strong style="color:#f0f6fc">行业板块领涨：</strong>')
lines.append('<span class="tag-red">玻璃玻纤 +7.83%</span> <span class="tag-red">电子化学品Ⅱ +6.72%</span> <span class="tag-red">光学光电子 +5.38%</span> <span class="tag-red">半导体 +5.30%</span> <span class="tag-red">其他电子Ⅱ +4.98%</span>')
lines.append('</div>')
lines.append('<div style="padding:6px 0;font-size:14px"><strong style="color:#f0f6fc">概念板块领涨：</strong>')
lines.append('<span class="tag-red">药用玻璃 +8.50%</span> <span class="tag-red">气溶胶检测 +8.38%</span> <span class="tag-red">全面屏 +8.37%</span> <span class="tag-red">电子纸 +8.13%</span> <span class="tag-red">裸眼3D +8.00%</span>')
lines.append('</div>')
lines.append('<div style="padding:6px 0;font-size:14px"><strong style="color:#f0f6fc">资金流入前三板块：</strong>')
lines.append('<span class="tag-red">电子 +272.2亿</span> <span class="tag-red">半导体 +242.6亿</span> <span class="tag-red">集成电路 +226.1亿</span>')
lines.append('</div>')
lines.append('<div style="padding:6px 0;font-size:14px"><strong style="color:#f0f6fc">连板龙头：</strong>')
lines.append('旭光电子(十天五板)、华正新材(八天五板)、宏昌电子(七天五板)、光华科技(七天四板)、中材科技(七天四板)、诺德股份(七天四板)、海星股份(三天三板)、杭电股份(三天三板)')
lines.append('</div>')
lines.append('</div>')

# === 美股 ===
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">🇺🇸</span> 美股市场 <span style="font-size:12px;color:#8b949e;font-weight:400">（6月17日收盘）</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">标普500</span><span class="idx-value">{fmt_price(7420.10)}</span><span class="idx-change">{updown(-1.21)} {red_green(-1.21)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">纳斯达克</span><span class="idx-value">{fmt_price(26021.66)}</span><span class="idx-change">{updown(-1.34)} {red_green(-1.34)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">道琼斯</span><span class="idx-value">{fmt_price(51492.55)}</span><span class="idx-change">{updown(-0.98)} {red_green(-0.98)}</span></div>')
lines.append('</div>')

# === 国际股市 ===
nikkei_pct = yf.get('nikkei', {}).get('pct', 0)
kospi_pct = yf.get('kospi', {}).get('pct', 0)
ftse_pct = yf.get('ftse100', {}).get('pct', 0)
stoxx_pct = yf.get('stoxx50', {}).get('pct', 0)
asx_pct = yf.get('asx200', {}).get('pct', 0)
nifty_pct = yf.get('nifty50', {}).get('pct', 0)
dax_pct = yf.get('dax', {}).get('pct', 0)
cac_pct = yf.get('cac40', {}).get('pct', 0)

nikkei_price = yf.get('nikkei', {}).get('price', 0)
kospi_price = yf.get('kospi', {}).get('price', 0)
ftse_price = yf.get('ftse100', {}).get('price', 0)
stoxx_price = yf.get('stoxx50', {}).get('price', 0)
asx_price = yf.get('asx200', {}).get('price', 0)
nifty_price = yf.get('nifty50', {}).get('price', 0)
dax_price = yf.get('dax', {}).get('price', 0)
cac_price = yf.get('cac40', {}).get('price', 0)

lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">🌍</span> 国际股市</div>')
lines.append(f'<div class="idx-row"><span class="idx-name">日经225</span><span class="idx-value">{fmt_price(nikkei_price)}</span><span class="idx-change">{updown(nikkei_pct)} {red_green(nikkei_pct)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">KOSPI</span><span class="idx-value">{fmt_price(kospi_price)}</span><span class="idx-change">{updown(kospi_pct)} {red_green(kospi_pct)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">富时100</span><span class="idx-value">{fmt_price(ftse_price)}</span><span class="idx-change">{updown(ftse_pct)} {red_green(ftse_pct)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">欧洲斯托克50</span><span class="idx-value">{fmt_price(stoxx_price)}</span><span class="idx-change">{updown(stoxx_pct)} {red_green(stoxx_pct)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">ASX 200</span><span class="idx-value">{fmt_price(asx_price)}</span><span class="idx-change">{updown(asx_pct)} {red_green(asx_pct)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">NIFTY 50</span><span class="idx-value">{fmt_price(nifty_price)}</span><span class="idx-change">{updown(nifty_pct)} {red_green(nifty_pct)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">德国DAX</span><span class="idx-value">{fmt_price(dax_price)}</span><span class="idx-change">{updown(dax_pct)} {red_green(dax_pct)}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">法国CAC40</span><span class="idx-value">{fmt_price(cac_price)}</span><span class="idx-change">{updown(cac_pct)} {red_green(cac_pct)}</span></div>')
lines.append('</div>')

# === 美债 ===
irx = yf.get('^IRX', {})
fvx = yf.get('^FVX', {})
tnx = yf.get('^TNX', {})
tyx = yf.get('^TYX', {})
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">📄</span> 美债收益率</div>')
lines.append(f'<div class="idx-row"><span class="idx-name">3月期</span><span class="idx-value">{irx.get("price",0):.2f}%</span><span class="idx-change">{updown(irx.get("pct",0))} {red_green(irx.get("pct",0))}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">5年期</span><span class="idx-value">{fvx.get("price",0):.2f}%</span><span class="idx-change">{updown(fvx.get("pct",0))} {red_green(fvx.get("pct",0))}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">10年期</span><span class="idx-value">{tnx.get("price",0):.2f}%</span><span class="idx-change">{updown(tnx.get("pct",0))} {red_green(tnx.get("pct",0))}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">30年期</span><span class="idx-value">{tyx.get("price",0):.2f}%</span><span class="idx-change">{updown(tyx.get("pct",0))} {red_green(tyx.get("pct",0))}</span></div>')
lines.append('</div>')

# === 外汇 ===
dxy = yf.get('dxy', {})
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">💱</span> 外汇市场</div>')
lines.append(f'<div class="idx-row"><span class="idx-name">美元指数 DXY</span><span class="idx-value">{dxy.get("price",0):.2f}</span><span class="idx-change">{updown(dxy.get("pct",0))} {red_green(dxy.get("pct",0))}</span></div>')
lines.append('<div class="idx-row"><span class="idx-name">EUR/USD</span><span class="idx-value">1.1503</span><span class="idx-change">' + updown(0.03) + ' ' + red_green(0.03) + '</span></div>')
lines.append('<div class="idx-row"><span class="idx-name">USD/JPY</span><span class="idx-value">160.61</span><span class="idx-change">' + updown(-0.01) + ' ' + red_green(-0.01) + '</span></div>')
lines.append('<div class="idx-row"><span class="idx-name">USD/CNY</span><span class="idx-value">6.763</span><span class="idx-change">' + updown(0.08) + ' ' + red_green(0.08) + '</span></div>')
lines.append('<div class="idx-row"><span class="idx-name">USD/HKD</span><span class="idx-value">7.835</span><span class="idx-change">' + updown(-0.01) + ' ' + red_green(-0.01) + '</span></div>')
lines.append('</div>')

# === 商品 ===
gold = yf.get('gold', {})
crude = yf.get('crude', {})
silver = yf.get('silver', {})
copper = yf.get('copper', {})
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">🛢️</span> 商品市场</div>')
lines.append(f'<div class="idx-row"><span class="idx-name">✨黄金</span><span class="idx-value">${gold.get("price",0):,.2f}</span><span class="idx-change">{updown(gold.get("pct",0))} {red_green(gold.get("pct",0))}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">原油 (WTI)</span><span class="idx-value">${crude.get("price",0):.2f}</span><span class="idx-change">{updown(crude.get("pct",0))} {red_green(crude.get("pct",0))}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">白银</span><span class="idx-value">${silver.get("price",0):.2f}</span><span class="idx-change">{updown(silver.get("pct",0))} {red_green(silver.get("pct",0))}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">铜</span><span class="idx-value">${copper.get("price",0):.4f}</span><span class="idx-change">{updown(copper.get("pct",0))} {red_green(copper.get("pct",0))}</span></div>')
lines.append('</div>')

# === 加密货币 ===
btc = yf.get('btc', {})
eth = yf.get('eth', {})
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">₿</span> 加密货币</div>')
lines.append(f'<div class="idx-row"><span class="idx-name">BTC</span><span class="idx-value">${btc.get("price",0):,.2f}</span><span class="idx-change">{updown(btc.get("pct",0))} {red_green(btc.get("pct",0))}</span></div>')
lines.append(f'<div class="idx-row"><span class="idx-name">ETH</span><span class="idx-value">${eth.get("price",0):,.2f}</span><span class="idx-change">{updown(eth.get("pct",0))} {red_green(eth.get("pct",0))}</span></div>')
lines.append('</div>')

# === 新闻 ===
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">📰</span> 要闻速览</div>')

# 财新网
lines.append('<div style="padding:4px 0 2px 0;font-size:14px;color:#f0f6fc;font-weight:600">📌 财新网</div>')
for n in news['caixin'][:8]:
    lines.append(f'<div class="news-item"><span class="news-source">财新</span><a href="{n["url"]}" target="_blank" rel="noopener noreferrer">{n["title"]}</a></div>')

# 人民网
lines.append('<div style="padding:6px 0 2px 0;font-size:14px;color:#f0f6fc;font-weight:600">📌 人民网</div>')
for n in news['people'][:8]:
    lines.append(f'<div class="news-item"><span class="news-source">人民</span><a href="{n["url"]}" target="_blank" rel="noopener noreferrer">{n["title"]}</a></div>')

# 东方财富
lines.append('<div style="padding:6px 0 2px 0;font-size:14px;color:#f0f6fc;font-weight:600">📌 东方财富</div>')
for n in news['eastmoney'][:8]:
    lines.append(f'<div class="news-item"><span class="news-source">东财</span><a href="{n["url"]}" target="_blank" rel="noopener noreferrer">{n["title"]}</a></div>')

# FT中文网
lines.append('<div style="padding:6px 0 2px 0;font-size:14px;color:#f0f6fc;font-weight:600">📌 金融时报</div>')
for n in news['ftchinese'][:8]:
    lines.append(f'<div class="news-item"><span class="news-source">FT</span><a href="{n["url"]}" target="_blank" rel="noopener noreferrer">{n["title"]}</a></div>')

lines.append('</div>')

# === 今日总结 ===
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">📋</span> 今日总结</div>')
lines.append('<div class="summary-text">')

# 市场总览
lines.append('<strong>🌏 市场总览</strong><br>')
# Global market summary
a_shanghai = 0.40
chi_next = -0.74
sp500 = -1.21
nikkei_p = nikkei_pct
kospi_p = kospi_pct
lines.append('亚太市场分化：A股三大指数全线收涨（上证+0.40%、深证+1.31%、创业板+1.56%），恒指小幅收跌-0.74%；')
lines.append(f'美股三大指数集体回调（标普{sp500:.2f}%、纳指-1.34%、道指-0.98%）；')
lines.append(f'亚太市场涨跌互现（日经+0.13%、KOSPI+{kospi_p:.2f}%），欧洲市场小幅上扬（斯托克50+0.45%、CAC40+0.75%）。')
lines.append(f'美债收益率短端上行、长端回落，10年期报4.46%（-0.53%），30年期报4.93%（-0.98%）。')
lines.append('外汇市场美元走强（DXY+0.85%），人民币小幅贬值至6.763。')
lines.append('<br><br>')

# A股热点
lines.append('<strong>🔥 A股热点</strong><br>')
lines.append('行业板块：半导体(+5.30%)、光学光电子(+5.38%)、电子化学品Ⅱ(+6.72%)、玻璃玻纤(+7.83%)领涨；')
lines.append('概念板块：药用玻璃(+8.50%)、气溶胶检测(+8.38%)、全面屏(+8.37%)、电子纸(+8.13%)、裸眼3D(+8.00%)。')
lines.append('连板龙头：旭光电子(十天五板)、华正新材(八天五板)、宏昌电子(七天五板)、光华科技(七天四板)。')
lines.append('主力资金流入前三：电子(+272.2亿)、半导体(+242.6亿)、集成电路(+226.1亿)。')
lines.append('<br><br>')

# 要闻聚焦
lines.append('<strong>📌 要闻聚焦</strong><br>')
lines.append('• 习近平对常态化做好东西部协作工作作出重要指示，闽宁协作三十年启示录发布<br>')
lines.append('• 国务院印发《实施就业优先战略"十五五"规划》<br>')
lines.append('• 中国政府发布关于全球治理的白皮书<br>')
lines.append('• 王毅同伊朗外长通话，伊方感谢中方为推动谈判发挥积极作用<br>')
lines.append('• 2026陆家嘴论坛今日开幕，潘功胜、吴清等将发声<br>')
lines.append('• DeepSeek首轮融资完成，AI行业持续扩张<br>')
lines.append('• 央行创设境外央行类机构回购工具，优化离岸人民币流动性管理<br>')
lines.append('• 美股回调：纳指跌超1%，芯片股跳水；SpaceX一度超亚马逊跻身全球前五<br>')
lines.append('• 网贷行业研究设立纾困基金，每年投入不低于15亿元<br>')
lines.append('• 德勤：上半年港交所新股募资额全球第二<br>')

lines.append('</div>')
lines.append('</div>')

lines.append('</body></html>')

html = '\n'.join(lines)
with open('/home/hermes_agent/digest/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML written: {len(html)} chars")
