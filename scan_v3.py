import requests, re, json, os
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

results = []

# 1. Check caixin.com macro page
try:
    r = requests.get("https://www.caixin.com/macro/", headers=headers, timeout=10)
    r.encoding = 'utf-8'
    print(f"Caixin macro page: {len(r.text)} bytes")
    links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    for href, t in links:
        title = re.sub(r'<[^>]+>', '', t).strip()
        if 'caixin' in href and len(title) > 10:
            kw = ['国务院','发改委','工信部','科技部','央行','能源局','财政部',
                  '新规','印发','意见','办法','条例','规定','数据局','金融监管']
            if any(k in title for k in kw):
                results.append({'title': title, 'url': href, 'source': '财新网'})
    print(f"Found {len(results)} policy articles on caixin macro")
except Exception as e:
    print(f"Caixin macro FAIL: {e}")

# 2. Check caixin finance channel
try:
    r = requests.get("https://www.caixin.com/finance/", headers=headers, timeout=10)
    r.encoding = 'utf-8'
    links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    for href, t in links:
        title = re.sub(r'<[^>]+>', '', t).strip()
        if 'caixin' in href and len(title) > 10:
            kw = ['国务院','发改委','央行','财政部','新规','政策','金融监管']
            if any(k in title for k in kw):
                results.append({'title': title, 'url': href, 'source': '财新网'})
    print(f"Found {len(results)} total so far")
except Exception as e:
    print(f"Caixin finance FAIL: {e}")

# 3. FT中文网
try:
    r = requests.get("https://www.ftchinese.com/", headers=headers, timeout=10)
    r.encoding = 'utf-8'
    links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    for href, t in links:
        title = re.sub(r'<[^>]+>', '', t).strip()
        if 'story' in href and len(title) > 10:
            kw = ['中国','政策','监管','央行','AI','芯片','关税','贸易','新能源']
            if any(k in title for k in kw):
                results.append({'title': title, 'url': href, 'source': 'FT中文网'})
    print(f"FT page OK")
except Exception as e:
    print(f"FT FAIL: {e}")

# Print results
seen = set()
unique = []
for item in results:
    key = item['title'][:20]
    if key not in seen:
        seen.add(key)
        unique.append(item)

print(f"\n=== 最终 {len(unique)} 条政策相关 ===")
for i, item in enumerate(unique, 1):
    print(f"{i}. [{item['source']}] {item['title'][:60]}")

# Save
os.makedirs('/home/hermes_agent/digest', exist_ok=True)
with open('/home/hermes_agent/digest/new_policies_found.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f"\nSaved to new_policies_found.json")
