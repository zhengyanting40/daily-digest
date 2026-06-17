#!/usr/bin/env python3
"""Better people.cn news scraper using http://"""
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
seen = set()

# Try politics.people.com.cn
try:
    html = fetch('http://politics.people.com.cn/')
    # Find real news links with dates like /n1/2026/
    for m in re.finditer(r'<a[^>]*href="(http://politics\.people\.com\.cn/n1/2026/\d+/\d+/[^"]*)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        if len(title) > 8 and title not in seen:
            items.append((title, url))
            seen.add(title)
except: pass

# Try www.people.com.cn with GB/ format
try:
    html = fetch('http://www.people.com.cn/')
    for m in re.finditer(r'<a[^>]*href="(http://[^.]+\.people\.com\.cn/GB/\d+/\d+/\d+/\d+\.html)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        blacklist = ['人民会客厅', '对话企业家', '更多', '人民网', '频道']
        skip = any(b in title for b in blacklist)
        if len(title) > 8 and not skip and title not in seen:
            items.append((title, url))
            seen.add(title)
except: pass

# Also try finance.people.com.cn
try:
    html = fetch('http://finance.people.com.cn/')
    for m in re.finditer(r'<a[^>]*href="(http://finance\.people\.com\.cn/n1/2026/\d+/\d+/[^"]*)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        if len(title) > 8 and title not in seen:
            items.append((title, url))
            seen.add(title)
except: pass

items = items[:10]
result = [{'title': t, 'url': u} for t, u in items]

with open('/home/hermes_agent/digest/people_news.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"People news: {len(result)} items")
for t, u in items[:5]:
    print(f"  - {t[:40]}...")
