#!/usr/bin/env python3
"""Caixin news scraper"""
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
url = 'https://www.caixin.com/'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode('utf-8', errors='replace')
except Exception as e:
    # Try finance.caixin.com as backup
    try:
        url2 = 'https://finance.caixin.com/'
        req2 = urllib.request.Request(url2, headers=headers)
        with urllib.request.urlopen(req2, timeout=20) as r:
            html = r.read().decode('utf-8', errors='replace')
    except:
        html = ''

articles = []
seen_urls = set()
for m in re.finditer(r'<a[^>]*href="(https?://[^"]*caixin[^"]*)"[^>]*>([^<]+)</a>', html):
    url = m.group(1)
    title = m.group(2).strip()
    if len(title) > 8 and 'promote' not in url.lower() and 'en.' not in url and 'claw' not in url and 'data' not in url:
        if url not in seen_urls:
            seen_urls.add(url)
            articles.append({'title': title, 'url': url})

articles = articles[:10]

with open('/home/hermes_agent/digest/today_news_caixin.json', 'w') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f'Caixin: {len(articles)} articles')
for a in articles[:3]:
    print(f'  {a["title"][:50]}')
