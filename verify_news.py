#!/usr/bin/env python3
import json
with open('/home/hermes_agent/digest/today_news.json') as f: d=json.load(f)
for k,v in d.items():
    print(f'{k}: {len(v)}条')
    for i,it in enumerate(v[:3]):
        print(f'  {i+1}. {it["title"][:50]}')
