import json, os, re
from urllib.request import Request, urlopen

digest_dir = "/home/hermes_agent/digest"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
def fetch_url(url, timeout=15):
    req = Request(url, headers=headers)
    resp = urlopen(req, timeout=timeout)
    return resp.read().decode('utf-8', errors='replace')

results = []
seen = set()

# Try multiple FT Chinese URLs
urls = [
    "https://www.ftchinese.com/",
    "https://www.ftchinese.com/channel/global.html",
    "https://www.ftchinese.com/channel/china.html",
    "https://www.ftchinese.com/channel/markets.html",
]
for url in urls:
    try:
        html = fetch_url(url, timeout=15)
        pat = re.compile(r'<a[^>]*href=["\'](https?://[^"\']*ftchinese[^"\']*)["\'][^>]*>(.*?)</a>', re.DOTALL)
        matches = pat.findall(html)
        for u, t in matches:
            title = re.sub(r'<[^>]+>', '', t).strip()
            title = re.sub(r'\s+', ' ', title)
            if not title or len(title) < 8:
                continue
            if title in seen or u in seen:
                continue
            seen.add(title)
            seen.add(u)
            results.append({"title": title, "url": u})
    except Exception as e:
        print(f"{url}: {type(e).__name__}")

# Filter out non-news pages
filtered = []
for r in results:
    t = r["title"]
    if any(kw in t for kw in ["金融时报", "峰会", "论坛", "全球企业动态", "随时随"]):
        continue
    filtered.append(r)

print(f"Total FT items: {len(filtered)}")
for i, n in enumerate(filtered[:12]):
    print(f"  {i+1}. {n['title']}")

with open(f"{digest_dir}/today_news_ft.json", "w") as f:
    json.dump(filtered[:12], f, ensure_ascii=False, indent=2)
