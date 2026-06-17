#!/usr/bin/env python3
"""Debug exact link format on people.cn"""
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'}
req = urllib.request.Request('http://www.people.com.cn/', headers=headers)
resp = urllib.request.urlopen(req, timeout=15, context=ctx)
html = resp.read().decode('utf-8', errors='replace')

import re
# Find ALL a tags and print their href
for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', html):
    url = m.group(1)
    title = m.group(2).strip().replace('\n', ' ')[:50]
    if 'n1/' in url or 'n2/' in url:
        print(f"[{url[:80]}] -> {title}")
