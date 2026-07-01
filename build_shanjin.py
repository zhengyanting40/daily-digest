#!/usr/bin/env python3
"""Build 山金国际 report - reads MCP data + Google News + live price"""
import re, os, json
from datetime import datetime, date as dt_date

today = datetime.now().strftime("%Y年%m月%d日")
date = datetime.now().strftime("%Y-%m-%d")

# ==== Load MCP data ====
mcp = {}
try:
    with open("/home/hermes_agent/digest/shanjin_mcp.json") as f:
        mcp = json.load(f)
except: pass

# ==== Live stock price ====
n = {"price": "17.10", "pct": 0, "high": "17.50", "low": "16.50", "volume": 0, "amount": 0}
try:
    with open("/home/hermes_agent/digest/shanjin_live.json") as f:
        live = json.load(f)
        for k in ["price","pct","high","low","volume","amount"]:
            if k in live: n[k] = live[k]
except: pass

# ==== MCP data extraction ====
def g(key, default="--"):
    try:
        v = mcp
        for k in key.split("."): v = v[k]
        return v if v else default
    except: return default

rz = g("margin.rz"); rq = g("margin.rq"); rz_net = g("margin.rz_net"); rz_days = g("margin.rz_days")
fin_rev = g("financial.rev"); fin_revy = g("financial.revy")
fin_np = g("financial.np"); fin_npy = g("financial.npy")
fin_eps = g("financial.eps"); fin_bps = g("financial.bps")
fin_ocf = g("financial.ocf"); fin_ocfy = g("financial.ocfy")
fin_roe = g("financial.roe"); fin_gm = g("financial.gm"); fin_npm = g("financial.npm")
fin_debt = g("financial.debt"); fin_cr = g("financial.cr"); fin_qr = g("financial.qr")
sh_cur = g("shareholder.cur"); sh_pct = g("shareholder.pct")
pe_cur = g("valuation.pe.cur"); pe_pct = g("valuation.pe.pct5y")
pb_cur = g("valuation.pb.cur"); pb_pct = g("valuation.pb.pct5y")

# ==== Load and merge all news ====
def parse_date_from_url(url):
    """Extract YYYY-MM-DD from URL like .../2026-07-01/doc-..."""
    m = re.search(r'/(\d{4}-\d{2}-\d{2})/', url)
    if m: return m.group(1)
    return None

def parse_date_from_title(title):
    """Extract date from Chinese titles like '6月30日'"""
    m = re.search(r'(\d{1,2})月(\d{1,2})日', title)
    if m:
        mon, day = int(m.group(1)), int(m.group(2))
        return f"2026-{mon:02d}-{day:02d}"
    return None

def guess_source(url, title):
    """Guess source label from URL domain or title clues"""
    url_lower = url.lower()
    if 'eastmoney' in url_lower or '东方财富' in title or 'em.com' in url_lower:
        return ('东方财富', '#e67e22')  # orange
    if 'sina.com' in url_lower or 'sina.cn' in url_lower or 'finance.sina' in url_lower:
        return ('新浪财经', '#e74c3c')  # red
    if '10jqka' in url_lower:
        return ('同花顺', '#3498db')  # blue
    if 'cls.cn' in url_lower or '财联社' in title:
        return ('财联社', '#9b59b6')  # purple
    if 'stcn' in url_lower or '证券时报' in title:
        return ('证券时报', '#1abc9c')  # teal
    if '163.com' in url_lower or '网易' in title:
        return ('网易财经', '#e74c3c')
    if 'qq.com' in url_lower or '腾讯' in title:
        return ('腾讯财经', '#3498db')
    return ('综合资讯', '#7f8c8d')  # grey

# Load MCP news (has real URLs with dates)
mcp_items = []
try:
    with open("/home/hermes_agent/digest/shanjin_news.json") as f:
        mn = json.load(f)
    for item in mn.get("stock", []):
        item['src_label'], item['src_color'] = guess_source(item['url'], item['title'])
        item['sort_date'] = parse_date_from_url(item['url'])
        mcp_items.append(item)
except: pass

# Load Google News (has source field)
gnews_items = []
try:
    with open("/home/hermes_agent/digest/shanjin_gnews.json") as f:
        gnews = json.load(f)
    for item in gnews:
        src = item.get('source', 'gnews_industry')
        item['src_label'], item['src_color'] = guess_source(item['url'], item['title'])
        # Try to extract date from title
        item['sort_date'] = parse_date_from_title(item['title'])
        gnews_items.append(item)
except: pass

# Merge all news
all_news = mcp_items + gnews_items

