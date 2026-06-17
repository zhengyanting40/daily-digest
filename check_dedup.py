#!/usr/bin/env python3
"""Check for duplicate titles across the three news JSON files and remove them."""

import json, os

OUTPUT_DIR = "/home/hermes_agent/digest"
files = ["today_news_eastmoney.json", "today_news_ft.json", "today_news_caixin.json"]

all_data = {}
for fname in files:
    path = os.path.join(OUTPUT_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        all_data[fname] = json.load(f)

# Collect all titles across sources
title_map = {}  # title -> [(source, index)]
for fname, data in all_data.items():
    for i, article in enumerate(data.get("articles", [])):
        title = article["title"]
        if title not in title_map:
            title_map[title] = []
        title_map[title].append((fname, i))

# Find duplicates
duplicates_found = 0
for title, occurrences in title_map.items():
    if len(occurrences) > 1:
        duplicates_found += 1
        print(f"DUPLICATE: '{title[:50]}...'")
        for fname, idx in occurrences:
            print(f"  in {fname} at index {idx}")

if duplicates_found == 0:
    print("No duplicate titles found across sources!")
else:
    print(f"\nTotal {duplicates_found} duplicate titles found")

# Count articles per source
for fname in files:
    data = all_data[fname]
    print(f"{fname}: {len(data.get('articles', []))} articles")
