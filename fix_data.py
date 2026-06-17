#!/usr/bin/env python3
"""Fix Eastmoney news and get A股 sector data."""
import json, urllib.request, re, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def fetch_url_chunked(url, timeout=20):
    """Fetch with chunked reading to handle large pages."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx)
        html = b''
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            html += chunk
        return html.decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

# 1. Fix Eastmoney news - use chunked reading
result = fetch_url_chunked('https://finance.eastmoney.com/')
seen_urls = set()
eastmoney_items = []

if not result.startswith('ERROR'):
    # Pattern 1: standard eastmoney article links
    pattern = r'<a[^>]*href=["\'](https?://finance\.eastmoney\.com/a/[^"\']+)["\'][^>]*>([^<]{10,80})</a>'
    matches = re.findall(pattern, result)
    for url, title in matches:
        title = re.sub(r'<[^>]+>', '', title).strip()
        if len(title) > 8 and '更多' not in title and '&gt' not in title:
            if url not in seen_urls:
                seen_urls.add(url)
                eastmoney_items.append((title, url))
    
    # Pattern 2: broad match
    if len(eastmoney_items) < 3:
        pattern2 = r'<a[^>]*href=["\'](https?://[^"\']*eastmoney\.com[^"\']+/\d+[^"\']*)["\'][^>]*>([^<]{10,80})</a>'
        matches2 = re.findall(pattern2, result)
        for url, title in matches2:
            title = re.sub(r'<[^>]+>', '', title).strip()
            if len(title) > 8 and '更多' not in title and '&gt' not in title and '东方财富' not in title:
                if url not in seen_urls:
                    seen_urls.add(url)
                    eastmoney_items.append((title, url))

print(f"Eastmoney: {len(eastmoney_items)} items")

# Save fixed eastmoney data
if len(eastmoney_items) >= 3:
    news_path = '/home/hermes_agent/digest/today_news.json'
    with open(news_path, 'r') as f:
        news_data = json.load(f)
    news_data['eastmoney'] = [{'title': t, 'url': u} for t, u in eastmoney_items[:10]]
    with open(news_path, 'w') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print(f"Updated eastmoney in news file: {len(eastmoney_items)} items")
else:
    # Try a different eastmoney URL
    result2 = fetch_url_chunked('https://www.eastmoney.com/')
    if not result2.startswith('ERROR'):
        pattern3 = r'<a[^>]*href=["\'](https?://[^"\']*eastmoney\.com[^"\']+)["\'][^>]*>([^<]{10,80})</a>'
        matches3 = re.findall(pattern3, result2)
        for url, title in matches3:
            title = re.sub(r'<[^>]+>', '', title).strip()
            if len(title) > 8 and '更多' not in title and '&gt' not in title:
                if url not in seen_urls:
                    seen_urls.add(url)
                    eastmoney_items.append((title, url))
        print(f"After retry: Eastmoney: {len(eastmoney_items)} items")
        if len(eastmoney_items) >= 3:
            news_path = '/home/hermes_agent/digest/today_news.json'
            with open(news_path, 'r') as f:
                news_data = json.load(f)
            news_data['eastmoney'] = [{'title': t, 'url': u} for t, u in eastmoney_items[:10]]
            with open(news_path, 'w') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)

# 2. Get A data from cn_data file
with open('/home/hermes_agent/digest/today_cn_data.json', 'r') as f:
    cn_data = json.load(f)

# 3. Get A股 sector data from Eastmoney API
sectors_hy = []
try:
    url = 'https://push2.eastmoney.com/api/qt/clist/get?cb=&fid=f3&po=1&pz=10&pn=1&np=1&fltt=2&invt=2&fs=m:90+t:2&fields=f12,f14,f2,f3,f4,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    if data.get('data') and data['data'].get('diff'):
        for item in data['data']['diff'][:10]:
            sectors_hy.append({
                'name': item.get('f14', ''),
                'pct': item.get('f3', 0),
                'code': item.get('f12', '')
            })
    print(f"Sectors (hy): {len(sectors_hy)} items")
except Exception as e:
    print(f"Sectors (hy) error: {e}")

# 4. A股概念板块
sectors_gn = []
try:
    url = 'https://push2.eastmoney.com/api/qt/clist/get?cb=&fid=f3&po=1&pz=10&pn=1&np=1&fltt=2&invt=2&fs=m:90+t:3&fields=f12,f14,f2,f3,f4,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    if data.get('data') and data['data'].get('diff'):
        for item in data['data']['diff'][:10]:
            sectors_gn.append({
                'name': item.get('f14', ''),
                'pct': item.get('f3', 0),
                'code': item.get('f12', '')
            })
    print(f"Sectors (gn): {len(sectors_gn)} items")
except Exception as e:
    print(f"Sectors (gn) error: {e}")

# 5. Save sector data
cn_data['sectors_hy'] = sectors_hy
cn_data['sectors_gn'] = sectors_gn
with open('/home/hermes_agent/digest/today_cn_data.json', 'w') as f:
    json.dump(cn_data, f, ensure_ascii=False, indent=2)

# Print A index data
print(f"\nA indices: {cn_data.get('a_indices', {})}")
print(f"HSI: {cn_data.get('hsi', {})}")
print(f"FundFlow: {len(cn_data.get('fund_flow', []))}")
print(f"LimitUp: {len(cn_data.get('limit_up', []))}")
print(f"Forex: {cn_data.get('forex', {})}")
