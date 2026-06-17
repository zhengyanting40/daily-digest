#!/usr/bin/env python3
"""Update YF data with correct bond changes from range=1mo"""
import json

with open('/home/hermes_agent/digest/today_yf.json', 'r') as f:
    data = json.load(f)

# Update bonds with correct change data from our debug
bond_fixes = {
    'US3M': {'price': 3.63, 'change': 0.012, 'pct': 0.33},
    'US5Y': {'price': 4.151, 'change': -0.062, 'pct': -1.47},
    'US10Y': {'price': 4.428, 'change': -0.059, 'pct': -1.31},
    'US30Y': {'price': 4.928, 'change': -0.047, 'pct': -0.94}
}

for k, v in bond_fixes.items():
    data[k] = v

with open('/home/hermes_agent/digest/today_yf.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Bond data updated successfully")
for k in ['US3M','US5Y','US10Y','US30Y']:
    d = data[k]
    print(f'  {k}: {d["price"]}% ({d["pct"]:+.2f}%)')
