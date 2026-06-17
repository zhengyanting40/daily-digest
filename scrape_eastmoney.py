#!/usr/bin/env python3
"""Scrape headline news from 东方财富 (https://finance.eastmoney.com/)"""
import requests
import re
import json
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

url = "https://finance.eastmoney.com/"

try:
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    html = resp.text

    print(f"HTML length: {len(html)}")
    
    news_list = []

    # Strategy 1: Look for common eastmoney article patterns in the HTML
    # 东方财富 article links look like: /a/20260604XXXXXX.html
    # Find all article links
    link_pattern = re.findall(
        r'<a[^>]*href=["\'](https?://finance\.eastmoney\.com/a/\d+[^"\'<>]*\.html)["\'][^>]*>(.*?)</a>',
        html, re.DOTALL
    )
    
    seen_urls = set()
    for url_match, title_match in link_pattern:
        title = re.sub(r'<[^>]+>', '', title_match).strip()
        title = re.sub(r'\s+', ' ', title)
        if title and len(title) > 8 and url_match not in seen_urls:
            seen_urls.add(url_match)
            news_list.append({
                "title": title,
                "url": url_match,
                "source": "东方财富"
            })
    
    print(f"Strategy 1 found: {len(news_list)} items")
    
    # Strategy 2: If not enough, also look for relative paths
    if len(news_list) < 6:
        rel_pattern = re.findall(
            r'<a[^>]*href=["\'](/a/\d+[^"\'<>]*\.html)["\'][^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        for url_match, title_match in rel_pattern:
            title = re.sub(r'<[^>]+>', '', title_match).strip()
            title = re.sub(r'\s+', ' ', title)
            full_url = "https://finance.eastmoney.com" + url_match
            if title and len(title) > 8 and full_url not in seen_urls:
                seen_urls.add(full_url)
                news_list.append({
                    "title": title,
                    "url": full_url,
                    "source": "东方财富"
                })
        print(f"After strategy 2: {len(news_list)} items")
    
    # Strategy 3: Look for news-item containers or li tags commonly used
    if len(news_list) < 6:
        # Try to find article links more broadly
        broad_pattern = re.findall(
            r'<a[^>]*href=["\'](https?://finance\.eastmoney\.com/[^"\'<>]*(?:html|shtml))["\'][^>]*>([^<]{10,})</a>',
            html
        )
        for url_match, title_match in broad_pattern:
            title = title_match.strip()
            if title and len(title) > 8 and url_match not in seen_urls:
                seen_urls.add(url_match)
                news_list.append({
                    "title": title,
                    "url": url_match,
                    "source": "东方财富"
                })
        print(f"After strategy 3: {len(news_list)} items")
    
    # Strategy 4: For eastmoney, the news list is often in a specific section
    # Try extracting from the main news section
    if len(news_list) < 6:
        # Search for "新闻" related sections with links
        sections = re.split(r'<div[^>]*class=["\'].*?news.*?["\'][^>]*>', html, re.IGNORECASE)
        for section in sections[1:]:  # skip the first part before any news div
            sec_links = re.findall(
                r'<a[^>]*href=["\'](https?://finance\.eastmoney\.com/[^"\'<>]+\.html)["\'][^>]*>([^<]{10,})</a>',
                section
            )
            for url_match, title_match in sec_links:
                title = title_match.strip()
                if title and len(title) > 8 and url_match not in seen_urls:
                    seen_urls.add(url_match)
                    news_list.append({
                        "title": title,
                        "url": url_match,
                        "source": "东方财富"
                    })
        print(f"After strategy 4: {len(news_list)} items")
    
    # Deduplicate by title (keep first occurrence)
    seen_titles = set()
    unique_news = []
    for item in news_list:
        if item["title"] not in seen_titles:
            seen_titles.add(item["title"])
            unique_news.append(item)
    
    # Take top 8
    result = unique_news[:8]
    
    print(f"\nFinal news count: {len(result)}")
    for i, n in enumerate(result, 1):
        print(f"  {i}. {n['title'][:60]}... -> {n['url'][:70]}...")

    output_path = "/home/hermes_agent/digest/eastmoney_news.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")

except Exception as e:
    print(f"ERROR: {e}")
    # Save whatever we got
    output_path = "/home/hermes_agent/digest/eastmoney_news.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(news_list if 'news_list' in dir() else [], f, ensure_ascii=False, indent=2)
