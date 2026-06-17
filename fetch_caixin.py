#!/usr/bin/env python3
"""Fetch caixin.com news for 2026-06-04"""

import requests
import json
import re
import sys
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.caixin.com/",
}

session = requests.Session()
session.headers.update(HEADERS)

results = []

# Strategy 1: Try the homepage first
print("=== Strategy 1: Fetching homepage ===", flush=True)
try:
    resp = session.get("https://www.caixin.com/", timeout=15)
    resp.encoding = 'utf-8'
    print(f"Homepage status: {resp.status_code}, len={len(resp.text)}", flush=True)
    
    # Look for news links - caixin typically has <a> tags with href containing dates
    # Pattern: find all <a> tags with href containing news/article patterns
    links = re.findall(r'<a[^>]*href="(https?://[^"]*caixin[^"]*)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
    
    # Also try relative links
    links2 = re.findall(r'<a[^>]*href="(/[^"]*2026-06-04[^"]*)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
    
    seen = set()
    
    for url, title_text in links:
        title = re.sub(r'<[^>]+>', '', title_text).strip()
        if title and len(title) > 5 and url not in seen:
            seen.add(url)
            results.append({"title": title, "url": url})
    
    for url, title_text in links2:
        title = re.sub(r'<[^>]+>', '', title_text).strip()
        full_url = "https://www.caixin.com" + url if url.startswith('/') else url
        if title and len(title) > 5 and full_url not in seen:
            seen.add(full_url)
            results.append({"title": title, "url": full_url})
    
    print(f"Found {len(results)} items from homepage", flush=True)
except Exception as e:
    print(f"Homepage failed: {e}", flush=True)

# Strategy 2: Try the date-specific URL
if len(results) < 6:
    print("\n=== Strategy 2: Fetching date page ===", flush=True)
    try:
        resp = session.get("https://www.caixin.com/2026-06-04/", timeout=15)
        resp.encoding = 'utf-8'
        print(f"Date page status: {resp.status_code}, len={len(resp.text)}", flush=True)
        
        if resp.status_code == 200:
            links = re.findall(r'<a[^>]*href="(https?://[^"]*)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            links2 = re.findall(r'<a[^>]*href="(/[^"]*)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            
            seen_urls = {r['url'] for r in results}
            
            for url, title_text in links:
                title = re.sub(r'<[^>]+>', '', title_text).strip()
                if title and len(title) > 5 and url not in seen_urls:
                    seen_urls.add(url)
                    results.append({"title": title, "url": url})
            
            for url, title_text in links2:
                title = re.sub(r'<[^>]+>', '', title_text).strip()
                full_url = "https://www.caixin.com" + url if url.startswith('/') else url
                if title and len(title) > 5 and full_url not in seen_urls:
                    seen_urls.add(full_url)
                    results.append({"title": title, "url": full_url})
            
            print(f"Total items: {len(results)}", flush=True)
    except Exception as e:
        print(f"Date page failed: {e}", flush=True)

# Strategy 3: Try the "要闻" or finance section
if len(results) < 6:
    print("\n=== Strategy 3: Fetching finance/news section ===", flush=True)
    for url_path in ["/finance/", "/latest/", "/roll/", "/economics/"]:
        try:
            url = f"https://www.caixin.com{url_path}"
            resp = session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            print(f"Section {url_path} status: {resp.status_code}, len={len(resp.text)}", flush=True)
            
            if resp.status_code == 200:
                links = re.findall(r'<a[^>]*href="(https?://[^"]*)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                links2 = re.findall(r'<a[^>]*href="(/[^"]*)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                
                seen_urls = {r['url'] for r in results}
                
                for url, title_text in links:
                    title = re.sub(r'<[^>]+>', '', title_text).strip()
                    if title and len(title) > 5 and url not in seen_urls:
                        seen_urls.add(url)
                        results.append({"title": title, "url": url})
                
                for url, title_text in links2:
                    title = re.sub(r'<[^>]+>', '', title_text).strip()
                    full_url = "https://www.caixin.com" + url if url.startswith('/') else url
                    if title and len(title) > 5 and full_url not in seen_urls:
                        seen_urls.add(full_url)
                        results.append({"title": title, "url": full_url})
        except Exception as e:
            print(f"Section {url_path} failed: {e}", flush=True)

