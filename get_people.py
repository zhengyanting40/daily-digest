#!/usr/bin/env python3
"""Better people news scraper - try more URLs."""
import urllib.request, json, os, re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
HEADERS = {'User-Agent': UA, 'Accept-Language': 'zh-CN,zh;q=0.9'}

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', errors='replace')

def extract(html, domain):
    items = []
    seen = set()
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*' + domain + r'[^"\']*?/n1/[^"\']*?\.html)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1).strip()
        raw = m.group(2).strip()
        title = re.sub(r'<[^>]+>', '', raw).strip()
        title = re.sub(r'\s+', ' ', title)
        if not title or len(title) < 8 or '更多' in title or '&gt' in title:
            continue
        key = title[:30]
        if key not in seen:
            seen.add(key)
            items.append((title, url))
    return items

people = []
for sub in ['finance', 'world', 'opinion', 'env', 'health']:
    try:
        html = fetch('http://' + sub + '.people.com.cn/')
        for t, u in extract(html, r'people\.com\.cn'):
            if len(people) < 12:
                people.append((t, u))
    except Exception as e:
        print(sub + ': ' + str(e)[:40])

with open('/home/hermes_agent/digest/people_extra.json', 'w') as f:
    json.dump(people, f, ensure_ascii=False, indent=2)
print('people: ' + str(len(people)))
for t, u in people[:8]:
    print('  ' + t[:55])
