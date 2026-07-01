#!/usr/bin/env python3
"""Fetch Google News for 山金国际 report - standalone script
Outputs JSON to stdout and saves to shanjin_gnews.json"""
import json, re, html as h, urllib.request, urllib.parse, ssl, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=10):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except:
        return None

def search_google_news(query, max_results=8):
    url = f"https://news.google.com/search?q={urllib.parse.quote(query)}&hl=zh-CN&gl=CN"
    html = fetch(url)
    if not html:
        return []
    results = []
    seen_titles = set()
    for m in re.finditer(r'<a[^>]*href="(\./read/[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL):
        rel_url = m.group(1)
        title = h.unescape(re.sub(r'<[^>]+>', ' ', m.group(2))).strip()
        title = re.sub(r'\s+', ' ', title)
        full_url = "https://news.google.com/" + rel_url.lstrip('./')
        if title not in seen_titles and len(title) > 10:
            seen_titles.add(title)
            results.append({"title": title, "url": full_url})
            if len(results) >= max_results:
                break
    return results

all_news = []
all_news += [{"title": n["title"], "url": n["url"], "source": "gnews_stock"} for n in search_google_news("山金国际", 8)]
all_news += [{"title": n["title"], "url": n["url"], "source": "gnews_industry"} for n in search_google_news("黄金价格 金价 A股", 6)]
all_news += [{"title": n["title"], "url": n["url"], "source": "gnews_industry"} for n in search_google_news("黄金ETF 金矿", 5)]
all_news += [{"title": n["title"], "url": n["url"], "source": "gnews_eastmoney"} for n in search_google_news("山金国际 site:eastmoney.com", 6)]

# Dedup
final, seen = [], set()
for n in all_news:
    key = n['title'][:25]
    if key not in seen:
        seen.add(key)
        final.append(n)

# Save
with open("/home/hermes_agent/digest/shanjin_gnews.json", "w") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print(json.dumps(final, ensure_ascii=False, indent=2))
sys.stderr.write(f"\n✅ {len(final)} articles saved to shanjin_gnews.json\n")
