import requests, re, json, os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 1. 财新网宏观频道
print("=== 财新网宏观频道 ===")
r = requests.get("https://www.caixin.com/macro/", headers=headers, timeout=15)
r.encoding = 'utf-8'
links = re.findall(r'<a[^>]*href=[\"\'](https?://[^\"\']+caixin[^\"\']*)[\"\'][^>]*>(.*?)</a>', r.text, re.DOTALL)

found = []
for href, t in links:
    title = re.sub(r'<[^>]+>', '', t).strip()
    kw = ['国务院','发改委','工信部','科技部','央行','人民银行','能源局','财政部','商务部',
          '金融监管总局','证监会','数据局','新规','印发','通知','意见','办法','条例','规定',
          '人工智能','量子','低空','商业航天','新能源','数字经济','数据要素','芯片','半导体',
          '算力','东数西算']
    if title and len(title) > 10 and any(k in title for k in kw):
        found.append({'title': title, 'url': href})
        print(f"  [{len(found)}] {title[:60]}")

# 2. 新浪财经搜索
print("\n=== 新浪财经搜索 ===")
for q in ['%E5%9B%BD%E5%8A%A1%E9%99%A2+%E6%96%B0%E8%A7%84',  # 国务院 新规
          '%E5%8F%91%E6%94%B9%E5%A7%94+%E6%94%BF%E7%AD%96',    # 发改委 政策
          '%E5%B7%A5%E4%BF%A1%E9%83%A8+%E5%8D%B0%E5%8F%91',    # 工信部 印发
          '%E5%A4%AE%E8%A1%8C+%E6%94%BF%E7%AD%96']:             # 央行 政策
    try:
        url = f'https://search.sina.com.cn/?q={q}&range=all&c=news&sort=time'
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = 'utf-8'
        titles = re.findall(r'<h2[^>]*>(.*?)</h2>', r.text, re.DOTALL)
        count = 0
        for t in titles:
            title = re.sub(r'<[^>]+>', '', t).strip()
            if title and len(title) > 12 and count < 3:
                print(f"  [SINA] {title[:60]}")
                found.append({'title': title, 'url': 'https://search.sina.com.cn', 'source': '新浪搜索'})
                count += 1
    except Exception as e:
        print(f"  FAIL: {e}")

# 去重输出
seen = set()
unique = []
for item in found:
    key = item['title'][:20]
    if key not in seen:
        seen.add(key)
        unique.append(item)

os.makedirs('/home/hermes_agent/digest', exist_ok=True)
with open('/home/hermes_agent/digest/new_policies_found.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f"\n共发现 {len(unique)} 条政策相关文章")
