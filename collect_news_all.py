import urllib.request, json, re
import html as _html_mod

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def fetch_url(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

def clean_title(t):
    cleaned = re.sub(r'<[^>]+>', '', t).strip()
    return _html_mod.unescape(cleaned)

def extract_news_caixin():
    html = fetch_url('https://www.caixin.com/', timeout=25)
    if not html:
        html = fetch_url('https://finance.caixin.com/', timeout=25)
    if not html:
        return []
    news = {}
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*caixin\.com[^"\']*\d+[^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1)
        title = clean_title(m.group(2))
        if len(title) > 8 and 'promote' not in url and 'en.' not in url and 'claw' not in url:
            if url not in news:
                news[url] = {'title': title, 'url': url, 'source': 'caixin'}
    return list(news.values())[:12]

def extract_news_people():
    news = {}
    for base_url in ['http://www.people.com.cn/', 'http://politics.people.com.cn/',
                     'http://finance.people.com.cn/', 'http://world.people.com.cn/']:
        html = fetch_url(base_url, timeout=15)
        if not html:
            continue
        for m in re.finditer(r'<a[^>]*href=["\'](http://[^"\']*people\.com\.cn[^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
            href = m.group(1)
            title = clean_title(m.group(2))
            if len(title) > 8 and '会客厅' not in title and '对话' not in title and '更多' not in title and '>>>' not in title and '&gt' not in title:
                if href not in news:
                    news[href] = {'title': title, 'url': href, 'source': 'people'}
    return list(news.values())[:10]

def extract_news_eastmoney():
    html = fetch_url('https://finance.eastmoney.com/', timeout=25)
    if not html:
        return []
    news = {}
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*eastmoney\.com[^"\']*?/\d+[^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1)
        title = clean_title(m.group(2))
        if len(title) > 8 and '更多' not in title and '&gt' not in title:
            if url not in news:
                news[url] = {'title': title, 'url': url, 'source': 'eastmoney'}
    return list(news.values())[:12]

def extract_news_ft():
    html = fetch_url('https://www.ftchinese.com/', timeout=15)
    if not html:
        return []
    news = {}
    seen = set()
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*ftchinese\.com/story/\d+[^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1).split('?')[0]
        title = clean_title(m.group(2))
        if len(title) > 8 and url not in seen:
            seen.add(url)
            news[url] = {'title': title, 'url': url, 'source': 'ft'}
    for h in re.finditer(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL):
        inner = h.group(1)
        for a in re.finditer(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', inner, re.DOTALL):
            url = a.group(1).strip()
            if url.startswith('/'):
                url = 'https://www.ftchinese.com' + url
            url = url.split('?')[0]
            title = clean_title(a.group(2))
            if len(title) > 8 and '/story/' in url and url not in seen:
                seen.add(url)
                news[url] = {'title': title, 'url': url, 'source': 'ft'}
    return list(news.values())[:12]

all_news = {
    'caixin': extract_news_caixin(),
    'people': extract_news_people(),
    'eastmoney': extract_news_eastmoney(),
    'ft': extract_news_ft(),
}

print(json.dumps(all_news, ensure_ascii=False, indent=2))
