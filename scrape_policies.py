#!/usr/bin/env python3
"""
Scrape latest policy news (2026 May-June) from three Chinese sources:
1. 财新网 (Caixin) - macro/policy channel
2. 新浪财经 (Sina Finance) - policy search/channel
3. 金融时报中文网 (FT Chinese) - policy channel
"""

import requests
import json
import re
import time
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

session = requests.Session()
session.headers.update(HEADERS)

results = []

# ─────────────────────────────────────────────
# 1. 财新网 - 宏观/政策频道
# ─────────────────────────────────────────────
def scrape_caixin():
    print("=" * 60)
    print("[1/3] 正在采集财新网...")
    urls_to_try = [
        "https://www.caixin.com/",
        "https://www.caixin.com/hongguan/caijingguancha/",
        "https://www.caixin.com/2026-05/",
        "https://www.caixin.com/2026-06/",
    ]
    found = []
    for url in urls_to_try:
        try:
            print(f"  访问: {url}")
            r = session.get(url, timeout=15, allow_redirects=True)
            r.encoding = 'utf-8'
            if r.status_code == 200:
                html = r.text
                # Extract article links and titles
                # Caixin uses <h4><a href="...">title</a></h4> or similar patterns
                articles = re.findall(
                    r'<a[^>]*href="(https?://(?:www\.)?caixin\.com/\d{4}[^"]*)"[^>]*>(.*?)</a>',
                    html, re.DOTALL
                )
                for href, title in articles:
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if title and len(title) > 5:
                        found.append({"title": title, "url": href})
                print(f"  找到 {len(articles)} 个链接")
            time.sleep(1.5)
        except Exception as e:
            print(f"  [!] 出错: {e}")
    
    # Deduplicate
    seen = set()
    unique = []
    for item in found:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique.append(item)
    
    # Filter for policy-related content
    policy_kw = ['政策', '国务院', '发改委', '部委', '发布', '方案', '意见', '通知',
                 '决定', '规划', '改革', '监管', '立法', '办法', '措施', '支持',
                 '能源局', '工信部', '科技部', '央行', '财政部', '商务部']
    
    for item in unique:
        title = item['title']
        if any(kw in title for kw in policy_kw):
            # Determine date from URL or content
            date_match = re.search(r'/(\d{4}-\d{2}-\d{2})/', item['url'])
            date_str = date_match.group(1) if date_match else '2026-05'
            
            # Extract keywords
            keywords = [kw for kw in policy_kw if kw in title]
            
            results.append({
                "name": title,
                "date": date_str,
                "source": "财新网",
                "source_url": item['url'],
                "keywords": keywords if keywords else ["政策"]
            })
            print(f"  ✓ {title[:50]}...")
    
    print(f"  财新网: 采集到 {len(results)} 条政策相关记录 (计入总表)")
    return results


