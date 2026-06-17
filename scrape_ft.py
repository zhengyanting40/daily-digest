#!/usr/bin/env python3
"""Scrape news from FT中文网 (https://www.ftchinese.com/)"""
import requests
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

url = "https://www.ftchinese.com/"

try:
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    html = resp.text

    print(f"HTML length: {len(html)}")
    
    news_list = []
    seen_urls = set()
    
    # FT中文网 article links look like: /story/00109XXXX
    # Strategy 1: Find all article links with /story/ pattern
    story_pattern = re.findall(
        r'<a[^>]*href=["\'](https?://www\.ftchinese\.com/story/\d+[^"\'<>]*)["\'][^>]*>(.*?)</a>',
        html, re.DOTALL
    )
    
    for url_match, title_match in story_pattern:
        title = re.sub(r'<[^>]+>', '', title_match).strip()
        title = re.sub(r'\s+', ' ', title)
        if title and len(title) > 6 and url_match not in seen_urls:
            seen_urls.add(url_match)
            news_list.append({
                "title": title,
                "url": url_match,
                "source": "FT中文网"
            })
    
    print(f"Strategy 1 (full URL): {len(news_list)} items")
    
    # Strategy 2: Look for relative /story/ paths
    if len(news_list) < 8:
        rel_pattern = re.findall(
            r'<a[^>]*href=["\'](/story/\d+[^"\'<>]*)["\'][^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        for url_match, title_match in rel_pattern:
            title = re.sub(r'<[^>]+>', '', title_match).strip()
            title = re.sub(r'\s+', ' ', title)
            full_url = "https://www.ftchinese.com" + url_match
            if title and len(title) > 6 and full_url not in seen_urls:
                seen_urls.add(full_url)
                news_list.append({
                    "title": title,
                    "url": full_url,
                    "source": "FT中文网"
                })
        print(f"After strategy 2: {len(news_list)} items")
    
    # Strategy 3: Look in specific sections (headlines, top stories)
    if len(news_list) < 8:
        # Try to find h3 or h2 tags that contain links
        headline_pattern = re.findall(
            r'<h[23][^>]*>.*?<a[^>]*href=["\'](https?://www\.ftchinese\.com/[^"\'<>]+)["\'][^>]*>(.*?)</a>.*?</h[23]>',
            html, re.DOTALL
        )
        for url_match, title_match in headline_pattern:
            title = re.sub(r'<[^>]+>', '', title_match).strip()
            title = re.sub(r'\s+', ' ', title)
            if title and len(title) > 6 and url_match not in seen_urls and 'story' in url_match:
                seen_urls.add(url_match)
                news_list.append({
                    "title": title,
                    "url": url_match,
                    "source": "FT中文网"
                })
        print(f"After strategy 3: {len(news_list)} items")
    
    # Strategy 4: Broader FT links
    if len(news_list) < 8:
        broad_pattern = re.findall(
            r'<a[^>]*href=["\'](https?://www\.ftchinese\.com/[^"\'<>]+)["\'][^>]*>([^<]{10,})</a>',
            html
        )
        for url_match, title_match in broad_pattern:
            title = title_match.strip()
            if title and len(title) > 6 and url_match not in seen_urls and 'story' in url_match:
                seen_urls.add(url_match)
                news_list.append({
                    "title": title,
                    "url": url_match,
                    "source": "FT中文网"
                })
        print(f"After strategy 4: {len(news_list)} items")
    
    # Deduplicate by title
    seen_titles = set()
    unique_news = []
    for item in news_list:
        if item["title"] not in seen_titles:
            seen_titles.add(item["title"])
            unique_news.append(item)
    
    # Take top 10
    result = unique_news[:10]
    
    print(f"\nFinal news count: {len(result)}")
    for i, n in enumerate(result, 1):
        print(f"  {i}. {n['title'][:60]}... -> {n['url'][:70]}...")

    output_path = "/home/hermes_agent/digest/ft_news.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    # Save whatever we got
    output_path = "/home/hermes_agent/digest/ft_news.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(news_list if 'news_list' in dir() else [], f, ensure_ascii=False, indent=2)
