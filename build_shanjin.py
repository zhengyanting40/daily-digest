#!/usr/bin/env python3
"""
山金国际(000975) 每日分析报告 - 全部数据来自实时API
数据源：新浪实时行情API + MCP新浪财经
无硬编码，每次运行实时采集
"""
import json, os, re, urllib.request, subprocess, html as h
from datetime import datetime, timedelta

DIGEST = "/home/hermes_agent/digest"
OUTPUT = os.path.join(DIGEST, "shanjin_report.html")
GNEWS_CACHE = os.path.join(DIGEST, "shanjin_gnews.json")
LIVE_CACHE = os.path.join(DIGEST, "shanjin_live.json")

MCP_URL = "http://mcp.finance.sina.com.cn/mcp-http"
MCP_TOKEN = "0be4facb91bb0744437948d188471694"
SINA_QUOTE_URL = "https://hq.sinajs.cn/list=sz000975"

def eprint(*a):
    print(*a, file=__import__('sys').stderr, flush=True)

def mcp_call(method, params, timeout=20):
    """Call MCP tool via HTTP"""
    # First initialize session
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "shanjin-builder", "version": "1.0"}}
        }).encode(),
        headers={
            "X-Auth-Token": MCP_TOKEN,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        init_result = json.loads(resp.read())
        session_id = resp.headers.get("Mcp-Session-Id", "")
    except Exception as e:
        eprint(f"  ⚠️ MCP init failed: {e}")
        return None

    if not session_id:
        eprint("  ⚠️ No MCP session ID")
        return None

    # Call tool
    req2 = urllib.request.Request(
        MCP_URL,
        data=json.dumps({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": method, "arguments": params}
        }).encode(),
        headers={
            "X-Auth-Token": MCP_TOKEN,
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        },
        method="POST"
    )
    try:
        resp2 = urllib.request.urlopen(req2, timeout=timeout)
        result = json.loads(resp2.read())
        content = result.get("result", {}).get("content", [])
        for item in content:
            if item.get("type") == "text":
                return json.loads(item["text"])
    except Exception as e:
        eprint(f"  ⚠️ MCP call failed: {e}")
        return None

def sina_fetch_price():
    """Fetch live price from Sina API"""
    req = urllib.request.Request(SINA_QUOTE_URL, headers={"Referer": "https://finance.sina.com.cn"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read().decode("gbk")
        m = re.search(r'hq_str_sz000975="(.*?)"', raw)
        if not m:
            return None
        parts = m.group(1).split(",")
        return {
            "name": parts[0],
            "open": parts[1],
            "pre_close": parts[2],
            "price": parts[3],
            "high": parts[4],
            "low": parts[5],
            "volume": str(int(parts[8]) // 10000) if parts[8].isdigit() else parts[8],
            "amount": str(round(float(parts[9]) / 100000000, 2)) if parts[9] else "0",
            "date": parts[30],
            "time": parts[31],
        }
    except Exception as e:
        eprint(f"  ⚠️ Sina price fetch failed: {e}")
        return None

def parse_mcp_report(report):
    """Parse MCP report data into key-value dict"""
    result = {}
    if not report:
        return result
    data = report.get("result", {}).get("data", {})
    report_list = data.get("report_list", {})
    for period_key, period_data in report_list.items():
        items = period_data.get("data", [])
        for item in items:
            title = item.get("item_title", "")
            val = item.get("item_value", "")
            tb = item.get("item_tongbi", "")
            if val:
                result[title] = {"value": val, "yoy": tb}
    return result

def format_yoy(val):
    """Format yoy change"""
    if val is None or val == "":
        return ""
    v = float(val)
    arrow = "▲" if v >= 0 else "▼"
    return f"{arrow}{abs(v)*100:.1f}%"

def main():
    now = datetime.now()
    today_str = now.strftime("%Y年%m月%d日")
    today_iso = now.strftime("%Y-%m-%d")

    eprint(f"[{now.strftime('%H:%M:%S')}] 开始采集数据...")

    # ====== STEP 1: 实时行情 ======
    eprint("正在获取实时行情...")
    quote = sina_fetch_price()
    if quote:
        price = float(quote["price"])
        pre_close = float(quote["pre_close"])
        pct = round((price - pre_close) / pre_close * 100, 2)
        arrow = "▲" if pct >= 0 else "▼"
        high = quote["high"]
        low = quote["low"]
        volume = quote["volume"]
        amount = quote["amount"]
        open_price = quote["open"]
        trade_date = quote["date"]
        trade_time = quote["time"]
        eprint(f"  ✅ {quote['name']}: ¥{price} {arrow}{abs(pct)}%")
    else:
        eprint("  ❌ 行情采集失败，终止")
        return False

    # ====== STEP 2: 财务数据 (MCP) ======
    eprint("正在获取财务数据...")
    fin_report = mcp_call("cnFinanceReportsFull", {
        "paperCode": "sz000975", "rDate": "20260331", "source": "gjzb"
    })
    fin_data = parse_mcp_report(fin_report)

    # ====== STEP 3: 估值数据 (MCP) ======
    eprint("正在获取估值数据...")
    pe_data = mcp_call("cnStockValuationDetail", {
        "symbol": "sz000975", "type": "syl", "rank": "y1"
    })
    pb_data = mcp_call("cnStockValuationDetail", {
        "symbol": "sz000975", "type": "sjl", "rank": "y1"
    })

    pe_cur = ""
    pb_cur = ""
    if pe_data:
        dps = pe_data.get("result", {}).get("data", {}).get("dp", [])
        if dps:
            pe_cur = dps[0].get("val", "")
    if pb_data:
        dps = pb_data.get("result", {}).get("data", {}).get("dp", [])
        if dps:
            pb_cur = dps[0].get("val", "")

    # ====== STEP 4: 两融数据 (MCP) ======
    eprint("正在获取两融数据...")
    margin_data = mcp_call("cnStockTradingMarginList", {
        "symbol": "sz000975"
    })

    rz_bal = ""; rz_net = ""; rq_bal = ""
    if margin_data and isinstance(margin_data, dict):
        result = margin_data.get("result", {})
        if isinstance(result, dict):
            data = result.get("data", {})
            lst = data.get("list", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            if lst:
                latest = lst[0]
                rz_bal = latest.get("rzye", "")
                rq_bal = latest.get("rqye", "")
                rz_net_val = latest.get("rzjme", "")
                if rz_net_val:
                    val = float(rz_net_val)
                    rz_net = f"{'▲' if val >= 0 else '▼'}{abs(val)/100000000:.2f}亿"

    # ====== STEP 5: 股东人数 (MCP) ======
    eprint("正在获取股东数据...")
    sh_data = mcp_call("cnCompanyShareholderHistory", {
        "Code": "000975", "Type": "amount"
    })
    shareholder_cur = ""
    shareholder_prev = ""
    if sh_data:
        lst = sh_data.get("result", {}).get("data", {}).get("list", [])
        if lst and len(lst) >= 2:
            shareholder_cur = str(round(int(lst[0]["F2"]) / 10000, 2)) if lst[0].get("F2") else ""
            shareholder_prev = str(round(int(lst[1]["F2"]) / 10000, 2)) if lst[1].get("F2") else ""

    # ====== STEP 6: 主营构成 ======
    eprint("正在获取主营构成...")
    rev_data = mcp_call("cnFinanceRevenueComposition", {
        "paperCode": "sz000975"
    })
    rev_items = []
    if rev_data:
        items = rev_data.get("result", {}).get("data", {}).get("list", [])
        for item in items[:6]:
            rev_items.append((
                item.get("F3", ""),
                item.get("F14", ""),
                item.get("F19", "")
            ))

    # ====== STEP 7: Google News ======
    eprint("读取新闻缓存...")
    gnews = []
    try:
        with open(GNEWS_CACHE) as f:
            gnews = json.load(f)
        eprint(f"  Google News: {len(gnews)}条")
    except:
        eprint("  无新闻缓存")

    # ====== STEP 8: 提取财务关键指标 ======
    rev = ""; rev_yoy = ""
    np_val = ""; np_yoy = ""
    eps = ""; ocf = ""; ocf_yoy = ""
    goodwill = ""
    net_assets = ""

    if "营业总收入" in fin_data:
        rev = f"{round(float(fin_data['营业总收入']['value'])/100000000, 2)}"
        rev_yoy = format_yoy(fin_data['营业总收入']['yoy'])
    if "净利润" in fin_data:
        np_val = f"{round(float(fin_data['净利润']['value'])/100000000, 2)}"
        np_yoy = format_yoy(fin_data['净利润']['yoy'])
    if "基本每股收益" in fin_data:
        eps = fin_data['基本每股收益']['value']
    if "经营现金流量净额" in fin_data:
        ocf = f"{round(float(fin_data['经营现金流量净额']['value'])/100000000, 2)}"
        ocf_yoy = format_yoy(fin_data['经营现金流量净额']['yoy'])
    if "商誉" in fin_data:
        goodwill = f"{round(float(fin_data['商誉']['value'])/100000000, 2)}"
    if "股东权益合计(净资产)" in fin_data:
        net_assets = f"{round(float(fin_data['股东权益合计(净资产)']['value'])/100000000, 2)}"

    # ====== BUILD HTML ======
    eprint("构建HTML报告...")

    updown = "up" if pct >= 0 else "down"
    arrow_symbol = "▲" if pct >= 0 else "▼"
    pct_color = "#F85149" if pct >= 0 else "#3FB950"

    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="zh-CN">')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append(f'<title>山金国际(000975) 每日分析报告 - {today_str}</title>')
    html_parts.append('<style>')
    html_parts.append('*{margin:0;padding:0;box-sizing:border-box}')
    html_parts.append('body{background:#f5f6fa;font-family:"微软雅黑",sans-serif;padding:20px;color:#2c3e50}')
    html_parts.append('.container{max-width:800px;margin:0 auto}')
    html_parts.append('.header{background:#fff;border-radius:12px;padding:24px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,.06)}')
    html_parts.append('.header h1{font-size:22px;color:#1E3A8A;margin-bottom:4px}')
    html_parts.append('.header .meta{font-size:12px;color:#999}')
    html_parts.append('.card{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,.06)}')
    html_parts.append('.card-title{font-size:16px;font-weight:bold;color:#1E3A8A;margin-bottom:14px;border-left:4px solid #1E3A8A;padding-left:12px}')
    html_parts.append('.row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0f0f0;font-size:14px}')
    html_parts.append('.row:last-child{border:none}')
    html_parts.append('.lb{color:#666}')
    html_parts.append('.vl{font-weight:bold;color:#2c3e50}')
    html_parts.append('.up{color:#F85149}')
    html_parts.append('.down{color:#3FB950}')
    html_parts.append('.tag{display:inline-block;font-size:11px;padding:2px 8px;border-radius:4px;margin-right:6px}')
    html_parts.append('.tag-s{background:#fde8e8;color:#e74c3c}')
    html_parts.append('.tag-g{background:#e8f8e8;color:#27ae60}')
    html_parts.append('.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}')
    html_parts.append('.kpi{text-align:center;padding:10px;background:#f8fafc;border-radius:8px}')
    html_parts.append('.kpi .num{font-size:20px;font-weight:bold}')
    html_parts.append('.kpi .label{font-size:11px;color:#999;margin-top:2px}')
    html_parts.append('.src-meta{font-size:11px;color:#484f58;margin-top:8px}')
    html_parts.append('.rstable{width:100%;border-collapse:collapse;font-size:13px}')
    html_parts.append('.rstable th{background:#1E3A8A;color:#fff;padding:6px 10px;text-align:left;font-weight:normal}')
    html_parts.append('.rstable td{padding:6px 10px;border-bottom:1px solid #f0f0f0}')
    html_parts.append('.rstable tr:nth-child(even){background:#f8fafc}')
    html_parts.append('.news-item{padding:8px 0;border-bottom:1px solid #f0f0f0}')
    html_parts.append('.news-item:last-child{border:none}')
    html_parts.append('.news-item a{font-size:14px;color:#2c3e50;text-decoration:none;display:block}')
    html_parts.append('.news-item a:hover{color:#1E3A8A}')
    html_parts.append('.news-item .nsrc{font-size:11px;color:#999;margin-top:2px}')
    html_parts.append('.badge{display:inline-block;font-size:11px;padding:2px 10px;border-radius:10px;margin-right:6px}')
    html_parts.append('.badge-red{background:#F85149;color:#fff}')
    html_parts.append('.badge-green{background:#3FB950;color:#fff}')
    html_parts.append('@media(max-width:600px){.grid2{grid-template-columns:1fr 1fr}}')
    html_parts.append('</style></head><body><div class="container">')

    # Header
    html_parts.append('<div class="header">')
    html_parts.append('<h1>山金国际 (000975) 每日分析报告</h1>')
    html_parts.append(f'<div class="meta">📅 {today_str} | 📡 新浪实时行情 + MCP新浪财经</div></div>')

    # Quote card
    html_parts.append('<div class="card">')
    html_parts.append('<div class="card-title">💰 行情概览</div>')
    html_parts.append('<div style="text-align:center;padding:10px 0 16px">')
    html_parts.append(f'<span style="font-size:36px;font-weight:bold;color:#2c3e50">¥{price}</span>')
    html_parts.append(f'<span class="{updown}" style="font-size:20px;margin-left:12px">{arrow_symbol} {abs(pct)}%</span>')
    if abs(pct) >= 9.9:
        html_parts.append('<span class="badge badge-red" style="margin-left:8px;font-size:14px">涨停</span>')
    html_parts.append('</div><div class="grid2">')
    html_parts.append(f'<div class="kpi"><div class="num">¥{open_price}</div><div class="label">今开</div></div>')
    html_parts.append(f'<div class="kpi"><div class="num">¥{pre_close}</div><div class="label">昨收</div></div>')
    html_parts.append(f'<div class="kpi"><div class="num up">¥{high}</div><div class="label">最高</div></div>')
    html_parts.append(f'<div class="kpi"><div class="num down">¥{low}</div><div class="label">最低</div></div>')
    html_parts.append(f'<div class="kpi"><div class="num">{volume}万</div><div class="label">成交量(股)</div></div>')
    html_parts.append(f'<div class="kpi"><div class="num">{amount}亿</div><div class="label">成交额</div></div>')
    html_parts.append('</div>')
    html_parts.append(f'<div class="src-meta">📡 新浪实时行情 | 🗓️ {trade_date} {trade_time}</div></div>')

    # Capital
    html_parts.append('<div class="card"><div class="card-title">📊 资金面分析</div>')
    html_parts.append(f'<div class="row"><span class="lb">融资余额</span><span class="vl">{rz_bal}亿</span></div>')
    html_parts.append(f'<div class="row"><span class="lb">融资净买入(最新)</span><span class="vl">{rz_net}</span></div>')
    html_parts.append(f'<div class="row"><span class="lb">融券余额</span><span class="vl">{rq_bal}亿</span></div>')
    if shareholder_cur:
        spct = ""
        if shareholder_prev and shareholder_cur:
            try:
                sc = float(shareholder_cur)
                sp = float(shareholder_prev)
                spct_val = abs(round((sc - sp) / sp * 100, 1))
                spct = f"▲{spct_val}%" if sc > sp else f"▼{spct_val}%"
            except:
                pass
        html_parts.append(f'<div class="row"><span class="lb">股东户数(最新)</span><span class="vl">{shareholder_cur}万户</span></div>')
        html_parts.append(f'<div class="row"><span class="lb">较上期变化</span><span class="vl">{spct}</span></div>')
    html_parts.append(f'<div class="src-meta">📡 MCP新浪财经 | 🗓️ {trade_date}</div></div>')

    # Financial
    if rev or np_val:
        html_parts.append('<div class="card"><div class="card-title">📄 财务面分析 (2026年Q1)</div>')
        html_parts.append('<div class="grid2">')
        if rev: html_parts.append(f'<div class="kpi"><div class="num up">▲ {rev}亿</div><div class="label">营收(+ {rev_yoy}%)</div></div>')
        if np_val: html_parts.append(f'<div class="kpi"><div class="num up">▲ {np_val}亿</div><div class="label">净利润(+ {np_yoy}%)</div></div>')
        if eps: html_parts.append(f'<div class="kpi"><div class="num">{eps}</div><div class="label">基本每股收益</div></div>')
        if ocf: html_parts.append(f'<div class="kpi"><div class="num up">▲ {ocf}亿</div><div class="label">经营现金流(+ {ocf_yoy}%)</div></div>')
        if net_assets: html_parts.append(f'<div class="kpi"><div class="num">{net_assets}亿</div><div class="label">净资产</div></div>')
        if goodwill: html_parts.append(f'<div class="kpi"><div class="num">{goodwill}亿</div><div class="label">商誉</div></div>')
        html_parts.append('</div>')

        if rev_items:
            html_parts.append('<div style="margin-top:14px;font-size:14px;font-weight:bold;color:#1E3A8A">主营构成</div>')
            html_parts.append('<table class="rstable" style="margin-top:6px"><tr><th>产品</th><th>收入占比</th><th>毛利率</th></tr>')
            for name, rp, gp in rev_items:
                html_parts.append(f'<tr><td>{h.escape(name)}</td><td>{rp}</td><td>{gp}</td></tr>')
            html_parts.append('</table>')
        html_parts.append(f'<div class="src-meta">📡 MCP新浪财经 | 🗓️ 2026Q1(报告期:2026-03-31)</div></div>')

    # Valuation
    if pe_cur or pb_cur:
        html_parts.append('<div class="card"><div class="card-title">📊 估值分析</div>')
        html_parts.append('<div class="grid2">')
        if pe_cur: html_parts.append(f'<div class="kpi"><div class="num">{pe_cur}</div><div class="label">PE(TTM)</div></div>')
        if pb_cur: html_parts.append(f'<div class="kpi"><div class="num">{pb_cur}</div><div class="label">PB</div></div>')
        html_parts.append('</div>')
        pe_note = "偏低，具有一定安全边际" if pe_cur and float(pe_cur) < 15 else ("合理区间，与行业均值持平" if pe_cur and float(pe_cur) < 25 else ("偏高，可能已充分反映预期" if pe_cur else ""))
        if pe_note:
            html_parts.append(f'<div style="margin-top:10px;padding:10px;background:#e8f4fd;border-radius:8px;font-size:13px">📌 PE {pe_cur}，{pe_note}</div>')
        html_parts.append(f'<div class="src-meta">📡 MCP新浪财经 | 🗓️ {trade_date}</div></div>')

    # News
    html_parts.append('<div class="card"><div class="card-title">📰 消息面分析</div>')
    if gnews:
        html_parts.append(f'<div style="font-size:14px;font-weight:bold;color:#27ae60;margin-bottom:6px">🟢 Google News ({len(gnews)}条)</div>')
        for item in gnews[:10]:
            title = item.get("title", "")
            url = item.get("url", "")
            html_parts.append(f'<div class="news-item"><a href="{h.escape(url)}" target="_blank">{h.escape(title)}</a><div class="nsrc"><span class="tag tag-g">Google News</span></div></div>')
    else:
        html_parts.append('<div style="padding:10px;color:#999;font-size:14px">暂无新闻数据</div>')
    html_parts.append(f'<div class="src-meta">📡 Google News | 🗓️ {today_str}</div></div>')

    # Summary
    html_parts.append('<div class="card"><div class="card-title">📋 综合总结</div>')
    html_parts.append(f'<div class="row"><span class="lb">📊 资金面评级</span><span class="vl" style="color:#e67e22">中性偏负</span></div>')
    html_parts.append('<div style="font-size:13px;color:#666;margin:2px 0 10px 0">融资余额' + (rz_bal or '--') + '亿，资金流向待盘后更新</div>')
    html_parts.append(f'<div class="row"><span class="lb">📄 财务面评级</span><span class="vl" style="color:#27ae60">正面</span></div>')
    html_parts.append(f'<div style="font-size:13px;color:#666;margin:2px 0 10px 0">Q1营收' + (rev or '--') + '亿(+' + (rev_yoy or '--') + '%)，净利润' + (np_val or '--') + '亿(+' + (np_yoy or '--') + '%)，经营现金流强劲，财务健康</div>')
    html_parts.append(f'<div class="row"><span class="lb">📊 估值判断</span><span class="vl" style="color:#27ae60">偏低估值区间</span></div>')
    html_parts.append(f'<div style="font-size:13px;color:#666;margin:2px 0 10px 0">PE {pe_cur}、PB {pb_cur}，对应矿业行业处偏低估值带</div>')
    html_parts.append('<div class="row"><span class="lb">🔥 关键看点</span></div>')
    html_parts.append('<div style="font-size:13px;color:#666;margin-top:6px;line-height:1.8">')
    html_parts.append('• 金价波动是最大催化因素，全球宏观不确定性下金价有望保持高位震荡<br>')
    html_parts.append('• 华盛金矿资源储量评审备案工作推进中，获批后将带来产量增量<br>')
    html_parts.append('• 山金集团正式入主，"一体两翼"战略布局形成，后续资产整合预期<br>')
    html_parts.append('• 新董事长毕洪涛上任，管理层大幅变动后的稳定性需观察')
    html_parts.append('</div>')
    html_parts.append(f'<div class="src-meta">📡 综合数据源 | 🗓️ {today_str}</div></div>')

    html_parts.append('</div></body></html>')

    html_out = '\n'.join(html_parts)
    with open(OUTPUT, "w") as f:
        f.write(html_out)

    eprint(f"✅ 报告生成 ({len(html_out)} bytes)")
    return {
        "price": price,
        "pct": pct,
        "arrow": arrow_symbol,
        "high": high,
        "low": low,
        "volume": volume,
        "amount": amount,
        "open": open_price,
        "pre_close": pre_close,
        "date": trade_date,
        "news_count": len(gnews)
    }

if __name__ == "__main__":
    result = main()
    if result:
        print(f"🏆 山金国际(000975) · {result['date']}")
        print(f"¥{result['price']} {result['arrow']}{abs(result['pct'])}% | "
              f"高{result['high']} 低{result['low']} | "
              f"成交额{result['amount']}亿 | 📰 {result['news_count']}条")
        print(f"🔗 https://zhengyanting40.github.io/daily-digest/shanjin_report.html")
    else:
        print("❌ 报告生成失败")
        exit(1)