# Strategy 4: Try the channel API that caixin might use
if len(results) < 6:
    print("\n=== Strategy 4: Try API endpoints ===", flush=True)
    # Try common caixin API patterns
    api_urls = [
        "https://gateway.caixin.com/api/dataplatform/getNewsList?channelId=0&page=1&limit=10",
        "https://www.caixin.com/api/news/list?page=1&size=10",
        "https://www.caixin.com/api/article/list?page=1&size=10",
    ]
    for api_url in api_urls:
        try:
            resp = session.get(api_url, timeout=10, headers={**HEADERS, "Accept": "application/json"})
            print(f"API {api_url} status: {resp.status_code}", flush=True)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    print(f"API returned JSON: {str(data)[:200]}", flush=True)
                except:
                    print(f"API returned non-JSON: {resp.text[:200]}", flush=True)
        except Exception as e:
            print(f"API {api_url} failed: {e}", flush=True)

# Strategy 5: Try with Playwright/browser if available
if len(results) < 6:
    print("\n=== Strategy 5: Try browser rendering ===", flush=True)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers(HEADERS)
            page.goto("https://www.caixin.com/", timeout=30000)
            page.wait_for_load_state("networkidle")
            content = page.content()
            
            links = re.findall(r'<a[^>]*href="(https?://[^"]*caixin[^"]*)"[^>]*>(.*?)</a>', content, re.DOTALL)
            links2 = re.findall(r'<a[^>]*href="(/[^"]*)"[^>]*>(.*?)</a>', content, re.DOTALL)
            
            seen_urls = {r['url'] for r in results}
            
            for url, title_text in links:
                title = re.sub(r'<[^>]+>', '', title_text).strip()
                if title and len(title) > 5 and url not in seen_urls:
                    seen_urls.add(url)
                    results.append({"title": title, "url": url})
            
            for url, title_text in links2:
                title = re.sub(r'<[^>]+>', '', title_text).strip()
                full_url = "https://www.caixin.com" + url if url.startswith('/') else url
                if title and len(title) > 5 and full_url not in seen_urls:
                    seen_urls.add(full_url)
                    results.append({"title": title, "url": full_url})
            
            browser.close()
            print(f"Browser total items: {len(results)}", flush=True)
    except ImportError:
        print("Playwright not available, skipping", flush=True)
    except Exception as e:
        print(f"Browser strategy failed: {e}", flush=True)

# Filter: keep only items that look like real news (with meaningful titles)
def is_good_news(item):
    title = item['title']
    url = item['url']
    # Skip navigation items, short titles, non-news URLs
    bad_keywords = ['登录', '注册', '搜索', '更多', '首页', '上一页', '下一页', 
                    '微博', '微信', 'APP', '关于我们', '广告', '联系', 
                    'English', '意见', '反馈', 'RSS', '订阅', '网站地图',
                    '财新网', '财新传媒', '手机财新', '客户端', '杂志',
                    '财新周刊', '财新数据', '财新智库', '财新国际']
    for kw in bad_keywords:
        if kw in title:
            return False
    if len(title) < 8:
        return False
    # Prefer longer, more descriptive titles
    return True

# Also filter out duplicate titles
seen_titles = set()
filtered = []
for item in results:
    if item['title'] not in seen_titles and is_good_news(item):
        seen_titles.add(item['title'])
        filtered.append(item)

results = filtered

print(f"\n=== Final: {len(results)} news items ===", flush=True)
for i, item in enumerate(results[:20], 1):
    print(f"{i}. {item['title']} -> {item['url']}", flush=True)

# Save to file
output_path = "/home/hermes_agent/digest/caixin_news_0604.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {output_path}", flush=True)
print(f"Total news items collected: {len(results)}", flush=True)
