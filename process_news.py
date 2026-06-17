import urllib.request, json, re, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers=headers)
        r = urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx)
        return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

# Load existing
with open('/home/hermes_agent/digest/today_news.json', 'r') as f:
    news = json.load(f)

# Filter People - keep only real news with /n1/2026 pattern
real_people = [item for item in news['people'] if '/n1/2026' in item['url']]
news['people'] = real_people[:10]
print(f"People (filtered): {len(news['people'])}")

# Remove caixin duplicates
seen = set()
caixin_unique = []
for item in news['caixin']:
    if item['title'] not in seen:
        seen.add(item['title'])
        caixin_unique.append(item)
news['caixin'] = caixin_unique[:8]
print(f"Caixin (dedup, limit 8): {len(news['caixin'])}")

# Try FT with story and channel patterns
html = fetch('https://www.ftchinese.com/')
ft_news = []
if html:
    # Try different patterns
    for m in re.finditer(r'<a[^>]*href=["\'](/story/\d+[^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = 'https://www.ftchinese.com' + m.group(1).strip()
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if len(title) > 8 and 'book' not in url and 'channel' not in url:
            ft_news.append({'title': title, 'url': url})
    # Also try full URL pattern
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*ftchinese\.com/[^"\']+/[^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1).strip()
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if len(title) > 8 and 'story' in url:
            if not any(item['url'] == url for item in ft_news):
                ft_news.append({'title': title, 'url': url})

# Try scraping sections from the page - look for text content that contains headlines
if html:
    # Look for Chinese headlines in various patterns
    for m in re.finditer(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL):
        inner = m.group(1)
        # Find links within heading
        for a in re.finditer(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', inner, re.DOTALL):
            url = a.group(1).strip()
            title_str = re.sub(r'<[^>]+>', '', a.group(2)).strip()
            if len(title_str) > 8:
                if url.startswith('/'):
                    url = 'https://www.ftchinese.com' + url
                if not any(item['url'] == url for item in ft_news):
                    ft_news.append({'title': title_str, 'url': url})

seen = set()
ft_unique = []
for item in ft_news:
    if item['url'] not in seen:
        seen.add(item['url'])
        ft_unique.append(item)
news['ft'] = ft_unique[:10]
print(f"FT: {len(news['ft'])}")

with open('/home/hermes_agent/digest/today_news.json', 'w', encoding='utf-8') as f:
    json.dump(news, f, ensure_ascii=False, indent=2)
print("Saved!")
