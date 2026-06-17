#!/usr/bin/env python3
"""Improved news scraper - get more real news from all sources."""
import urllib.request, json, os, re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
HEADERS = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', errors='replace')

def extract_articles(html, domain_filter, title_min_len=6):
    """Extract article links and titles from HTML."""
    articles = []
    seen_titles = set()
    for m in re.finditer(r'<a[^>]*href=["\'](https?://[^"\']*' + domain_filter + r'[^"\']*?)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        url = m.group(1).strip()
        raw_title = m.group(2).strip()
        title = re.sub(r'<[^>]+>', '', raw_title).strip()
        # Clean up whitespace
        title = re.sub(r'\s+', ' ', title)
        if title and len(title) >= title_min_len and title not in seen_titles:
            seen_titles.add(title)
            articles.append((title, url))
    return articles

def is_nav_link(url, title):
    """Check if this is a navigation/section link not a real article."""
    nav_patterns = ['promote', 'en.', 'claw', 'people.com.cn/GB/8215/', '/GB/453221/']
    for p in nav_patterns:
        if p in url.lower():
            return True
    nav_titles = ['更多>', 'English', 'Promotion', '数据通', '人民会客厅', '对话企业家', '人民网', '人民视频']
    for t in nav_titles:
        if t in title:
            return True
    # Check if title looks like nav (starts with section name, too short, etc.)
    if len(title) < 8:
        return True
    return False

out = '/home/hermes_agent/digest/news_data.json'
os.makedirs(os.path.dirname(out), exist_ok=True)
all_news = {}
all_news['ftchinese'] = []  # known to be very limited

# 1. 财新网 - try multiple pages/sections
caixin_items = []
try:
    html = fetch('https://www.caixin.com/')
    articles = extract_articles(html, r'caixin\.com')
    for t, u in articles:
        if not is_nav_link(u, t) and 'caixin.com/2026' in u:
            caixin_items.append((t, u))
except Exception as e:
    print('caixin error: ' + str(e)[:60])

# If not enough, try finance subdomain
if len(caixin_items) < 6:
    try:
        html = fetch('https://finance.caixin.com/')
        articles = extract_articles(html, r'caixin\.com')
        for t, u in articles:
            if not is_nav_link(u, t) and len(caixin_items) < 12:
                already = any(t in x[0] for x in caixin_items)
                if not already:
                    caixin_items.append((t, u))
    except Exception as e:
        print('finance.caixin error: ' + str(e)[:60])

all_news['caixin'] = caixin_items[:8]
print('caixin: ' + str(len(all_news['caixin'])))

# 2. 人民网 - multiple subdomains
people_items = []
seen_people = set()
for sub in ['politics', 'finance', 'world', 'opinion']:
    try:
        html = fetch('http://' + sub + '.people.com.cn/')
        articles = extract_articles(html, r'people\.com\.cn')
        for t, u in articles:
            if is_nav_link(u, t):
                continue
            key = t[:30]
            if key not in seen_people and len(people_items) < 12:
                seen_people.add(key)
                people_items.append((t, u))
    except Exception as e:
        print('people ' + sub + ' error: ' + str(e)[:40])

all_news['people'] = people_items[:8]
print('people: ' + str(len(all_news['people'])))

# 3. 东方财富
east_items = []
try:
    html = fetch('https://finance.eastmoney.com/')
    articles = extract_articles(html, r'eastmoney\.com')
    for t, u in articles:
        if is_nav_link(u, t):
            continue
        if '更多' in t or '&gt' in t:
            continue
        if len(t) < 8:
            continue
        east_items.append((t, u))
except Exception as e:
    print('eastmoney error: ' + str(e)[:60])

all_news['eastmoney'] = east_items[:8]
print('eastmoney: ' + str(len(all_news['eastmoney'])))

# 4. FT中文网
ft_items = []
try:
    html = fetch('https://www.ftchinese.com/')
    articles = extract_articles(html, r'ftchinese\.com/story')
    for t, u in articles:
        if len(t) > 4:
            ft_items.append((t, u))
except Exception as e:
    print('ft error: ' + str(e)[:60])

all_news['ftchinese'] = ft_items[:4]
print('ftchinese: ' + str(len(all_news['ftchinese'])))

with open(out, 'w') as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)
print('saved to ' + out)
