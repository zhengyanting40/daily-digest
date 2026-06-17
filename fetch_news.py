#!/usr/bin/env python3
"""
四源新闻采集脚本：
1. 财新网 (caixin.com) - 6-8条财经要闻
2. 人民网 (people.com.cn) - 6-8条要闻（http://协议）
3. 东方财富 (finance.eastmoney.com) - 6-8条财经新闻
4. FT中文网 (ftchinese.com) - 8-10条国际新闻
"""

import json
import os
import re
import time
import urllib.parse
from datetime import datetime

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

OUTPUT_DIR = "/home/hermes_agent/digest"


def clean_title(title):
    """Clean and validate title."""
    title = title.strip()
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title)
    # Filter out short/empty titles
    if len(title) < 8:
        return None
    # Filter non-news content
    skip_patterns = [
        r'^\d+$', r'^[•·\-—]', r'^登录', r'^注册', r'^搜索', r'^首页',
        r'客户端', r'APP下载', r'广告', r'免责声明', r'关于我们',
        r'网站地图', r'English', r'手机版', r'设为首页',
    ]
    for p in skip_patterns:
        if re.search(p, title):
            return None
    return title


def make_full_url(base, href):
    """Convert relative URL to absolute."""
    if href.startswith('http://') or href.startswith('https://'):
        return href
    return urllib.parse.urljoin(base, href)


def fetch_caixin():
    """采集财新网财经要闻 https://www.caixin.com/"""
    print(">>> 正在采集财新网...")
    url = "https://www.caixin.com/"
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        html = resp.text
        
        # 财新网 - 多个可能的CSS选择器模式
        links_found = set()
        
        # 方法1: 查找 news_list 区域
        patterns = [
            # pattern: <a href="..." title="..." or >TITLE</a>
            r'<a[^>]*href="(https?://www\.caixin\.com/[^"]*)"[^>]*title="([^"]{10,})"',
            # pattern: h3/h4 > a
            r'<(?:h[234]|li|div)[^>]*>.*?<a[^>]*href="(https?://[^"]+caixin[^"]*)"[^>]*>(.*?)</a>',
            # general pattern with caixin.com domains
            r'<a[^>]*href="(https?://(?:www\.)?caixin\.com/[^"]*)"[^>]*>([^<]{10,})</a>',
        ]
        
        for pattern in patterns:
            for m in re.finditer(pattern, html, re.DOTALL):
                href = m.group(1)
                title = m.group(2).strip()
                # clean HTML tags from title
                title = re.sub(r'<[^>]+>', '', title)
                title = clean_title(title)
                if title and href not in links_found:
                    links_found.add(href)
                    items.append({"title": title, "url": href})
        
        # Also try to find in specific containers
        container_pattern = r'<div[^>]*class="[^"]*(?:news_list|list_news|hot_news|top_news)[^"]*"[^>]*>(.*?)</div>\s*</div>'
        for cm in re.finditer(container_pattern, html, re.DOTALL):
            inner = cm.group(1)
            for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>([^<]{10,})</a>', inner):
                href = m.group(1)
                title = clean_title(m.group(2))
                full_url = make_full_url(url, href)
                if title and full_url not in links_found:
                    links_found.add(full_url)
                    items.append({"title": title, "url": full_url})
        
        # Remove duplicates by URL
        seen = set()
        unique = []
        for item in items:
            if item['url'] not in seen:
                seen.add(item['url'])
                unique.append(item)
        
        print(f"  财新网: 找到 {len(unique)} 条")
        return unique[:8]
    except Exception as e:
        print(f"  财新网采集失败: {e}")
        return []


def fetch_people():
    """采集人民网要闻 http://www.people.com.cn/（主站可访问，politics子域名返回403）"""
    print(">>> 正在采集人民网...")
    url = "http://www.people.com.cn/"
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        html = resp.text
        
        links_found = set()
        
        # 人民网 - 直接匹配所有包含people.com.cn的文章链接
        patterns = [
            # <a href="http://*.people.com.cn/.../n1/...html" target="_blank">TITLE</a>  (新闻文章)
            r'<a[^>]*href="(http://[^"]*people\.com\.cn/[^"]*n\d+/\d+[^"]*)"[^>]*>([^<]{10,})</a>',
            r'<a[^>]*href="(http://[^"]*people\.com\.cn/[^"]*)"[^>]*title="([^"]{10,})"',
            # 所有people.com.cn链接
            r'<a[^>]*href="(http://[^"]*people\.com\.cn/[^"]*)"[^>]*>([^<]{15,})</a>',
        ]
        
        for pattern in patterns:
            for m in re.finditer(pattern, html):
                href = m.group(1)
                title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                title = clean_title(title)
                if title and href not in links_found:
                    links_found.add(href)
                    items.append({"title": title, "url": href})
        
        # Remove duplicates
        seen = set()
        unique = []
        for item in items:
            if item['url'] not in seen:
                seen.add(item['url'])
                unique.append(item)
        
        print(f"  人民网: 找到 {len(unique)} 条")
        return unique[:8]
    except Exception as e:
        print(f"  人民网采集失败: {e}")
        return []


