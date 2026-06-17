#!/usr/bin/env python3
"""FT Chinese news scraper - dual regex mode"""
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
url = 'https://www.ftchinese.com/'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode('utf-8', errors='replace')
except:
    html = ''

articles = []
seen_urls = set()

# Mode 1: Exact ftchinese story links
for m in re.finditer(r'<a[^>]*href="(https?://www\.ftchinese\.com/story/\d+[^"]*)"[^>]*>([^<]+)</a>', html):
    url = m.group(1).split('?')[0]
    title = m.group(2).strip()
    if len(title) > 6 and url not in seen_urls:
        seen_urls.add(url)
        articles.append({'title': title, 'url': url})

# Mode 2: Loose match for partial URLs
if len(articles) < 8:
    for m in re.finditer(r'<a[^>]*href="(/story/\d+[^"]*)"[^>]*>([^<]+)</a>', html):
        url = 'https://www.ftchinese.com' + m.group(1).split('?')[0]
        title = m.group(2).strip()
        if len(title) > 6 and url not in seen_urls:
            seen_urls.add(url)
            articles.append({'title': title, 'url': url})

articles = articles[:12]

with open('/home/hermes_agent/digest/today_news_ft.json', 'w') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f'FT: {len(articles)} articles')
for a in articles[:3]:
    print(f'  {a["title"][:50]}')
