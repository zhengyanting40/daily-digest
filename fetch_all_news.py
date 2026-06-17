#!/usr/bin/env python3
import urllib.request, urllib.error
import json, re, os, ssl, gzip
from io import BytesIO

def fetch_url(url, timeout=15):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        data = resp.read()
        # Handle gzip
        if resp.headers.get('Content-Encoding') == 'gzip':
            data = gzip.decompress(data)
        enc = resp.headers.get_content_charset() or 'utf-8'
        return data.decode(enc, errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

outdir = '/home/hermes_agent/digest'

# 1. 财新网
print("=== Caixin ===")
html = fetch_url('https://www.caixin.com/')
caixin_news = []
seen_all = set()
# Find links in the page - try various patterns
links = re.findall(r'<a[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</a>', html, re.DOTALL)
for url, title in links:
    title_clean = re.sub(r'<[^>]+>', '', title).strip()
    if len(title_clean) > 10 and ('caixin' in url.lower() or url.startswith('/')):
        if not url.startswith('http'):
            url = 'https://www.caixin.com' + url if url.startswith('/') else url
        if title_clean[:25] not in seen_all:
            seen_all.add(title_clean[:25])
            caixin_news.append({"title": title_clean, "url": url})
caixin_news = caixin_news[:8]
print(f"Caixin: {len(caixin_news)} items")
for n in caixin_news:
    print(f"  {n['title'][:50]}")

# 2. 人民网 - http protocol
print("\n=== People ===")
people_news = []
for pu in ['http://politics.people.com.cn/', 'http://finance.people.com.cn/', 'http://world.people.com.cn/', 'http://opinion.people.com.cn/']:
    try:
        html = fetch_url(pu)
        links = re.findall(r'<a[^>]*href=[\'"](http[^\'"]*people\.com\.cn[^\'"]*)[\'"][^>]*>(.*?)</a>', html, re.DOTALL)
        for url, title in links:
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            if len(title_clean) > 10 and '/n1/' in url:
                if title_clean[:25] not in seen_all:
                    seen_all.add(title_clean[:25])
                    people_news.append({"title": title_clean, "url": url})
    except Exception as e:
        print(f"  Error fetching {pu}: {e}")

people_uniq = []
seen_urls = set()
for n in people_news:
    if n['url'] not in seen_urls:
        seen_urls.add(n['url'])
        people_uniq.append(n)
people_news = people_uniq[:8]
print(f"People: {len(people_news)} items")
for n in people_news:
    print(f"  {n['title'][:50]}")

# 3. 东方财富
print("\n=== EastMoney ===")
html = fetch_url('https://finance.eastmoney.com/')
em_news = []
links = re.findall(r'<a[^>]*href=[\'"](https?://[^\'"]*eastmoney[^\'"]*)[\'"][^>]*>(.*?)</a>', html, re.DOTALL)
for url, title in links:
    title_clean = re.sub(r'<[^>]+>', '', title).strip()
    if len(title_clean) > 12:
        if title_clean[:25] not in seen_all:
            seen_all.add(title_clean[:25])
            em_news.append({"title": title_clean, "url": url})
em_uniq = []
seen_em = set()
for n in em_news:
    key = n['title'][:25]
    if key not in seen_em:
        seen_em.add(key)
        em_uniq.append(n)
em_news = em_uniq[:8]
print(f"EastMoney: {len(em_news)} items")

# 4. FT中文网
print("\n=== FT Chinese ===")
html = fetch_url('https://www.ftchinese.com/')
ft_news = []
links = re.findall(r'<a[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</a>', html, re.DOTALL)
for url, title in links:
    title_clean = re.sub(r'<[^>]+>', '', title).strip()
    if len(title_clean) > 10 and ('ftchinese' in url.lower() or 'story' in url.lower()):
        if not url.startswith('http'):
            url = 'https://www.ftchinese.com' + url if url.startswith('/') else url
        if title_clean[:25] not in seen_all:
            seen_all.add(title_clean[:25])
            ft_news.append({"title": title_clean, "url": url})
ft_uniq = []
seen_ft = set()
for n in ft_news:
    key = n['title'][:25]
    if key not in seen_ft:
        seen_ft.add(key)
        ft_uniq.append(n)
ft_news = ft_uniq[:10]
print(f"FT: {len(ft_news)} items")
for n in ft_news:
    print(f"  {n['title'][:50]}")

# Save to JSON
for name, data in [('caixin', caixin_news), ('people', people_news), ('eastmoney', em_news), ('ftchinese', ft_news)]:
    path = os.path.join(outdir, f'today_news_{name}.json')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Saved {name}: {path} ({len(data)} items)")

print("\n=== ALL DONE ===")
