#!/usr/bin/env python3
"""People.cn news scraper - uses http:// protocol"""
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
url = 'http://www.people.com.cn/'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode('utf-8', errors='replace')
except Exception as e:
    html = ''

articles = []
seen_urls = set()
for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', html):
    url = m.group(1)
    title = m.group(2).strip()
    # Filter: must contain n1/ or n2/ and be long enough
    if ('n1/' in url or 'n2/' in url) and len(title) >= 10:
        # Skip navigation items
        blacklist = ['人民会客厅', '对话企业家', '更多', '频道']
        if any(b in title for b in blacklist):
            continue
        # Ensure absolute URL
        if url.startswith('//'):
            url = 'http:' + url
        elif url.startswith('/'):
            url = 'http://www.people.com.cn' + url
        elif not url.startswith('http'):
            continue
        if url not in seen_urls:
            seen_urls.add(url)
            articles.append({'title': title, 'url': url})

articles = articles[:10]

with open('/home/hermes_agent/digest/today_news_people.json', 'w') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f'People: {len(articles)} articles')
for a in articles[:3]:
    print(f'  {a["title"][:50]} -> {a["url"][:60]}')
