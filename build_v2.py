#!/usr/bin/env python3
"""Build daily digest HTML from collected JSON data - July 8, 2026"""
import json

DIGEST = '/home/hermes_agent/digest'

# Load data
with open(f'{DIGEST}/today_cn.json') as f: cn = json.load(f)
with open(f'{DIGEST}/today_yf.json') as f: yf = json.load(f)
with open(f'{DIGEST}/today_news.json') as f: news = json.load(f)
with open(f'{DIGEST}/today_sectors.json') as f: sectors = json.load(f)
with open(f'{DIGEST}/today_stocks.json') as f: stocks_data = json.load(f)

a_idx = cn.get('a_indices', {})
hk = cn.get('hk', {})
hy_sectors = sectors.get('hy_sectors', [])
gn_sectors = sectors.get('gn_sectors', [])
fund_flow = sectors.get('fund_flow', [])
hk_sectors = sectors.get('hk_sectors', [])
hot_stocks = sectors.get('hot_stocks', [])
top_gainers = stocks_data.get('top_gainers', [])

def fmt_pct(pct):
    try: return f'{float(pct):+.2f}%'
    except: return '+0.00%'

def up_down(pct):
    try: return 'u' if float(pct) >= 0 else 'd'
    except: return 'u'

def idx_row(name, price, pct):
    u = up_down(pct)
    cls = 'up' if u == 'u' else 'down'
    arrow = '\u25b2' if u == 'u' else '\u25bc'
    return f'<div class="idx-row"><span class="idx-name">{name}</span><span class="idx-price">{price}</span><span class="idx-pct {cls}">{arrow} {fmt_pct(pct)}</span></div>'

def tag(name, pct, unit='%'):
    u = up_down(pct)
    cls = 'tag-up' if u == 'u' else 'tag-down'
    return f'<span class="tag {cls}">{name} {fmt_pct(pct)}</span>'

def meta(src, dt):
    return f'<div class="meta">\U0001f4e1 {src} | \U0001f5d3\ufe0f {dt}</div>'

lines = []

