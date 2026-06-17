#!/usr/bin/env python3
"""Debug people.cn page structure"""
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'}

req = urllib.request.Request('http://www.people.com.cn/', headers=headers)
resp = urllib.request.urlopen(req, timeout=15, context=ctx)
html = resp.read().decode('utf-8', errors='replace')

import re
# Find ALL links with 'people.com.cn' and some text
links = re.findall(r'<a[^>]*href="(http://[^"]*people\.com\.cn[^"]*)"[^>]*>([^<]{10,80})</a>', html)
print(f"Total links found: {len(links)}")
for url, title in links[:20]:
    print(f"  {title[:50]} -> {url[:80]}")
