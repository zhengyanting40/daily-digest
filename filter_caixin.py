#!/usr/bin/env python3
"""Filter caixin news for financial/economics key news - keep 6-8 best items"""

import json

# Read all items
with open("/home/hermes_agent/digest/caixin_news_0604.json", "r") as f:
    all_items = json.load(f)

# Keywords indicating non-financial content to exclude
exclude_keywords = [
    '讣闻', '照片', '图片', '夜读精选', '假球', '赌球', '世界杯',
    '酒店火灾', '火车与卡车', '韩国地方选举', '黎以', '停火协议',
]

# Keep only finance/economics/business related items
# Focus on sections: finance, economy, companies, www.caixin.com (main news)
financial_news = []
for item in all_items:
    title = item['title']
    url = item['url']
    
    # Skip items with exclude keywords
    skip = False
    for kw in exclude_keywords:
        if kw in title:
            skip = True
            break
    if skip:
        continue
    
    # Skip opinion/promotion sections
    if '/opinion.' in url or 'promote.' in url or '/photos.' in url:
        continue
    
    # Skip very short titles
    if len(title) < 10:
        continue
    
    # Skip promotion/data links
    if '数据通' in title or 'Promotion' in title or 'Claw' in title:
        continue
    
    financial_news.append(item)

# Keep top 8
selected = financial_news[:8]

print(f"Filtered from {len(all_items)} to {len(selected)} financial news items\n")

for i, item in enumerate(selected, 1):
    print(f"{i}. {item['title']}")
    print(f"   {item['url']}")
    print()

# Save filtered results
with open("/home/hermes_agent/digest/caixin_news_0604.json", "w") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

print(f"Saved {len(selected)} items to /home/hermes_agent/digest/caixin_news_0604.json")