def fetch_eastmoney():
    """采集东方财富财经新闻 https://finance.eastmoney.com/"""
    print(">>> 正在采集东方财富...")
    url = "https://finance.eastmoney.com/"
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        html = resp.text
        
        links_found = set()
        
        # 东方财富 - look for eastmoney.com article links
        patterns = [
            r'<a[^>]*href="(https?://finance\.eastmoney\.com/a/[^"]*)"[^>]*title="([^"]{10,})"',
            r'<a[^>]*href="(https?://finance\.eastmoney\.com/a/[^"]*)"[^>]*>([^<]{10,})</a>',
            r'<a[^>]*href="(https?://[^"]*eastmoney\.com/[^"]*\d{8,}[^"]*)"[^>]*title="([^"]{10,})"',
            r'<a[^>]*href="(https?://[^"]*eastmoney\.com/[^"]*\d{8,}[^"]*)"[^>]*>([^<]{10,})</a>',
        ]
        
        for pattern in patterns:
            for m in re.finditer(pattern, html):
                href = m.group(1)
                title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                title = clean_title(title)
                if title and href not in links_found:
                    links_found.add(href)
                    items.append({"title": title, "url": href})
        
        # Try to find in content areas
        for cls in ['newsList', 'list-item', 'main', 'left', 'right', 'content']:
            area_pat = rf'<[div|ul][^>]*class="[^"]*{cls}[^"]*"[^>]*>(.*?)</(?:div|ul)>'
            for cm in re.finditer(area_pat, html, re.DOTALL):
                inner = cm.group(1)
                for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*title="([^"]{10,})"', inner):
                    href = m.group(1)
                    title = clean_title(m.group(2))
                    full_url = make_full_url(url, href)
                    if title and full_url not in links_found:
                        links_found.add(full_url)
                        items.append({"title": title, "url": full_url})
        
        # Remove duplicates
        seen = set()
        unique = []
        for item in items:
            if item['url'] not in seen:
                seen.add(item['url'])
                unique.append(item)
        
        print(f"  东方财富: 找到 {len(unique)} 条")
        return unique[:8]
    except Exception as e:
        print(f"  东方财富采集失败: {e}")
        return []


def fetch_ftchinese():
    """采集FT中文网国际新闻 https://www.ftchinese.com/"""
    print(">>> 正在采集FT中文网...")
    url = "https://www.ftchinese.com/"
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        html = resp.text
        
        links_found = set()
        
        # FT中文网 patterns
        patterns = [
            r'<a[^>]*href="(https?://(?:www\.)?ftchinese\.com/story/[^"]*)"[^>]*>([^<]{10,})</a>',
            r'<a[^>]*href="(https?://(?:www\.)?ftchinese\.com/[^"]*)"[^>]*title="([^"]{10,})"',
            r'<a[^>]*href="(/story/[^"]*)"[^>]*>([^<]{10,})</a>',
            r'<a[^>]*href="(/[^"]*)"[^>]*title="([^"]{10,})"',
        ]
        
        for pattern in patterns:
            for m in re.finditer(pattern, html):
                href = m.group(1)
                title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                title = clean_title(title)
                full_url = make_full_url(url, href)
                if title and 'ftchinese' in full_url and full_url not in links_found:
                    links_found.add(full_url)
                    items.append({"title": title, "url": full_url})
        
        # Remove duplicates
        seen = set()
        unique = []
        for item in items:
            if item['url'] not in seen:
                seen.add(item['url'])
                unique.append(item)
        
        print(f"  FT中文网: 找到 {len(unique)} 条")
        return unique[:10]
    except Exception as e:
        print(f"  FT中文网采集失败: {e}")
        return []


def save_json(data, filename):
    """Save data to JSON file."""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 已保存: {path} ({len(data)} 条)")
    return path


def main():
    print("=" * 60)
    print(f"四源新闻采集 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 1. 财新网
    caixin_data = fetch_caixin()
    if caixin_data:
        save_json(caixin_data, "news_caixin_0604.json")
    
    time.sleep(1)
    
    # 2. 人民网
    people_data = fetch_people()
    if people_data:
        save_json(people_data, "news_people_0604.json")
    
    time.sleep(1)
    
    # 3. 东方财富
    eastmoney_data = fetch_eastmoney()
    if eastmoney_data:
        save_json(eastmoney_data, "news_eastmoney_0604.json")
    
    time.sleep(1)
    
    # 4. FT中文网
    ft_data = fetch_ftchinese()
    if ft_data:
        save_json(ft_data, "news_ft_0604.json")
    
    print("\n" + "=" * 60)
    print("采集完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
