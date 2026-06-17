import urllib.request, json, re, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def fetch(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=headers)
        r = urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx)
        return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

news = {}

# People's Daily - try www.people.com.cn
html = fetch('http://www.people.com.cn/')
people_news = []
if html:
    # Find all links
    for m in re.finditer(r'<a[^>]*href=["\'](http[^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1).strip()
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if len(title) > 8 and 'people.com.cn' in url:
            if any(x in title for x in ['人民会客厅','对话企业家','与思想结伴','更多','&gt']):
                continue
            if '/n1/' in url or '/GB/' in url:
                people_news.append({'title': title, 'url': url})

# Also try politics.people.com.cn
html2 = fetch('http://politics.people.com.cn/')
if html2:
    for m in re.finditer(r'<a[^>]*href=["\'](http[^"\']+)["\'][^>]*>(.*?)</a>', html2, re.DOTALL):
        url = m.group(1).strip()
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if len(title) > 8 and 'people.com.cn' in url and '/n1/' in url:
            if any(x in title for x in ['人民会客厅','对话企业家']):
                continue
            people_news.append({'title': title, 'url': url})

# Dedup
seen = set()
people_unique = []
for item in people_news:
    if item['url'] not in seen:
        seen.add(item['url'])
        people_unique.append(item)
news['people'] = people_unique[:10]
print(f"People: {len(news['people'])}")

# East Money
html = fetch('https://finance.eastmoney.com/')
eastmoney_news = []
if html:
    # Find links with typical eastmoney patterns
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*eastmoney[^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1).strip()
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if len(title) > 8 and '更多' not in title and '&gt' not in title:
            if re.search(r'/\d+[^/]*\.html', url) or 'a/' in url:
                eastmoney_news.append({'title': title, 'url': url})
seen = set()
em_unique = []
for item in eastmoney_news:
    if item['url'] not in seen:
        seen.add(item['url'])
        em_unique.append(item)
news['eastmoney'] = em_unique[:10]
print(f"Eastmoney: {len(news['eastmoney'])}")

# FT Chinese
html = fetch('https://www.ftchinese.com/')
ft_news = []
if html:
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*ftchinese\.com/story/\d+[^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1).strip()
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if len(title) > 8:
            ft_news.append({'title': title, 'url': url})
seen = set()
ft_unique = []
for item in ft_news:
    if item['url'] not in seen:
        seen.add(item['url'])
        ft_unique.append(item)
news['ft'] = ft_unique[:10]
print(f"FT: {len(news['ft'])}")

# Load existing caixin news
try:
    with open('/home/hermes_agent/digest/today_news.json', 'r') as f:
        existing = json.load(f)
    if 'caixin' in existing and existing['caixin']:
        news['caixin'] = existing['caixin']
        print(f"Caixin (loaded): {len(news['caixin'])}")
except:
    pass

with open('/home/hermes_agent/digest/today_news.json', 'w', encoding='utf-8') as f:
    json.dump(news, f, ensure_ascii=False, indent=2)
print("All news saved!")
