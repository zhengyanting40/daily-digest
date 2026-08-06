#!/usr/bin/env python3
"""Collect news: caixin + people + eastmoney + ftchinese"""
import json, re, ssl, urllib.request, html as ihtml

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def fetch(url, timeout=20, headers=None, chunked=False):
    h = {"User-Agent": UA}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        if chunked:
            buf = b''
            while True:
                c = r.read(65536)
                if not c: break
                buf += c
            return buf
        return r.read()

def clean(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = ihtml.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

results = {'caixin': [], 'people': [], 'eastmoney': [], 'ftchinese': []}

# 1. Caixin
try:
    html = fetch('https://www.caixin.com/', timeout=20).decode('utf-8', errors='replace')
    seen = set()
    for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL):
        url, t = m.group(1), clean(m.group(2))
        if not t or len(t) < 10: continue
        if 'promote' in url or 'en.' in url or 'claw' in url: continue
        if 'caixin.com' not in url: continue
        if not url.startswith('http'): continue
        if url in seen: continue
        seen.add(url)
        results['caixin'].append({'title': t, 'url': url})
        if len(results['caixin']) >= 8: break
except Exception as e:
    print(f"caixin fail: {e}")
print(f"caixin: {len(results['caixin'])}")

# 2. People (http only)
try:
    html = fetch('http://www.people.com.cn/', timeout=20).decode('utf-8', errors='replace')
    seen_url, seen_title = set(), set()
    for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL):
        url, t = m.group(1), clean(m.group(2))
        if not t or len(t) < 10: continue
        if 'n1/' not in url and 'n2/' not in url: continue
        if '\u4eba\u6c11\u4f1a\u5ba2\u5385' in t or '\u5bf9\u8bdd\u4f01\u4e1a\u5bb6' in t or '\u66f4\u591a' in t: continue
        if not url.startswith('http'): url = 'http://www.people.com.cn' + url
        if url in seen_url or t in seen_title: continue
        seen_url.add(url); seen_title.add(t)
        results['people'].append({'title': t, 'url': url})
        if len(results['people']) >= 8: break
except Exception as e:
    print(f"people fail: {e}")
print(f"people: {len(results['people'])}")

# 3. Eastmoney (chunked read)
try:
    raw = fetch('https://finance.eastmoney.com/', timeout=25, chunked=True)
    html = raw.decode('utf-8', errors='replace')
    seen = set()
    for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL):
        url, t = m.group(1), clean(m.group(2))
        if not t or len(t) < 10: continue
        if '\u66f4\u591a' in t or '&gt' in t: continue
        if 'eastmoney.com' not in url: continue
        if url in seen: continue
        seen.add(url)
        results['eastmoney'].append({'title': t, 'url': url})
        if len(results['eastmoney']) >= 8: break
except Exception as e:
    print(f"eastmoney fail: {e}")
print(f"eastmoney: {len(results['eastmoney'])}")

# 4. FT Chinese (anchor title+url regex + topnews fallback)
def ft_collect(url):
    try:
        html = fetch(url, timeout=20).decode('utf-8', errors='replace')
    except Exception:
        return []
    seen, out = set(), []
    # anchor-based extraction: title + url pairs (strip trailing quote)
    for m in re.finditer(r'<a[^>]*href="(/story/\d+)"[^>]*>(.*?)</a>', html, re.DOTALL):
        u = m.group(1).strip('"')
        t = clean(m.group(2))
        full = 'https://www.ftchinese.com' + u
        if full in seen: continue
        seen.add(full)
        out.append((t, full))
    # fallback: full URL regex
    if len(out) < 8:
        for m in re.finditer(r'https://www\.ftchinese\.com/story/\d+', html):
            u = m.group(0)
            if u in seen: continue
            seen.add(u)
            out.append(('', u))
    return out

try:
    pairs = ft_collect('https://www.ftchinese.com/')
    if len(pairs) < 8:
        pairs2 = ft_collect('https://www.ftchinese.com/channel/topnews.html')
        for p in pairs2:
            if p[1] not in [x[1] for x in pairs]:
                pairs.append(p)
    seen = set()
    for t, u in pairs:
        if u in seen: continue
        seen.add(u)
        results['ftchinese'].append({'title': t, 'url': u})
        if len(results['ftchinese']) >= 8: break
except Exception as e:
    print(f"ft fail: {e}")
print(f"ftchinese: {len(results['ftchinese'])}")

with open('/home/hermes_agent/digest/today_news.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False)
print("NEWS_DONE")
