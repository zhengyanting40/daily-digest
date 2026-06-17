#!/usr/bin/env python3
"""Collect news from caixin.com, people.com.cn, eastmoney.com, ftchinese.com"""
import json, re, urllib.request, ssl, time

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
HEADERS_MOBILE = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}

def fetch(url, headers=None, timeout=20):
    h = headers or HEADERS
    req = urllib.request.Request(url, headers=h)
    try:
        r = urllib.request.urlopen(req, context=ssl_ctx, timeout=timeout)
        html = ''
        while True:
            chunk = r.read(65536)
            if not chunk: break
            html += chunk.decode('utf-8', errors='replace')
        return html
    except Exception as e:
        return f'ERROR: {e}'

# === 1. 财新网 caixin.com ===
print("=== Caixin ===")
html = fetch('https://www.caixin.com/')
caixin_news = []
if html.startswith('ERROR'):
    print(f"  {html}")
else:
    # Find links in the page
    for m in re.finditer(r'<a[^>]*href="(https?://[^"]*caixin\.com[^"]*)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        # Filter
        if (len(title) > 8 and 'promote' not in url.lower() and 'en.' not in url 
            and 'claw' not in url and 'English' not in title):
            title = re.sub(r'\s+', ' ', title).strip()
            caixin_news.append({'url': url, 'title': title})
    # Also try finance.caixin.com
    html2 = fetch('https://finance.caixin.com/')
    if not html2.startswith('ERROR'):
        for m in re.finditer(r'<a[^>]*href="(https?://[^"]*caixin\.com[^"]*)"[^>]*>([^<]+)</a>', html2):
            url = m.group(1)
            title = m.group(2).strip()
            if (len(title) > 8 and 'promote' not in url.lower() and 'en.' not in url 
                and 'claw' not in url and 'English' not in title):
                title = re.sub(r'\s+', ' ', title).strip()
                caixin_news.append({'url': url, 'title': title})
    # Deduplicate
    seen = set()
    deduped = []
    for item in caixin_news:
        if item['url'] not in seen:
            seen.add(item['url'])
            deduped.append(item)
    caixin_news = deduped[:10]
    print(f"  Found {len(caixin_news)} news items")
    for n in caixin_news:
        print(f"    {n['title']}")

# === 2. 人民网 people.com.cn (http:// only) ===
print("\n=== People.cn ===")
html = fetch('http://www.people.com.cn/', timeout=25)
people_news = []
if html.startswith('ERROR'):
    print(f"  {html}")
else:
    for m in re.finditer(r'<a[^>]*href="(http[^"]*)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        title = re.sub(r'\s+', ' ', title).strip()
        # Filter for actual news links
        if ('n1/' in url or 'n2/' in url) and len(title) >= 10:
            if any(kw in title for kw in ['人民会客厅', '对话企业家', '更多', '频道']):
                continue
            # Make sure URL is absolute
            if not url.startswith('http'):
                continue
            people_news.append({'url': url, 'title': title})
    # Deduplicate
    seen = set()
    deduped = []
    for item in people_news:
        if item['url'] not in seen:
            seen.add(item['url'])
            deduped.append(item)
    people_news = deduped[:10]
    print(f"  Found {len(people_news)} news items")
    for n in people_news:
        print(f"    {n['title']}")

# === 3. 东方财富 eastmoney.com ===
print("\n=== Eastmoney ===")
html = fetch('https://finance.eastmoney.com/', timeout=25)
em_news = []
if html.startswith('ERROR'):
    print(f"  {html}")
else:
    for m in re.finditer(r'<a[^>]*href="(https?://[^"]*eastmoney\.com[^"]*)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        title = re.sub(r'\s+', ' ', title).strip()
        if len(title) > 8 and '更多' not in title and '&gt' not in title:
            em_news.append({'url': url, 'title': title})
    seen = set()
    deduped = []
    for item in em_news:
        if item['url'] not in seen:
            seen.add(item['url'])
            deduped.append(item)
    em_news = deduped[:10]
    print(f"  Found {len(em_news)} news items")
    for n in em_news[:10]:
        print(f"    {n['title']}")

# === 4. FT中文网 ftchinese.com ===
print("\n=== FT Chinese ===")
html = fetch('https://www.ftchinese.com/', timeout=25)
ft_news = []
if html.startswith('ERROR'):
    print(f"  {html}")
else:
    # Precise match first
    for m in re.finditer(r'<a[^>]*href="([^"]*ftchinese\.com/story/\d+[^"]*)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        title = re.sub(r'\s+', ' ', title).strip()
        if len(title) > 8:
            ft_news.append({'url': url, 'title': title})
    # If not enough, loose match
    if len(ft_news) < 6:
        for m in re.finditer(r'<a[^>]*href="/story/(\d+)"[^>]*>([^<]+)</a>', html):
            url = f'https://www.ftchinese.com/story/{m.group(1)}'
            title = m.group(2).strip()
            title = re.sub(r'\s+', ' ', title).strip()
            if len(title) > 8:
                ft_news.append({'url': url, 'title': title})
    # Deduplicate
    seen = set()
    deduped = []
    for item in ft_news:
        if item['url'] not in seen:
            seen.add(item['url'])
            deduped.append(item)
    ft_news = deduped[:12]
    print(f"  Found {len(ft_news)} news items")
    for n in ft_news:
        print(f"    {n['title']}")

# Save all news
all_news = {
    'caixin': caixin_news[:10],
    'people': people_news[:10],
    'eastmoney': em_news[:10],
    'ftchinese': ft_news[:12]
}
with open('/home/hermes_agent/digest/today_news.json', 'w') as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print(f"\n=== Summary ===")
print(f"  Caixin: {len(caixin_news)}")
print(f"  People: {len(people_news)}")
print(f"  Eastmoney: {len(em_news)}")
print(f"  FT Chinese: {len(ft_news)}")
