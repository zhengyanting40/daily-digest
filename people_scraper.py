#!/usr/bin/env python3
"""Scrape People's Daily (人民网) headline news from http://www.people.com.cn/"""

import requests
import re
import json
import sys
from html.parser import HTMLParser

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def fetch_page():
    """Fetch the people.com.cn homepage."""
    print("[*] Fetching http://www.people.com.cn/ ...")
    try:
        resp = requests.get("http://www.people.com.cn/", headers=headers, timeout=15)
        resp.encoding = "utf-8"
        print(f"[+] Status: {resp.status_code}, size: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        print(f"[-] Fetch failed: {e}")
        return None


def extract_links_from_html(html):
    """Extract headline news links from the HTML using regex + basic parsing."""
    news_items = []

    # Strategy 1: Look for links in common headline/top-news areas.
    # People.com.cn typically has links like:
    #   <a href="http://politics.people.com.cn/n1/2026/0604/..." target="_blank">标题</a>
    #   <a href="http://finance.people.com.cn/..." target="_blank">标题</a>
    # We look for <a> tags with href containing people.com.cn

    # Pattern: find <a ... href="...people.com.cn/..." ...> text </a>
    # We'll use a more comprehensive approach

    # First, let's find all href links
    link_pattern = re.compile(r'<a[^>]*href=["\'](http[^"\']*people\.com\.cn[^"\']*)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
    matches = link_pattern.findall(html)

    seen_urls = set()
    for url, title_text in matches:
        # Clean title - remove HTML tags inside
        title = re.sub(r'<[^>]+>', '', title_text).strip()
        title = re.sub(r'\s+', ' ', title)
        # Filter out empty titles, very short titles, and navigation/utility links
        if not title or len(title) < 6:
            continue
        # Filter out common non-news links
        skip_keywords = ['设为首页', '加入收藏', '邮箱', '通行证', '人民微博', '手机人民网',
                         '网站地图', '关于我们', 'Engl', '日本語', '한국어', '简体', '繁体',
                         '滚动', '人民网', '人民日报', '人民视讯', '人民电视', '主编邮箱',
                         '广告服务', '联系方式', '纠错', '招聘', '网站声明', '更多>>', '更多',
                         'Copyright', '人民日报社', '意见反馈', '登录', '注册', '客户端',
                         '新闻热线', '热线电话', 'APP', '微信', '微博', '合作伙伴',
                         '独家出品', '强国论坛', '领导留言板', '人民网评', '人民观察',
                         '中国共产党新闻网', '返回首页', '人民日报概况', '记者核实']
        if any(kw in title for kw in skip_keywords):
            continue
        # Filter out very generic short links
        if title in seen_urls:
            continue
        # Ensure URL is a proper people.com.cn news URL
        if not re.search(r'people\.com\.cn/n\d+/', url):
            continue

        seen_urls.add(title)
        news_items.append({
            "title": title,
            "url": url,
            "source": "人民网"
        })

    return news_items


def extract_headline_areas(html):
    """More targeted extraction: find headline/bulletin areas."""
    news_items = []

    # Strategy 2: Find specific div sections with headline/要闻 keywords
    # Common patterns in people.com.cn HTML

    # Headline area - often has id like "headline" or class like "top_news"
    headline_patterns = [
        r'<div[^>]*class=["\']headline["\'][^>]*>(.*?)</div>',
        r'<div[^>]*class=["\']top_news["\'][^>]*>(.*?)</div>',
        r'<div[^>]*id=["\']headline["\'][^>]*>(.*?)</div>',
        r'<div[^>]*class=["\']focus["\'][^>]*>(.*?)</div>',
        r'<ul[^>]*class=["\']headline_list["\'][^>]*>(.*?)</ul>',
        r'<div[^>]*class=["\']left_[^"\']*["\'][^>]*>(.*?)</div>',
    ]

    all_links = []

    for pat in headline_patterns:
        sections = re.findall(pat, html, re.DOTALL | re.IGNORECASE)
        for section in sections:
            # Extract links from this section
            a_tags = re.findall(r'<a[^>]*href=["\'](http[^"\']*people\.com\.cn[^"\']*)["\'][^>]*>(.*?)</a>', section, re.DOTALL | re.IGNORECASE)
            for url, title_text in a_tags:
                title = re.sub(r'<[^>]+>', '', title_text).strip()
                title = re.sub(r'\s+', ' ', title)
                if title and len(title) >= 6:
                    all_links.append((url, title))

    # Also look in the main content area
    body_areas = re.findall(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    if body_areas:
        # Find area around "要闻" heading
        yaowen_pat = re.compile(r'要闻[^<]*(?:<[^>]*>)*\s*(.*?)(?:<div[^>]*class=["\'](?:footer|copyright|right_)[^"\']*["\'])', re.DOTALL)
        for body in body_areas:
            yw_matches = yaowen_pat.findall(body)
            for yw_section in yw_matches:
                a_tags = re.findall(r'<a[^>]*href=["\'](http[^"\']*people\.com\.cn[^"\']*)["\'][^>]*>(.*?)</a>', yw_section, re.DOTALL | re.IGNORECASE)
                for url, title_text in a_tags:
                    title = re.sub(r'<[^>]+>', '', title_text).strip()
                    title = re.sub(r'\s+', ' ', title)
                    if title and len(title) >= 6:
                        all_links.append((url, title))

    seen_titles = set()
    for url, title in all_links:
        if title not in seen_titles:
            seen_titles.add(title)
            news_items.append({
                "title": title,
                "url": url,
                "source": "人民网"
            })

    return news_items


def main():
    html = fetch_page()
    if not html:
        print("[-] Failed to fetch people.com.cn")
        sys.exit(1)

    # Try both extraction strategies
    items1 = extract_links_from_html(html)
    items2 = extract_headline_areas(html)

    # Merge, deduplicate by URL
    seen_urls = set()
    merged = []
    for item in items1 + items2:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            merged.append(item)

    print(f"[+] Found {len(merged)} news items total")

    # Take top 8
    top_news = merged[:8]

    print(f"\n{'='*60}")
    print(f"Top {len(top_news)} Headline News:")
    print(f"{'='*60}")
    for i, item in enumerate(top_news, 1):
        print(f"{i}. {item['title']}")
        print(f"   URL: {item['url']}")
        print()

    # Save to JSON
    output_path = "/home/hermes_agent/digest/people_news.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(top_news, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved to {output_path}")

    # Also save full list for debugging
    full_path = "/home/hermes_agent/digest/people_news_all.json"
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[+] Full list saved to {full_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