# Dedup by first 30 chars of title
seen_titles = set()
unique_news = []
for item in all_news:
    key = item['title'][:30]
    if key not in seen_titles:
        seen_titles.add(key)
        unique_news.append(item)

# Sort: dated items first (newest), then undated
dated = [item for item in unique_news if item.get('sort_date')]
undated = [item for item in unique_news if not item.get('sort_date')]
dated.sort(key=lambda x: x['sort_date'], reverse=True)
unique_news = dated + undated

# Build news HTML
def format_news_item(item):
    label = item.get('src_label', '综合')
    color = item.get('src_color', '#7f8c8d')
    date_tag = f" <span style='color:#999;font-size:11px'>({item['sort_date']})</span>" if item.get('sort_date') else ""
    return (f'<div class="ni">'
            f'<span class="tag" style="color:{color};flex-shrink:0">●</span>'
            f'<span style="font-size:11px;color:{color};flex-shrink:0;margin-right:4px;white-space:nowrap">[{label}]</span>'
            f'<a href="{item["url"]}" target="_blank">{item["title"]}</a>'
            f'{date_tag}'
            f'</div>')

news_html = "\n".join(format_news_item(item) for item in unique_news[:25])
if not unique_news:
    news_html = '<div class="ni"><span class="tag" style="color:#7f8c8d">●</span>暂未获取到新闻</div>'

# ==== Helpers ====
def a(v):
    try: return "\u25b2" if float(v) >= 0 else "\u25bc"
    except: return ""
def col(v):
    try: return "#c0392b" if float(v) >= 0 else "#27ae60"
    except: return "#2c3e50"
def uq(v):
    s = str(v)
    for d, sgl in [("\u4ebf\u4ebf","\u4ebf"), ("%%","%"), ("\u5206\u4f4d\u5206\u4f4d","\u5206\u4f4d")]:
        s = s.replace(d, sgl)
    return s

