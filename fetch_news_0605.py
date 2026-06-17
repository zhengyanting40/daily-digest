#!/usr/bin/env python3
"""采集四源新闻（6月5日版）"""
import requests, re, json, os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

os.makedirs('/home/hermes_agent/digest', exist_ok=True)
results = {}

# 1. 财新网
print("=== 财新网 ===")
caixin = []
try:
    r = requests.get("https://www.caixin.com/", headers=headers, timeout=10)
    r.encoding = 'utf-8'
    links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    for href, t in links:
        title = re.sub(r'<[^>]+>', '', t).strip()
        if 'caixin' in href and len(title) > 10:
            kw_finance = ['A股','指数','央行','投资','市场','经济','IPO','上市','财报','监管','新能源','AI','芯片']
            if any(k in title for k in kw_finance):
                caixin.append({'title': title, 'url': href if href.startswith('http') else 'https:'+href})
    print(f"  财新网: {len(caixin)} 条")
except Exception as e:
    print(f"  财新网 FAIL: {e}")
results['caixin'] = caixin[:8]

# 2. 人民网
print("=== 人民网 ===")
people = []
for domain in ['politics.people.com.cn', 'finance.people.com.cn', 'world.people.com.cn', 'opinion.people.com.cn']:
    try:
        r = requests.get(f"http://{domain}/", headers=headers, timeout=8)
        r.encoding = 'utf-8'
        links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
        for href, t in links:
            title = re.sub(r'<[^>]+>', '', t).strip()
            if 'people.com.cn' in href and len(title) > 8 and '2026' in href:
                full_url = href if href.startswith('http') else f'http://{domain}{href}'
                if 'n1' in href:  # 新闻文章模式
                    people.append({'title': title, 'url': full_url})
    except:
        pass
print(f"  人民网: {len(people)} 条")
# 去重
seen = set()
people_uniq = []
for p in people:
    key = p['title'][:15]
    if key not in seen:
        seen.add(key)
        people_uniq.append(p)
results['people'] = people_uniq[:8]

# 3. 东方财富
print("=== 东方财富 ===")
eastmoney = []
try:
    r = requests.get("https://finance.eastmoney.com/", headers=headers, timeout=10)
    r.encoding = 'utf-8'
    links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    for href, t in links:
        title = re.sub(r'<[^>]+>', '', t).strip()
        if 'eastmoney' in href and len(title) > 10:
            full_url = href if href.startswith('http') else 'https:'+href
            eastmoney.append({'title': title, 'url': full_url})
    print(f"  东方财富: {len(eastmoney)} 条")
except Exception as e:
    print(f"  东方财富 FAIL: {e}")
results['eastmoney'] = eastmoney[:8]

# 4. FT中文网
print("=== FT中文网 ===")
ft = []
try:
    r = requests.get("https://www.ftchinese.com/", headers=headers, timeout=10)
    r.encoding = 'utf-8'
    links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    for href, t in links:
        title = re.sub(r'<[^>]+>', '', t).strip()
        if '/story/' in href and len(title) > 10:
            full_url = href if href.startswith('http') else 'https://www.ftchinese.com'+href
            ft.append({'title': title, 'url': full_url})
    print(f"  FT中文网: {len(ft)} 条")
except Exception as e:
    print(f"  FT中文网 FAIL: {e}")
results['ft'] = ft[:10]

# 保存
for key, items in results.items():
    path = f'/home/hermes_agent/digest/news_{key}_0605.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"  → 保存 {len(items)} 条到 {path}")

print("\n=== 完成 ===")
for key, items in results.items():
    print(f"  {key}: {len(items)} 条")
