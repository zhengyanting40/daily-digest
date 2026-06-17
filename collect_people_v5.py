#!/usr/bin/env python3
"""People.cn scraper - working version"""
import json, urllib.request, re, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'}

req = urllib.request.Request('http://www.people.com.cn/', headers=headers)
resp = urllib.request.urlopen(req, timeout=15, context=ctx)
html = resp.read().decode('utf-8', errors='replace')

items, seen = [], set()
for m in re.finditer(r'<a[^>]*href="(http://[^"]*)"[^>]*>([^<]+)</a>', html):
    url = m.group(1)
    title = m.group(2).strip().replace('\n',' ')[:60]
    if 'n1/' in url or 'n2/' in url:
        if len(title) < 8: continue
        if any(x in title for x in ['人民会客厅','对话企业家','更多','高考']): continue
        if url in seen: continue
        seen.add(url)
        items.append((title, url))

# All are good - pick best news (filter out very short titles, sections)
items = [(t,u) for t,u in items if len(t) >= 10 and not t.endswith('频道')]

result = [{'title': t, 'url': u} for t, u in items[:10]]
with open('/home/hermes_agent/digest/people_news.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"People news: {len(result)} items")
for r in result:
    print(f"  ✅ {r['title'][:50]}")
