#!/usr/bin/env python3
"""Trim articles to target counts and re-save."""

import json, os

OUTPUT_DIR = "/home/hermes_agent/digest"

targets = {
    "today_news_eastmoney.json": 8,
    "today_news_ft.json": 10,
    "today_news_caixin.json": 8,
}

for fname, target_count in targets.items():
    path = os.path.join(OUTPUT_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get("articles", [])
    if len(articles) > target_count:
        data["articles"] = articles[:target_count]
        print(f"{fname}: trimmed from {len(articles)} to {target_count}")
    else:
        print(f"{fname}: {len(articles)} articles (target: {target_count})")
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("\nDone.")
