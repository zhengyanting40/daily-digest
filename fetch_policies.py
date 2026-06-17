#!/usr/bin/env python3
"""采集三大来源近期国家级/部委级新政策"""
import requests, json, re, os, sys

os.makedirs('/home/hermes_agent/digest', exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 现有政策的已知关键词（用来去重）
known_policies = ['六张网','六网建设','十五五','6G通信','绿电直连','智能体规范','智能体应用']

all_policies = []

# 1. 财新网 — 宏观/政策频道
print("=== 财新网 ===")
for path in ['/macro/', '/finance/', '/latest/']:
    url = f'https://www.caixin.com{path}'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        # 找含"政策""国务院""发改委""工信部"等的标题
        titles = re.findall(r'<a[^>]*href=[\"\'](https?://[^\"\']*caixin[^\"\']*)[\"\'](?:[^>]*)>(.*?)</a>', r.text, re.DOTALL)
        for href, t in titles:
            title = re.sub(r'<[^>]+>', '', t).strip()
            policy_kw = ['政策','国务院','发改委','工信部','科技部','央行','人民银行','能源局','财政部','商务部',
                        '国家市场监督管理','应急管理部','交通运输部','农业农村部','人社部','教育部','生态环境部',
                        '证监会','金融监管','数据局','人工智能','量子','芯片','数据要素','低空经济','首发经济',
                        '银发经济','碳中和','新能源']
            if len(title) > 10 and any(kw in title for kw in policy_kw):
                print(f"  FOUND: {title[:50]}...")
                all_policies.append({'name': title, 'url': href, 'source': '财新网'})
    except Exception as e:
        print(f"  FAIL {url}: {e}")

# 2. 新浪财经 — 政策频道
print("\n=== 新浪财经 ===")
policy_urls = [
    'https://finance.sina.com.cn/china/',
    'https://finance.sina.com.cn/china/gncj/',
    'https://finance.sina.com.cn/roll/index.d.html?cid=56580',  # 政策
]
for url in policy_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        titles = re.findall(r'<a[^>]*href=[\"\'](https?://finance\.sina[^\"\']*)[\"\'](?:[^>]*)>(.*?)</a>', r.text, re.DOTALL)
        for href, t in titles:
            title = re.sub(r'<[^>]+>', '', t).strip()
            if len(title) > 12 and '2026' in href:
                print(f"  TITLE: {title[:50]}...")
                all_policies.append({'name': title, 'url': href, 'source': '新浪财经'})
    except Exception as e:
        print(f"  FAIL {url}: {e}")

# 3. FT中文网
print("\n=== FT中文网 ===")
ft_urls = [
    'https://www.ftchinese.com/',
    'https://www.ftchinese.com/channel/policy.html',
]
for url in ft_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        titles = re.findall(r'<a[^>]*href=[\"\'](https?://www\.ftchinese\.com/story/[^\"\']+)[\"\'](?:[^>]*)>(.*?)</a>', r.text, re.DOTALL)
        for href, t in titles:
            title = re.sub(r'<[^>]+>', '', t).strip()
            if len(title) > 10:
                print(f"  TITLE: {title[:50]}...")
                all_policies.append({'name': title, 'url': href, 'source': 'FT中文网'})
    except Exception as e:
        print(f"  FAIL {url}: {e}")

# 去重
seen = set()
unique_policies = []
for p in all_policies:
    key = p['name'][:20]
    if key not in seen:
        seen.add(key)
        unique_policies.append(p)

# 保存原始采集结果
output = '/home/hermes_agent/digest/all_policy_articles.json'
with open(output, 'w', encoding='utf-8') as f:
    json.dump(unique_policies, f, ensure_ascii=False, indent=2)
print(f"\n共采集 {len(unique_policies)} 条政策相关文章 → {output}")
