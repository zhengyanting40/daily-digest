#!/usr/bin/env python3
"""Eastmoney news scraper with chunked reading"""
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
url = 'https://finance.eastmoney.com/'
req = urllib.request.Request(url, headers=headers)
html = ''
try:
    r = urllib.request.urlopen(req, timeout=20)
    while True:
        chunk = r.read(65536)
        if not chunk:
            break
        html += chunk.decode('utf-8', errors='replace')
except Exception as e:
    html = ''

articles = []
seen_urls = set()
for m in re.finditer(r'<a[^>]*href="(https?://[^"]*eastmoney[^"]*)"[^>]*>([^<]+)</a>', html, re.I):
    url = m.group(1)
    title = m.group(2).strip()
    if len(title) > 8 and '更多' not in title and '&gt' not in title:
        if url not in seen_urls:
            seen_urls.add(url)
            articles.append({'title': title, 'url': url})

articles = articles[:10]

with open('/home/hermes_agent/digest/today_news_eastmoney.json', 'w') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f'Eastmoney: {len(articles)} articles')
for a in articles[:3]:
    print(f'  {a["title"][:50]}')
