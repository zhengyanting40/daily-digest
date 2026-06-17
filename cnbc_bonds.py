#!/usr/bin/env python3
"""Fetch CNBC bond yields"""
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
result = {}

bonds = {
    'US3M': 'https://www.cnbc.com/quotes/US3M',
    'US5Y': 'https://www.cnbc.com/quotes/US5Y',
    'US10Y': 'https://www.cnbc.com/quotes/US10Y',
    'US30Y': 'https://www.cnbc.com/quotes/US30Y'
}

for name, url in bonds.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='replace')
        # Extract yield - look for patterns like '4.487%'
        matches = re.findall(r'(\d+\.\d+)\s*%', html)
        if matches:
            result[name] = float(matches[0])
        else:
            result[name] = 'parse_failed'
    except Exception as e:
        result[name] = f'error: {e}'

with open('/home/hermes_agent/digest/cnbc_bonds.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=False, indent=2))
