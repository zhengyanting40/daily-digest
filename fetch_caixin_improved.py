#!/usr/bin/env python3
"""
Improved fetch for 财新网 - targeting actual news sections.
"""

import json
import os
import re
import sys
import time
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies.")
    sys.exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

OUTPUT_DIR = "/home/hermes_agent/digest"

def fetch_url(url, timeout=30):
    session = requests.Session()
    for attempt in range(2):
        try:
            resp = session.get(url, headers=HEADERS, timeout=timeout)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                return resp.text
            else:
                print(f"  HTTP {resp.status_code} for {url}")
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None


def fetch_caixin_better():
    """Try multiple Caixin URLs to get actual news articles."""
    print("\n=== 财新网 (Caixin) - Improved ===")
    
    urls_to_try = [
        "https://www.caixin.com/",
        "https://www.caixin.com/finance/",
        "https://www.caixin.com/economy/",
        "https://www.caixin.com/new/",
    ]
    
    articles = []
    seen_titles = set()
    seen_urls = set()
    
    for url in urls_to_try:
        print(f"  Trying: {url}")
        html = fetch_url(url)
        if not html:
            print(f"    Failed to load")
            continue
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for article links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '').strip()
            title = a_tag.get('title', '') or a_tag.get_text(strip=True)
            
            if not title or len(title) < 10:
                continue
            
            title = title.strip()
            
            # Skip promotional/sponsored content
            if '特别呈现' in title or 'promote.caixin.com' in href:
                continue
            
            chinese_count = sum(1 for c in title if '\u4e00' <= c <= '\u9fff')
            if chinese_count < 5:
                continue
            
            # Normalize URL
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://www.caixin.com' + href
            elif not href.startswith('http'):
                continue
            
            # Only keep caixin.com URLs (not promote/video subdomains for actual news)
            if 'caixin.com' not in href:
                continue
            
            if title in seen_titles or href in seen_urls:
                continue
            
            # Filter for actual news articles (has date pattern in URL like /2026-06-02/)
            if re.search(r'/20\d{2}-\d{2}-\d{2}/', href):
                articles.append({
                    "title": title,
                    "url": href,
                    "source": "财新网"
                })
                seen_titles.add(title)
                seen_urls.add(href)
        
        # Also try to extract from news list items
        news_items = soup.select('li a, .news-item a, .list-item a, h2 a, h3 a, .title a')
        for a_tag in news_items:
            href = a_tag.get('href', '').strip()
            title = a_tag.get('title', '') or a_tag.get_text(strip=True)
            
            if not title or len(title) < 10 or title in seen_titles:
                continue
            
            if '特别呈现' in title:
                continue
            
            chinese_count = sum(1 for c in title if '\u4e00' <= c <= '\u9fff')
            if chinese_count < 5:
                continue
            
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://www.caixin.com' + href
            elif not href.startswith('http'):
                continue
            
            if 'caixin.com' not in href:
                continue
            
            if href in seen_urls:
                continue
            
            if re.search(r'/20\d{2}-\d{2}-\d{2}/', href):
                articles.append({
                    "title": title,
                    "url": href,
                    "source": "财新网"
                })
                seen_titles.add(title)
                seen_urls.add(href)
    
    # Remove duplicates by URL
    unique = []
    seen = set()
    for a in articles:
        if a['url'] not in seen:
            seen.add(a['url'])
            unique.append(a)
    
    # Sort by URL recency (newer dates first)
    def sort_key(x):
        m = re.search(r'/20(\d{2})-(\d{2})-(\d{2})/', x['url'])
        if m:
            return m.group(0)
        return ''
    
    unique.sort(key=sort_key, reverse=True)
    
    print(f"  Found {len(unique)} real articles")
    
    return {
        "source": "财新网",
        "fetched_at": datetime.now().isoformat(),
        "articles": unique[:10]
    }


def main():
    result = fetch_caixin_better()
    
    filepath = os.path.join(OUTPUT_DIR, "today_news_caixin.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    articles = result.get("articles", [])
    error = result.get("error")
    if error:
        print(f"\n财新网: ERROR - {error}")
    else:
        print(f"\n财新网: {len(articles)} articles saved to {filepath}")
        for a in articles[:8]:
            print(f"  - {a['title'][:70]}")
    
    print(f"\nFile: {filepath}")


if __name__ == "__main__":
    main()