# ─────────────────────────────────────────────
# 2. 新浪财经 - 政策频道
# ─────────────────────────────────────────────
def scrape_sina():
    print("\n" + "=" * 60)
    print("[2/3] 正在采集新浪财经...")
    
    # Search URLs
    search_urls = [
        "https://search.sina.com.cn/?q=%E6%96%B0%E6%94%BF%E7%AD%96+2026+%E5%9B%BD%E5%8A%A1%E9%99%A2&range=all&c=news&sort=time",
        "https://search.sina.com.cn/?q=%E5%9B%BD%E5%8A%A1%E9%99%A2%E5%B8%B8%E5%8A%A1%E4%BC%9A%E8%AE%AE+2026&range=all&c=news&sort=time",
        "https://finance.sina.com.cn/china/",
    ]
    
    sina_results = []
    for url in search_urls:
        try:
            print(f"  访问: {url[:60]}...")
            r = session.get(url, timeout=15, allow_redirects=True)
            r.encoding = 'utf-8'
            if r.status_code == 200:
                html = r.text
                
                # Extract article links from search results
                # Sina search results format
                articles = re.findall(
                    r'<a[^>]*href="(https?://finance\.sina\.com\.cn[^"]*)"[^>]*target="_blank"[^>]*>(.*?)</a>',
                    html, re.DOTALL
                )
                
                # Also try sina.com.cn links
                articles2 = re.findall(
                    r'<a[^>]*href="(https?://[a-z]+\.sina\.com\.cn/[^"]*)"[^>]*>(.*?)</a>',
                    html, re.DOTALL
                )
                
                all_articles = list(set(articles + articles2))
                for href, title in all_articles:
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if title and len(title) > 8 and 'sina' in href:
                        sina_results.append({"title": title, "url": href})
                print(f"  找到 {len(all_articles)} 个链接")
            time.sleep(1.5)
        except Exception as e:
            print(f"  [!] 出错: {e}")
    
    # Also try Sina Finance news API
    try:
        print("  尝试新浪财经新闻API...")
        api_url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=30&versionNumber=1.2.4"
        r = session.get(api_url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data.get('result', {}).get('data', []):
                sina_results.append({
                    "title": item.get('title', ''),
                    "url": item.get('url', '')
                })
            print(f"  API: 找到 {len(data.get('result', {}).get('data', []))} 条")
    except Exception as e:
        print(f"  [!] API出错: {e}")
    
    # Filter policy-related
    policy_kw = ['政策', '国务院', '发改委', '部委', '发布', '方案', '意见', '通知',
                 '决定', '规划', '改革', '监管', '立法', '措施', '央行', '工信部',
                 '科技部', '财政部', '商务部', '能源局', '新政策', '国常会']
    
    seen = set()
    count = 0
    for item in sina_results:
        title = item['title']
        if title in seen:
            continue
        seen.add(title)
        
        if any(kw in title for kw in policy_kw):
            # Try to find date in title or URL
            date_match = re.search(r'(\d{4})[年-](\d{1,2})[月-](\d{1,2})', title)
            if date_match:
                date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
            else:
                date_str = '2026-05'
            
            keywords = [kw for kw in policy_kw if kw in title]
            
            results.append({
                "name": title,
                "date": date_str,
                "source": "新浪财经",
                "source_url": item['url'],
                "keywords": keywords if keywords else ["政策"]
            })
            count += 1
            print(f"  ✓ {title[:50]}...")
    
    print(f"  新浪财经: 采集到 {count} 条政策相关记录")
    return results


# ─────────────────────────────────────────────
# 3. 金融时报中文网 (FT Chinese)
# ─────────────────────────────────────────────
def scrape_ftchinese():
    print("\n" + "=" * 60)
    print("[3/3] 正在采集金融时报中文网...")
    
    urls_to_try = [
        "https://www.ftchinese.com/channel/policy.html",
        "https://www.ftchinese.com/",
    ]
    
    ft_results = []
    for url in urls_to_try:
        try:
            print(f"  访问: {url}")
            r = session.get(url, timeout=15, allow_redirects=True)
            r.encoding = 'utf-8'
            if r.status_code == 200:
                html = r.text
                # FT Chinese article links
                articles = re.findall(
                    r'<a[^>]*href="(https?://www\.ftchinese\.com/story/[^"]*)"[^>]*>(.*?)</a>',
                    html, re.DOTALL
                )
                for href, title in articles:
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if title and len(title) > 6:
                        ft_results.append({"title": title, "url": href})
                print(f"  找到 {len(articles)} 个链接")
            time.sleep(1.5)
        except Exception as e:
            print(f"  [!] 出错: {e}")
    
    # Filter policy-related
    policy_kw = ['政策', '国务院', '发改委', '央行', '监管', '发布', '方案', '意见',
                 '规划', '改革', '中国', '经济', '部委', '习近平', '李克强', '总理',
                 '部长', '工信部', '科技部', '财政部', '商务部', '能源']
    
    seen = set()
    count = 0
    for item in ft_results:
        title = item['title']
        if title in seen:
            continue
        seen.add(title)
        
        if any(kw in title for kw in policy_kw):
            date_str = '2026-05'
            keywords = [kw for kw in policy_kw if kw in title]
            
            results.append({
                "name": title,
                "date": date_str,
                "source": "金融时报中文网",
                "source_url": item['url'],
                "keywords": keywords if keywords else ["政策"]
            })
            count += 1
            print(f"  ✓ {title[:50]}...")
    
    print(f"  金融时报中文网: 采集到 {count} 条政策相关记录")
    return results


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
print("=== 2026年5-6月政策新闻采集 ===")
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

all_results = []
all_results.extend(scrape_caixin())
all_results.extend(scrape_sina())
all_results.extend(scrape_ftchinese())

print("\n" + "=" * 60)
print(f"总采集结果: {len(all_results)} 条")

# Deduplicate by title
seen = set()
deduped = []
for item in all_results:
    key = item['name'][:30]  # Compare first 30 chars
    if key not in seen:
        seen.add(key)
        deduped.append(item)

print(f"去重后: {len(deduped)} 条")

# Save
output_path = "/home/hermes_agent/digest/new_policies.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

print(f"\n已保存到: {output_path}")
print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
