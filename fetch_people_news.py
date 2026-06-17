import requests, json, re, os

os.makedirs('/home/hermes_agent/digest', exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

urls = [
    "http://www.people.com.cn/",
    "http://politics.people.com.cn/",
    "http://finance.people.com.cn/",
    "http://world.people.com.cn/",
]

all_news = []
seen_titles = set()

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        text = r.text
        print(f"OK {url} -> {len(text)} bytes")

        links = re.findall(r'<a[^>]*href=[\"\'](http[^\"\']*people\.com\.cn[^\"\']*)[\"\'][^>]*>(.*?)</a>', text, re.DOTALL)
        for href, title_text in links:
            title = re.sub(r'<[^>]+>', '', title_text).strip()
            if len(title) >= 8 and '2026' in href and title not in seen_titles:
                if any(kw in href for kw in ['/n1/', '/GB/', '/32306/']):
                    seen_titles.add(title)
                    all_news.append({'title': title, 'url': href})
    except Exception as e:
        print(f"FAIL {url} -> {e}")

unique = {}
for item in all_news:
    key = item['title'][:15]
    if key not in unique:
        unique[key] = item

news_list = list(unique.values())
print(f"\n=== Found {len(news_list)} unique news items ===")
for i, n in enumerate(news_list[:12], 1):
    print(f"{i}. {n['title']}")
    print(f"   {n['url']}")

output_path = '/home/hermes_agent/digest/people_news_0604.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(news_list[:12], f, ensure_ascii=False, indent=2)
print(f"\nSaved to {output_path}")
