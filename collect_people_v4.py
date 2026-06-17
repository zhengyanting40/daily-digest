#!/usr/bin/env python3
"""Scrape people.cn - fixed regex"""
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

html = fetch('http://www.people.com.cn/')
# Match any people.com.cn n1/ or n2/ pattern with article structure
for m in re.finditer(r'<a[^>]*href="(http://[^"]+people\.com\.cn/n[12]/[^"]+)"[^>]*>([^<]+)</a>', html):
    url = m.group(1)
    title = m.group(2).strip().replace('\n', ' ')
    # Filter: must be news article (has /n1/ or /n2/ with year pattern)
    if not re.search(r'/n[12]/\w+/\d{4}/\d+/', url): continue
    if len(title) < 10: continue
    blacklist = ['人民会客厅', '对话企业家', '更多', '频道', '高考']
    if any(b in title for b in blacklist): continue
    if url in seen_urls: continue
    seen_urls.add(url)
    items.append((title, url))

# Also try finance
try:
    html2 = fetch('http://finance.people.com.cn/')
    for m in re.finditer(r'<a[^>]*href="(http://[^"]+people\.com\.cn/n[12]/[^"]+)"[^>]*>([^<]+)</a>', html2):
        url = m.group(1)
        title = m.group(2).strip().replace('\n', ' ')
        if not re.search(r'/n[12]/\w+/\d{4}/\d+/', url): continue
        if len(title) < 10: continue
        if any(b in title for b in blacklist): continue
        if url in seen_urls: continue
        seen_urls.add(url)
        items.append((title, url))
except: pass

items = items[:10]
result = [{'title': t, 'url': u} for t, u in items]
with open('/home/hermes_agent/digest/people_news.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"People news: {len(result)} items")
for t, u in result:
    print(f"  ✅ {t[:60]}")
