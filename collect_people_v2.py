#!/usr/bin/env python3
"""Better people.cn scraper - extract real news articles"""
import json, urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=20, context=ctx)
    data = b''
    while True:
        chunk = resp.read(65536)
        if not chunk: break
        data += chunk
    return data.decode('utf-8', errors='replace')

items = []
seen_urls = set()
blacklist = ['人民会客厅', '对话企业家', '更多', '频道']

sources = [
    'http://www.people.com.cn/',
    'http://politics.people.com.cn/',
    'http://finance.people.com.cn/',
]

for source_url in sources:
    try:
        html = fetch(source_url)
        # Match links with n1/ or n2/ patterns containing dates
        for m in re.finditer(r'<a[^>]*href="(http://[^"]*people\.com\.cn/(?:n[12]/[a-z0-9]+/\d{4}/\d+/\d+/[^"]+))"[^>]*>([^<]+)</a>', html):
            url = m.group(1)
            title = m.group(2).strip().replace('\n', ' ')
            if len(title) < 10: continue
            if any(b in title for b in blacklist): continue
            if url in seen_urls: continue
            seen_urls.add(url)
            items.append((title, url))
    except Exception as e:
        print(f"  Error {source_url}: {e}")

items = items[:10]
result = [{'title': t, 'url': u} for t, u in items]
with open('/home/hermes_agent/digest/people_news.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"People news: {len(result)} items")
for t, u in result:
    print(f"  ✅ {t[:50]}")
