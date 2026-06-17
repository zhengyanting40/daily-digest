#!/usr/bin/env python3
"""Collect news from multiple sources: caixin, people, eastmoney, ftchinese"""
import urllib.request, re, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

all_news = []

# 1. 财新网
caixin_news = []
try:
    req = urllib.request.Request('https://www.caixin.com/', headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode('utf-8', errors='replace')
    seen = set()
    for m in re.finditer(r'<a[^>]*href="(https?://[^"]*caixin[^"]*)"[^>]*>([^<]+)</a>', html):
        url, title = m.group(1), m.group(2).strip()
        title = re.sub(r'\s+', ' ', title)
        if len(title) > 8 and url not in seen and 'promote' not in url and 'en.' not in url and 'claw' not in url:
            seen.add(url)
            caixin_news.append({'title': title, 'url': url})
    print(f"财新网: {len(caixin_news)} articles")
except Exception as e:
    print(f"财新网 ERROR: {e}")
    # Fallback to finance.caixin.com
    try:
        req = urllib.request.Request('http://finance.caixin.com/', headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode('utf-8', errors='replace')
        seen = set()
        for m in re.finditer(r'<a[^>]*href="(https?://[^"]*caixin[^"]*)"[^>]*>([^<]+)</a>', html):
            url, title = m.group(1), m.group(2).strip()
            title = re.sub(r'\s+', ' ', title)
            if len(title) > 8 and url not in seen and 'promote' not in url:
                seen.add(url)
                caixin_news.append({'title': title, 'url': url})
        print(f"财新网(fallback): {len(caixin_news)} articles")
    except Exception as e2:
        print(f"财新网 fallback ERROR: {e2}")
all_news.append({'source': 'caixin', 'items': caixin_news[:8]})

# 2. 人民网 (use http://)
people_news = []
try:
    req = urllib.request.Request('http://www.people.com.cn/', headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode('utf-8', errors='replace')
    seen = set()
    for m in re.finditer(r'<a[^>]*href="(http[^"]*)"[^>]*>([^<]+)</a>', html):
        url, title = m.group(1), m.group(2).strip()
        title = re.sub(r'\s+', ' ', title)
        if ('n1/' in url or 'n2/' in url) and len(title) >= 10:
            if '人民会客厅' not in title and '对话企业家' not in title and '更多' not in title:
                if url not in seen:
                    seen.add(url)
                    people_news.append({'title': title, 'url': url})
    print(f"人民网: {len(people_news)} articles")
except Exception as e:
    print(f"人民网 ERROR: {e}")
all_news.append({'source': 'people', 'items': people_news[:10]})

# 3. 东方财富
eastmoney_news = []
try:
    req = urllib.request.Request('https://finance.eastmoney.com/', headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        html = ''
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            html += chunk.decode('utf-8', errors='replace')
    seen = set()
    for m in re.finditer(r'<a[^>]*href="(https?://[^"]*(?:eastmoney|emoney)[^"]*/(?:a|news|content)/\d+[^"]*)"[^>]*>([^<]+)</a>', html):
        url, title = m.group(1), m.group(2).strip()
        title = re.sub(r'\s+', ' ', title)
        if len(title) > 8 and '更多' not in title and '&gt' not in title and url not in seen:
            seen.add(url)
            eastmoney_news.append({'title': title, 'url': url})
    if len(eastmoney_news) < 3:
        # Try broader pattern
        seen2 = set()
        for m in re.finditer(r'<a[^>]*href="(https?://[^"]*eastmoney[^"]*)"[^>]*>([^<]+)</a>', html):
            url, title = m.group(1), m.group(2).strip()
            title = re.sub(r'\s+', ' ', title)
            if len(title) > 8 and '更多' not in title and url not in seen2:
                seen2.add(url)
                if url not in seen:
                    eastmoney_news.append({'title': title, 'url': url})
    print(f"东方财富: {len(eastmoney_news)} articles")
except Exception as e:
    print(f"东方财富 ERROR: {e}")
all_news.append({'source': 'eastmoney', 'items': eastmoney_news[:8]})

# 4. FT中文网
ft_news = []
try:
    req = urllib.request.Request('https://www.ftchinese.com/', headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode('utf-8', errors='replace')
    seen = set()
    for m in re.finditer(r'<a[^>]*href="(https?://[^"]*ftchinese[^"]*/story/\d+[^"]*)"[^>]*>([^<]+)</a>', html):
        url, title = m.group(1), m.group(2).strip()
        title = re.sub(r'\s+', ' ', title)
        if len(title) > 8 and url not in seen:
            seen.add(url)
            ft_news.append({'title': title, 'url': url})
    print(f"FT中文网: {len(ft_news)} articles")
except Exception as e:
    print(f"FT中文网 ERROR: {e}")
all_news.append({'source': 'ft', 'items': ft_news[:10]})

# Save
with open('/home/hermes_agent/digest/today_news.json', 'w', encoding='utf-8') as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)
print(f"\nTotal: caixin={len(caixin_news[:8])}, people={len(people_news[:10])}, eastmoney={len(eastmoney_news[:8])}, ft={len(ft_news[:10])}")
