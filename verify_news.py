#!/usr/bin/env python3
import json

# Verify eastmoney
with open('/home/hermes_agent/digest/today_news_eastmoney.json') as f:
    data = json.load(f)
print(f'=== 东方财富 ({len(data)} articles) ===')
for i, a in enumerate(data, 1):
    print(f'{i}. {a["title"]}')
    print(f'   {a["url"]}')

print()

# Verify FT
with open('/home/hermes_agent/digest/today_news_ft.json') as f:
    data = json.load(f)
print(f'=== FT中文网 ({len(data)} articles) ===')
for i, a in enumerate(data, 1):
    print(f'{i}. {a["title"]}')
    print(f'   {a["url"]}')
