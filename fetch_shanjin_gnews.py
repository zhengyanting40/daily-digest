#!/usr/bin/env python3
"""Fetch Google News for 山金国际"""
import urllib.request, urllib.parse, ssl, re, json, html as h

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(query, max_r=8):
    url = "https://news.google.com/search?q=" + urllib.parse.quote(query) + "&hl=zh-CN&gl=CN"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        html_data = resp.read().decode("utf-8", errors="replace")
    results, seen = [], set()
    for m in re.finditer(r'<a[^>]*href="(\./read/[^"]+)"[^>]*>(.*?)</a>', html_data, re.DOTALL):
        title = h.unescape(re.sub(r'<[^>]+>', " ", m.group(2))).strip()
        url = "https://news.google.com/" + m.group(1).lstrip("./")
        key = title[:25]
        if key not in seen and len(title) > 10:
            seen.add(key)
            results.append({"title": title, "url": url})
            if len(results) >= max_r: break
    return results

all_news = []
for q, n in [("山金国际", 8), ("黄金价格 金价 A股", 6), ("黄金ETF 金矿", 5)]:
    try:
        all_news.extend(fetch(q, n))
    except:
        pass

seen = set()
deduped = []
for item in all_news:
    key = item["title"][:25]
    if key not in seen:
        seen.add(key)
        deduped.append(item)

with open("/home/hermes_agent/digest/shanjin_gnews.json", "w") as f:
    json.dump(deduped, f, ensure_ascii=False)
print(f"OK: {len(deduped)} news items saved")
