#!/usr/bin/env python3
"""Get eastmoney news with partial read support."""
import urllib.request, json, os, re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
HEADERS = {'User-Agent': UA, 'Accept': 'text/html,*/*;q=0.8', 'Accept-Language': 'zh-CN,zh;q=0.9'}

try:
    req = urllib.request.Request('https://finance.eastmoney.com/', headers=HEADERS)
    r = urllib.request.urlopen(req, timeout=20)
    html = ''
    while True:
        chunk = r.read(65536)
        if not chunk:
            break
        html += chunk.decode('utf-8', errors='replace')
except Exception as e:
    print('WARN: ' + str(e)[:80])

items = []
seen = set()
for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']+eastmoney\.com[^"\']*?)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
    url = m.group(1).strip()
    raw = m.group(2).strip()
    title = re.sub(r'<[^>]+>', '', raw).strip()
    title = re.sub(r'\s+', ' ', title)
    if not title or len(title) < 8 or '更多' in title or '&gt' in title:
        continue
    if url in seen:
        continue
    seen.add(url)
    items.append((title, url))

print('eastmoney: ' + str(len(items)))
for t, u in items[:10]:
    print('  ' + t[:60])

# Save
with open('/home/hermes_agent/digest/eastmoney_extra.json', 'w') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