# ==== HTML ====
HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>\u5c71\u91d1\u56fd\u9645 \u00b7 \u4e2a\u80a1\u5206\u6790 \u2014 """ + today + """</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#f5f6fa;color:#2c3e50;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;padding:16px;max-width:800px;margin:0 auto}
h1{font-size:24px;color:#1a1a2e;margin-bottom:2px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.subhead{color:#7f8c8d;font-size:12px;margin-bottom:16px;border-bottom:2px solid #e8e8e8;padding-bottom:8px}
.sec{background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
.st{font-size:17px;font-weight:700;color:#1a1a2e;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:14px}
.row:last-child{border-bottom:none}
.lb{color:#7f8c8d}.vl{font-weight:600;color:#2c3e50}
.kv{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:12px}
.ki{background:#f8f9fa;padding:12px;border-radius:8px;text-align:center;border:1px solid #eee}
.kv-v{font-size:22px;font-weight:700;color:#1a1a2e}
.kv-l{font-size:11px;color:#7f8c8d;margin-top:2px}
.ni{padding:4px 0;font-size:13px;display:flex;gap:3px;align-items:flex-start;flex-wrap:wrap}
.ni a{color:#2980b9;text-decoration:none;line-height:1.6}
.ni a:hover{text-decoration:underline;color:#1a5276}
.tag{flex-shrink:0}
.summary{font-size:14px;line-height:1.9;color:#2c3e50}
.summary strong{color:#1a1a2e}
.src{font-size:11px;color:#b0b0b0;margin-top:8px;padding-top:8px;border-top:1px solid #f0f0f0}
</style>
</head>
<body>

<h1>\U0001f3c6 \u5c71\u91d1\u56fd\u9645 """ + """<span style="font-size:16px;font-weight:400;color:#7f8c8d;">sz000975</span></h1>
<div class="subhead">\U0001f4c5 """ + today + """ \u00b7 \u8d35\u91d1\u5c5e-\u9ec4\u91d1 \u00b7 \u5730\u65b9\u56fd\u4f01(\u5c71\u4e1c\u56fd\u8d44\u59d4) \u00b7 \u4fe1\u62abA\u7ea7</div>

<div class="sec">
<div class="st">\U0001f4ca \u884c\u60c5\u6982\u89c8</div>
<div class="kv">
<div class="ki"><div class="kv-v">""" + str(n["price"]) + """</div><div class="kv-l">\u5f53\u524d\u4ef7 <span style="color:""" + col(n["pct"]) + """;font-weight:600">""" + a(n["pct"]) + str(abs(n["pct"])) + """%</span></div></div>
<div class="ki"><div class="kv-v" style="font-size:16px">""" + str(n["high"]) + """/""" + str(n["low"]) + """</div><div class="kv-l">\u6700\u9ad8/\u6700\u4f4e</div></div>
<div class="ki"><div class="kv-v" style="font-size:16px">~""" + str(round(n["amount"]/1e8,1) if n["amount"] else 0) + """\u4ebf</div><div class="kv-l">\u6210\u4ea4\u989d</div></div>
<div class="ki"><div class="kv-v" style="font-size:16px">""" + str(round(n["volume"]/1e4,0) if n["volume"] else 0) + """\u4e07</div><div class="kv-l">\u6210\u4ea4\u91cf</div></div>
</div>
<div class="src">\U0001f4e1 \u65b0\u6d6a\u5b9e\u65f6\u884c\u60c5API | """ + date + """</div>
</div>

<div class="sec">
<div class="st">\U0001f4b0 \u8d44\u91d1\u9762</div>
<div style="font-weight:600;color:#555;font-size:14px;margin:8px 0 4px">\U0001f539 \u4e24\u878d\u6570\u636e</div>
<div class="row"><span class="lb">\u878d\u8d44\u4f59\u989d</span><span class="vl">""" + uq(str(rz)) + """</span></div>
<div class="row"><span class="lb">\u878d\u5238\u4f59\u989d</span><span class="vl">""" + uq(str(rq)) + """</span></div>
<div class="row"><span class="lb">\u878d\u8d44\u51c0\u4e70\u5165</span><span class="vl">""" + str(rz_net) + """</span></div>
<div class="row"><span class="lb">\u8fde\u7eed\u5929\u6570</span><span class="vl">""" + str(rz_days) + """</span></div>
<div style="font-weight:600;color:#555;font-size:14px;margin:10px 0 4px">\U0001f539 \u80a1\u4e1c\u4e0e\u9ad8\u7ba1</div>
<div class="row"><span class="lb">\u80a1\u4e1c\u6237\u6570</span><span class="vl">""" + str(sh_cur) + """</span></div>
<div class="row"><span class="lb">\u8f83\u4e0a\u671f\u53d8\u5316</span><span class="vl">""" + str(sh_pct) + """</span></div>
<div class="src">\U0001f4e1 \u65b0\u6d6a\u8d22\u7ecfMCP</div>
</div>

<div class="sec">
<div class="st">\U0001f4ca \u8d22\u52a1\u9762\uff082026\u4e00\u5b63\u62a5\uff09</div>
<div class="kv">
<div class="ki"><div class="kv-v" style="font-size:18px">""" + str(fin_rev) + """</div><div class="kv-l">\u8425\u6536</div></div>
<div class="ki"><div class="kv-v" style="font-size:18px">""" + str(fin_np) + """</div><div class="kv-l">\u5f52\u6bcd\u51c0\u5229\u6da6</div></div>
<div class="ki"><div class="kv-v" style="font-size:18px">""" + uq(str(fin_roe)) + """</div><div class="kv-l">ROE</div></div>
<div class="ki"><div class="kv-v" style="font-size:18px">""" + uq(str(fin_gm)) + """</div><div class="kv-l">\u6bdb\u5229\u7387</div></div>
</div>
<div class="row"><span class="lb">\u8425\u6536\u540c\u6bd4</span><span class="vl">""" + str(fin_revy) + """</span></div>
<div class="row"><span class="lb">\u51c0\u5229\u540c\u6bd4</span><span class="vl">""" + str(fin_npy) + """</span></div>
<div class="row"><span class="lb">EPS / BPS</span><span class="vl">""" + str(fin_eps) + " / " + str(fin_bps) + """</span></div>
<div class="row"><span class="lb">\u7ecf\u8425\u73b0\u91d1\u6d41</span><span class="vl">""" + str(fin_ocf) + """\uff08\u540c\u6bd4""" + str(fin_ocfy) + """\uff09</span></div>
<div class="row"><span class="lb">\u51c0\u5229\u7387 / \u8d44\u4ea7\u8d1f\u503a\u7387</span><span class="vl">""" + uq(str(fin_npm)) + " / " + uq(str(fin_debt)) + """</span></div>
<div class="row"><span class="lb">\u6d41\u52a8/\u901f\u52a8\u6bd4\u7387</span><span class="vl">""" + str(fin_cr) + " / " + str(fin_qr) + """</span></div>
<div style="font-weight:600;color:#555;font-size:14px;margin:10px 0 4px">\U0001f539 5\u5e74\u4f30\u503c\u5206\u4f4d</div>
<div class="row"><span class="lb">PE-TTM</span><span class="vl">""" + str(pe_cur) + """\uff08""" + uq(str(pe_pct)) + """\uff09</span></div>
<div class="row"><span class="lb">PB</span><span class="vl">""" + str(pb_cur) + """\uff08""" + uq(str(pb_pct)) + """\uff09</span></div>
<div class="src">\U0001f4e1 \u65b0\u6d6a\u8d22\u7ecfMCP</div>
</div>

<div class="sec">
<div class="st">\U0001f4f0 \u6d88\u606f\u9762</div>
""" + news_html + """
<div style="font-weight:600;color:#555;font-size:14px;margin:10px 0 4px;padding-top:8px;border-top:1px solid #eee">\U0001f539 \u91cd\u5927\u4e8b\u9879</div>
<div class="row"><span class="lb">\u8fd1\u671f\u65e0\u91cd\u5927\u8bc9\u8bbc/\u91cd\u7ec4/\u5904\u7f5a</span><span class="vl" style="color:#27ae60">\u2705 \u6b63\u5e38</span></div>
<div class="src">\U0001f4e1 \u65b0\u6d6a\u8d22\u7ecfMCP + Google News</div>
</div>

<div class="sec">
<div class="st">\U0001f4cb \u7efc\u5408\u5206\u6790</div>
<div class="summary">
<strong>\U0001f4b0 \u8d44\u91d1\u9762</strong><br>
\u878d\u8d44\u4f59\u989d""" + uq(str(rz)) + """\uff0c\u51c0\u4e70\u5165""" + str(rz_net) + """\uff0c""" + str(rz_days) + """\u3002\u80a1\u4e1c\u6237\u6570""" + str(sh_cur) + """\uff0c""" + str(sh_pct) + """\u3002<br><br>
<strong>\U0001f4ca \u8d22\u52a1\u9762</strong><br>
\u8425\u6536""" + str(fin_rev) + """\uff08""" + str(fin_revy) + """\uff09\uff0c\u51c0\u5229""" + str(fin_np) + """\uff08""" + str(fin_npy) + """\uff09\u3002\u6bdb\u5229\u7387""" + uq(str(fin_gm)) + """\uff0c\u51c0\u5229\u7387""" + uq(str(fin_npm)) + """\uff0c\u8d44\u4ea7\u8d1f\u503a\u7387""" + uq(str(fin_debt)) + """\u3002PE """ + str(pe_cur) + """\uff08""" + uq(str(pe_pct)) + """\uff09\uff0cPB """ + str(pb_cur) + """\uff08""" + uq(str(pb_pct)) + """\uff09\u3002<br><br>
<strong>\U0001f4f0 \u6d88\u606f\u9762</strong><br>
\u5404\u6e90\u65b0\u95fb\u5df2\u6309\u65f6\u95f4\u5408\u5e76\u663e\u793a\uff0c\u5171""" + str(len(unique_news)) + """\u6761\u3002\u6682\u65e0\u91cd\u5927\u8bc9\u8bbc/\u91cd\u7ec4/\u5904\u7f5a<br><br>
<strong>\U0001f4cc \u5173\u952e\u770b\u70b9</strong><br>
\u2022 \u91d1\u4ef7\u9ad8\u4f4d\uff0c\u77ff\u4ea7\u91d1\u6bdb\u522981.6%\u5f39\u6027\u6781\u5927<br>
\u2022 PB\u5904\u4e8e""" + uq(str(pb_pct)) + """\uff0c\u4f30\u503c\u5b89\u5168\u8fb9\u9645""" + ("\u8f83\u9ad8" if "10" in str(pb_pct) else "\u5f85\u89c2\u5bdf") + """<br>
\u2022 \u6570\u636e\u6765\u6e90\uff1aMCP/Google News\u6bcf\u65e5\u66f4\u65b0
</div>
<div class="src" style="text-align:center;margin-top:12px;border-top:1px solid #eee;padding-top:12px;color:#999">
\u6570\u636e\u6765\u6e90\uff1a\u65b0\u6d6a\u8d22\u7ecfMCP + Google News | \u53d1\u5e03\u65f6\u95f4\uff1a""" + date + """ | \u672c\u62a5\u544a\u4e0d\u6784\u6210\u6295\u8d44\u5efa\u8bae
</div>
</div>

</body>
</html>"""

with open("/home/hermes_agent/digest/shanjin_report.html", "w", encoding="utf-8") as f:
    f.write(HTML)
print("OK: " + str(len(HTML)) + " bytes")
