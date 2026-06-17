#!/usr/bin/env python3
"""Fallback data collection for A股/港股/美股/A股板块/A股资金流 when MCP is down.
Uses Yahoo Finance + Sina web API + Eastmoney web API."""
import json, urllib.request, re, ssl, time

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def fetch_url(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

def fetch_json(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

def get_yf_chart(symbol, timeout=10):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d'
    data = fetch_json(url, timeout)
    if 'error' in data:
        return None
    try:
        result = data['chart']['result'][0]
        meta = result.get('meta', {})
        quotes = result.get('indicators', {}).get('quote', [{}])[0]
        closes = quotes.get('close', [])
        current_close = next((c for c in closes if c is not None), None)
        prev_close = meta.get('chartPreviousClose') or meta.get('previousClose')
        if current_close is None:
            current_close = meta.get('regularMarketPrice')
        if current_close and prev_close:
            change = current_close - prev_close
            pct = (change / prev_close) * 100
            return {'price': round(current_close, 2), 'change': round(change, 2), 'pct': round(pct, 2)}
        return None
    except Exception:
        return None

# 1. A股指数 via Yahoo Finance
a_shares = {
    '上证指数': '000001.SS',
    '深证成指': '399001.SZ',
    '创业板指': '399006.SZ'
}
a_indices = {}
for name, sym in a_shares.items():
    r = get_yf_chart(sym)
    if r:
        a_indices[name] = r

# 2. 恒生指数 via YF
hsi = get_yf_chart('^HSI')
hsi_data = {'恒生指数': hsi} if hsi else {}

# 3. 港股领涨板块 via Sina web API
hk_plates = []
try:
    hk_data = fetch_url('https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/rhk/index.phtml', timeout=10)
    if hk_data:
        # Parse 港股板块
        pattern = r'<a[^>]*href="[^"]*[?&]node=rhk_(\w+)[^"]*"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, hk_data)
        for code, name in matches[:10]:
            hk_plates.append({'code': f'rhk_{code}', 'name': name})
except Exception as e:
    pass

# 4. A股行业板块排行 via Sina
sectors_hy = []
try:
    hy_data = fetch_url('https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/hy/index.phtml', timeout=10)
    if hy_data:
        # Try the plain table format
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', hy_data, re.DOTALL)
        for row in rows[:15]:
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(tds) >= 3:
                name_match = re.search(r'<a[^>]*>([^<]+)</a>', tds[0])
                pct_match = re.search(r'([+-]?\d+\.?\d*)%?', tds[1] if len(tds) > 1 else '')
                if name_match and pct_match:
                    sectors_hy.append({'name': name_match.group(1).strip(), 'pct': pct_match.group(1)})
except Exception as e:
    pass

# 5. A股概念板块排行 via Sina (alternative if above fails)
sectors_gn = []
try:
    gn_page = fetch_url('https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/gn/index.phtml', timeout=10)
    if gn_page:
        # Try regex pattern
        blocks = re.findall(r'<a[^>]*href="[^"]*[?&]node=gn_(\w+)[^"]*"[^>]*>([^<]+)</a>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>', gn_page)
        for code, name, pct in blocks[:10]:
            sectors_gn.append({'code': f'gn_{code}', 'name': name.strip(), 'pct': pct.strip()})
except Exception as e:
    pass

# 6. A股资金流 from Eastmoney
fund_flow = []
try:
    # Eastmoney fund flow API
    url = 'https://push2.eastmoney.com/api/qt/clist/get?cb=&fid=f62&po=1&pz=5&pn=1&np=1&fltt=2&invt=2&fs=m:90+t:3&fields=f12,f14,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124'
    ff_data = fetch_json(url, timeout=10)
    if 'data' in ff_data and ff_data['data'] and ff_data['data'].get('diff'):
        for item in ff_data['data']['diff'][:5]:
            fund_flow.append({
                'name': item.get('f14', ''),
                'net_inflow': item.get('f62', 0),
                'code': item.get('f12', '')
            })
except Exception as e:
    pass

# 7. A股涨停/连板 from Sina web
limit_up = []
try:
    # Try Sina limit-up pool
    lu_url = 'https://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/lb/index.phtml'
    lu_data = fetch_url(lu_url, timeout=10)
    if lu_data:
        items = re.findall(r'<tr[^>]*>.*?<a[^>]*>([^<]+)</a>.*?<td[^>]*>([^<]*)</td>', lu_data, re.DOTALL)
        for name, days in items[:15]:
            limit_up.append({'name': name.strip(), 'days': days.strip()})
except:
    pass

# 8. 外汇 via MCP alternative - use Sina forex
fx = {}
try:
    # Get from YF forex pairs
    pairs = {
        'EUR/USD': 'EURUSD=X',
        'USD/JPY': 'USDJPY=X',
        'USD/CNY': 'CNY=X',  # Actually USDCNY
        'USD/HKD': 'USDHKD=X'
    }
    for name, sym in pairs.items():
        r = get_yf_chart(sym)
        if r:
            fx[name] = r
except:
    pass

result = {
    'a_indices': a_indices,
    'hsi': hsi_data,
    'hk_plates': hk_plates,
    'sectors_hy': sectors_hy,
    'sectors_gn': sectors_gn,
    'fund_flow': fund_flow,
    'limit_up': limit_up,
    'forex': fx,
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
}

with open('/home/hermes_agent/digest/today_cn_data.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"CN data saved. A:{len(a_indices)} HK:{len(hsi_data)} Sectors-hy:{len(sectors_hy)} Sectors-gn:{len(sectors_gn)} FundFlow:{len(fund_flow)} LimitUp:{len(limit_up)} Forex:{len(fx)}")
