#!/usr/bin/env python3
"""Test data availability."""
import json, os

OUTPUT_DIR = '/home/hermes_agent/digest'

with open(f'{OUTPUT_DIR}/all_data.json') as f:
    yahoo_data = json.load(f)
with open(f'{OUTPUT_DIR}/cn_hk_extra.json') as f:
    cn_data = json.load(f)
with open(f'{OUTPUT_DIR}/news_collected.json') as f:
    news_items = json.load(f)
with open(f'{OUTPUT_DIR}/cn_hk_data.json') as f:
    cn_hk_data = json.load(f)

print('Yahoo keys:', list(yahoo_data.keys()))
print('CN keys:', list(cn_data.keys()))
print('CN HK keys:', list(cn_hk_data.keys()))
print('News count:', len(news_items))

# Filter recent news
finance_news = []
for n in news_items:
    url = n.get('url', '')
    title = n.get('title', '')
    source = n.get('source', '')
    if '2024-' in url or '2025-' in url:
        continue
    if any(kw in title for kw in ['春晚', '李樟煜', '靳东', '郑钦文', '捷强装备']):
        continue
    title_key = title[:20]
    if not any(title_key in f.get('title','') for f in finance_news):
        finance_news.append(n)

print(f'Finance news (filtered): {len(finance_news)}')
for n in finance_news:
    print(f'  [{n.get("source","")}] {n["title"][:50]}')