# CSS + Head
lines.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>\u6bcf\u65e5\u65b0\u95fb\u901f\u9012 \u00b7 2026\u5e747\u67088\u65e5</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Helvetica Neue",sans-serif;background:#0d1117;color:#c9d1d9;padding:12px;line-height:1.6;max-width:600px;margin:0 auto}
.header{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;padding:16px;margin-bottom:12px;text-align:center;border:1px solid #30363d}
.header h1{font-size:20px;font-weight:700;margin-bottom:4px}
.header .sub{font-size:12px;color:#484f58}
.section{background:#161b22;border-radius:10px;padding:12px;margin-bottom:10px;border-left:3px solid #30363d;overflow:hidden}
.section-title{font-size:16px;font-weight:600;margin-bottom:8px;color:#e6edf3}
.section-title .icon{margin-right:6px}
.meta{font-size:11px;color:#484f58;margin-top:-4px;margin-bottom:8px}
.idx-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #21262d;font-size:15px}
.idx-row:last-child{border-bottom:none}
.idx-name{font-weight:500}
.idx-price{font-weight:600}
.idx-pct{font-weight:600;width:80px;text-align:right}
.up{color:#F85149}
.down{color:#3FB950}
.tag{display:inline-block;background:#21262d;border-radius:4px;padding:2px 8px;margin:2px;font-size:13px;white-space:nowrap}
.tag-up{background:#2d1b1b;color:#F85149}
.tag-down{background:#1b2d1b;color:#3FB950}
.news-item{padding:6px 0;border-bottom:1px solid #21262d;font-size:14px}
.news-item:last-child{border-bottom:none}
.news-item a{color:#58a6ff;text-decoration:none}
.news-item a:hover{text-decoration:underline}
.summary-text{font-size:14px;line-height:1.8;color:#c9d1d9}
.summary-text strong{color:#e6edf3}
.footer{text-align:center;font-size:11px;color:#484f58;padding:12px}
@media(max-width:480px){.idx-row{font-size:14px}.section-title{font-size:15px}}
</style>
</head>
<body>''')

# Header
dow = '\u661f\u671f\u4e09'  # Wednesday
lines.append(f'<div class="header">')
lines.append(f'<h1>\U0001f4f0 \u6bcf\u65e5\u65b0\u95fb\u901f\u9012</h1>')
lines.append(f'<div class="sub">2026\u5e747\u67088\u65e5 \u00b7 {dow} \u00b7 \u6570\u636e\u622a\u81f37\u67087\u65e5\u6536\u76d8</div>')
lines.append('</div>')

# === 1. Hong Kong ===
lines.append('<div class="section" style="border-color:#F85149;">')
lines.append('<div class="section-title"><span class="icon">\U0001f1ed\U0001f1f0</span> \u6e2f\u80a1</div>')
hsi = hk.get('hkHSI', {})
hcei = hk.get('hkHSCEI', {})
hsi_pct = hsi.get('pct', 0)
hcei_pct = hcei.get('pct', 0)
lines.append(idx_row('\u6052\u751f\u6307\u6570', hsi.get('price', '--'), hsi_pct))
lines.append(idx_row('\u56fd\u4f01\u6307\u6570', hcei.get('price', '--'), hcei_pct))
# HK leading sectors
hk_leading = [s for s in hk_sectors[:6] if s.get('pct', 0) > 0][:5]
if hk_leading:
    lines.append('<div style="margin-top:8px"><strong>\u9886\u6da8\u677f\u5757\uff1a</strong><br>')
    for s in hk_leading:
        lines.append(tag(s.get('name',''), s.get('pct',0)))
    lines.append('</div>')
lines.append(meta('\u65b0\u6d6a\u8d22\u7ecf', '2026-07-07'))
lines.append('</div>')

# === 2. A-share ===
lines.append('<div class="section" style="border-color:#F85149;">')
lines.append('<div class="section-title"><span class="icon">\U0001f1e8\U0001f1f3</span> A\u80a1</div>')
sh = a_idx.get('sh000001', {})
sz = a_idx.get('sz399001', {})
cy = a_idx.get('sz399006', {})
lines.append(idx_row('\u4e0a\u8bc1\u6307\u6570', sh.get('price', '--'), sh.get('pct', 0)))
lines.append(idx_row('\u6df1\u8bc1\u6210\u6307', sz.get('price', '--'), sz.get('pct', 0)))
lines.append(idx_row('\u521b\u4e1a\u677f\u6307', cy.get('price', '--'), cy.get('pct', 0)))

# Leading industry sectors
if hy_sectors:
    lines.append('<div style="margin-top:8px"><strong>\u9886\u6da8\u884c\u4e1a\u677f\u5757\uff1a</strong><br>')
    for s in hy_sectors[:6]:
        lines.append(tag(s.get('name',''), s.get('pct',0)))
    lines.append('</div>')

# Leading concept sectors
if gn_sectors:
    lines.append('<div style="margin-top:6px"><strong>\u9886\u6da8\u6982\u5ff5\u677f\u5757\uff1a</strong><br>')
    for s in gn_sectors[:6]:
        lines.append(tag(s.get('name',''), s.get('pct',0)))
    lines.append('</div>')

# Fund flow
if fund_flow:
    lines.append('<div style="margin-top:6px"><strong>\u4e3b\u529b\u8d44\u91d1\u6d41\u5165\u524d\u4e09\uff1a</strong><br>')
    for i, s in enumerate(fund_flow[:3]):
        inflow = s.get('net_inflow', 0)
        lines.append(f'<span class="tag tag-up">{s.get("name","")} {inflow:.1f}\u4ebf</span>')
    lines.append('</div>')

# Top gainers
if top_gainers:
    lines.append('<div style="margin-top:6px"><strong>\u70ed\u70b9\u80a1\u7968 Top 10\uff1a</strong><br>')
    for s in top_gainers[:10]:
        pct = s.get('pct', 0)
        lines.append(tag(f'{s.get("name","")}({s.get("price","")})', pct))
    lines.append('</div>')

lines.append(meta('\u65b0\u6d6a\u8d22\u7ecf / \u4e1c\u65b9\u8d22\u5bcc', '2026-07-07'))
lines.append('</div>')

# === 3. US ===
lines.append('<div class="section" style="border-color:#F85149;">')
lines.append('<div class="section-title"><span class="icon">\U0001f1fa\U0001f1f8</span> \u7f8e\u80a1</div>')
for k in ['S&P 500', 'NASDAQ', '\u9053\u7434\u65af']:
    d = yf.get(k, {})
    if isinstance(d, dict) and d.get('price'):
        lines.append(idx_row(k, round(d['price'], 2), d.get('pct', 0)))
lines.append(meta('Yahoo Finance v8', '2026-07-07'))
lines.append('</div>')

# === 4. International ===
lines.append('<div class="section">')
lines.append('<div class="section-title"><span class="icon">\U0001f30d</span> \u56fd\u9645\u80a1\u5e02</div>')
intl_names = ['\u65e5\u7ecf225', 'KOSPI', '\u5bcc\u65f6100', '\u65af\u6258\u514b50', 'ASX 200', 'NIFTY 50', 'DAX', 'CAC']
intl_display = {'\u65e5\u7ecf225': '\u65e5\u7ecf225', 'KOSPI': 'KOSPI', '\u5bcc\u65f6100': '\u5bcc\u65f6100',
                '\u65af\u6258\u514b50': '\u65af\u6258\u514b50', 'ASX 200': 'ASX 200', 'NIFTY 50': 'NIFTY 50',
                'DAX': 'DAX', 'CAC': 'CAC'}
for k in intl_names:
    d = yf.get(k, {})
    if isinstance(d, dict) and d.get('price'):
        lines.append(idx_row(intl_display.get(k, k), round(d['price'], 2), d.get('pct', 0)))
lines.append(meta('Yahoo Finance v8', '2026-07-07'))
lines.append('</div>')

# === 5. US Bonds ===
lines.append('<div class="section">')
lines.append('<div class="section-title"><span class="icon">\U0001f4c4</span> \u7f8e\u503a\u6536\u76ca\u7387</div>')
for k, n in [('3\u4e2a\u6708', '3\u6708\u671f'), ('5\u5e74', '5\u5e74'), ('10\u5e74', '10\u5e74'), ('30\u5e74', '30\u5e74')]:
    d = yf.get(k, {})
    if isinstance(d, dict) and d.get('price'):
        lines.append(idx_row(n, f'{d["price"]:.3f}%', d.get('pct', 0)))
lines.append(meta('Yahoo Finance v8', '2026-07-07'))
lines.append('</div>')

# === 6. Forex ===
lines.append('<div class="section">')
lines.append('<div class="section-title"><span class="icon">\U0001f4b1</span> \u5916\u6c47</div>')
for k in ['DXY', 'EUR/USD', 'USD/JPY', 'USD/CNY', 'USD/HKD']:
    d = yf.get(k, {})
    if isinstance(d, dict) and d.get('price'):
        lines.append(idx_row(k, round(d['price'], 4), d.get('pct', 0)))
lines.append(meta('Yahoo Finance v8', '2026-07-07'))
lines.append('</div>')

# === 7. Commodities ===
lines.append('<div class="section">')
lines.append('<div class="section-title"><span class="icon">\U0001f6e2\ufe0f</span> \u5546\u54c1</div>')
for k, n in [('\u9ec4\u91d1', '\u9ec4\u91d1'), ('\u539f\u6cb9', '\u539f\u6cb9'), ('\u767d\u94f6', '\u767d\u94f6'), ('\u94dc', '\u94dc')]:
    d = yf.get(k, {})
    if isinstance(d, dict) and d.get('price'):
        lines.append(idx_row(n, round(d['price'], 2), d.get('pct', 0)))
lines.append(meta('Yahoo Finance v8', '2026-07-07'))
lines.append('</div>')

# === 8. Crypto ===
lines.append('<div class="section">')
lines.append('<div class="section-title"><span class="icon">\u20bf</span> \u52a0\u5bc6\u8d27\u5e01</div>')
for k in ['BTC', 'ETH']:
    d = yf.get(k, {})
    if isinstance(d, dict) and d.get('price'):
        lines.append(idx_row(k, f'${d["price"]:,.2f}', d.get('pct', 0)))
lines.append(meta('Yahoo Finance v8', '2026-07-07'))
lines.append('</div>')

# === 9. News ===
lines.append('<div class="section" style="border-color:#30363d;">')
lines.append('<div class="section-title"><span class="icon">\U0001f4f0</span> \u8981\u95fb</div>')

news_sources = [
    ('\u8d22\u65b0\u7f51', '#1a1a2e', 'caixin'),
    ('\u4eba\u6c11\u7f51', '#16213e', 'people'),
    ('\u4e1c\u65b9\u8d22\u5bcc', '#1a1a2e', 'eastmoney'),
    ('FT\u4e2d\u6587\u7f51', '#16213e', 'ftchinese'),
]
for src_name, bg, src_key in news_sources:
    items = news.get(src_key, [])
    if items:
        lines.append(f'<div style="background:{bg};border-radius:6px;padding:8px;margin-bottom:8px;">')
        lines.append(f'<div style="font-size:13px;font-weight:600;color:#8b949e;margin-bottom:4px;">\u25b6 {src_name}</div>')
        for item in items[:10]:
            title = item.get('title', '')
            url = item.get('url', '#')
            lines.append(f'<div class="news-item"><a href="{url}" target="_blank" rel="noopener">{title}</a></div>')
        lines.append('</div>')

lines.append('</div>')

# === 10. Summary ===
summary_parts = []
summary_parts.append('<div class="section" style="border-color:#30363d;">')
summary_parts.append('<div class="section-title"><span class="icon">\U0001f4cb</span> \u4eca\u65e5\u603b\u7ed3</div>')
summary_parts.append('<div class="summary-text">')

sh_pct = float(sh.get('pct', 0))
sz_pct = float(sz.get('pct', 0))
cy_pct = float(cy.get('pct', 0))
hsi_p = float(hsi.get('pct', 0))
hsi_name = '\u4e0a\u6da8' if hsi_p >= 0 else '\u4e0b\u8dcc'
sp_pct = float(yf.get('S&P 500', {}).get('pct', 0))
nas_pct = float(yf.get('NASDAQ', {}).get('pct', 0))
dow_pct = float(yf.get('\u9053\u7434\u65af', {}).get('pct', 0))
nik_pct = float(yf.get('\u65e5\u7ecf225', {}).get('pct', 0))
kos_pct = float(yf.get('KOSPI', {}).get('pct', 0))
ftse_pct = float(yf.get('\u5bcc\u65f6100', {}).get('pct', 0))
gold_pct = float(yf.get('\u9ec4\u91d1', {}).get('pct', 0))
oil_pct = float(yf.get('\u539f\u6cb9', {}).get('pct', 0))
btc_pct = float(yf.get('BTC', {}).get('pct', 0))

summary_parts.append(f'<strong>\U0001f30f \u5e02\u573a\u603b\u89c8</strong><br>')
summary_parts.append(f'A\u80a1\u4e09\u5927\u6307\u6570\u5168\u7ebf\u56de\u8c03\uff08\u4e0a\u8bc1{sh_pct:+.2f}%\u3001\u6df1\u8bc1{sz_pct:+.2f}%\u3001\u521b\u4e1a\u677f{cy_pct:+.2f}%\uff09\uff1b')
summary_parts.append(f'\u6052\u6307{hsi_name}{abs(hsi_p):.2f}%\uff1b')
summary_parts.append(f'\u7f8e\u80a1\u4e09\u5927\u6307\u6570\u56de\u8c03\uff08\u6807\u666e{dow_pct:+.2f}%\u3001\u7eb3\u6307{nas_pct:+.2f}%\uff09\uff0c')
summary_parts.append(f'\u4e9a\u592a\u666e\u8dcc\uff08\u65e5\u7ecf{nik_pct:+.2f}%\u3001KOSPI{kos_pct:+.2f}%\uff09\uff0c\u6b27\u6d32\u5fae\u6da8\uff08\u5bcc\u65f6100{ftse_pct:+.2f}%\uff09\u3002')
summary_parts.append(f'\u5546\u54c1\u5206\u5316\uff1a\u9ec4\u91d1\u56de\u8c03{gold_pct:+.2f}%\uff0c\u539f\u6cb9\u5927\u6da8{oil_pct:+.2f}%\uff1b\u7f8e\u503a\u6536\u76ca\u7387\u5168\u7ebf\u62ac\u5347\uff0c\u5916\u6c47\u5e73\u7a33\u3002')
summary_parts.append('<br><br>')

summary_parts.append(f'<strong>\U0001f525 A\u80a1\u70ed\u70b9</strong><br>')
hy_names = [f'{s.get("name","")}({float(s.get("pct",0)):+.2f}%)' for s in hy_sectors[:3]]
if hy_names:
    summary_parts.append('\u884c\u4e1a\u677f\u5757\uff1a' + '\u3001'.join(hy_names) + '\u9886\u6da8\uff1b')
gn_names = [f'{s.get("name","")}({float(s.get("pct",0)):+.2f}%)' for s in gn_sectors[:3]]
if gn_names:
    summary_parts.append('\u6982\u5ff5\u677f\u5757\uff1a' + '\u3001'.join(gn_names) + '\u3002')
ff_names = [f'{s.get("name","")}({s.get("net_inflow",0):.1f}\u4ebf)' for s in fund_flow[:3]]
if ff_names:
    summary_parts.append('\u4e3b\u529b\u8d44\u91d1\u6d41\u5165\uff1a' + '\u3001'.join(ff_names) + '\u3002')
tg_names = [f'{s.get("name","")}(+{float(s.get("pct",0)):.1f}%)' for s in top_gainers[:5]]
if tg_names:
    summary_parts.append('\u6da8\u5e45\u699c\u524d\u4e94\uff1a' + '\u3001'.join(tg_names) + '\u3002')
summary_parts.append('<br><br>')

summary_parts.append(f'<strong>\U0001f4cc \u8981\u95fb\u805a\u7126</strong><br>')
seen = set()
for src_key in ['caixin', 'eastmoney']:
    for item in news.get(src_key, [])[:3]:
        t = item.get('title', '')
        if t[:15] not in seen:
            seen.add(t[:15])
            summary_parts.append('\u2022 ' + t + '<br>')
for item in news.get('ftchinese', [])[:3]:
    t = item.get('title', '')
    if t[:15] not in seen:
        seen.add(t[:15])
        summary_parts.append('\u2022 ' + t + '<br>')

summary_parts.append('</div></div>')
lines.extend(summary_parts)

# Footer
lines.append(f'''<div class="footer">
\u6570\u636e\u6765\u6e90\uff1a\u65b0\u6d6a\u8d22\u7ecf \u00b7 Yahoo Finance \u00b7 \u4e1c\u65b9\u8d22\u5bcc | \u65f6\u95f4\uff1a2026-07-07 15:00
</div>
</body>
</html>''')

html = '\n'.join(lines)

with open(f'{DIGEST}/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
import re
news_count = len(re.findall(r'<div class="news-item">', html))
caixin_count = html.count('caixin')
people_count = html.count('people')
eastmoney_count = html.count('eastmoney')
ft_count = html.count('ftchinese')

print(f'HTML_BUILT|{len(html)}bytes|{news_count}news|caixin:{caixin_count}|people:{people_count}|eastmoney:{eastmoney_count}|ft:{ft_count}')
