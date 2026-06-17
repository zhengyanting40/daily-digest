#!/usr/bin/env python3
import json
with open('/home/hermes_agent/digest/today_yf.json') as f:
    d = json.load(f)
print("=== Bond Yields ===")
for s in ['^IRX', '^FVX', '^TNX', '^TYX']:
    v = d.get(s, {})
    print(f"  {s}: {v.get('price','?')} ({v.get('pct',0):+.2f}%)")

print("\n=== Commodities ===")
for name in ['gold','crude','silver','copper']:
    v = d.get(name, {})
    print(f"  {name}: {v.get('price','?')} ({v.get('pct',0):+.2f}%)")

print("\n=== Crypto ===")
for name in ['btc','eth']:
    v = d.get(name, {})
    print(f"  {name}: {v.get('price','?')} ({v.get('pct',0):+.2f}%)")

print("\n=== International Indices ===")
for name in ['nikkei','kospi','ftse100','stoxx50','asx200','nifty50','dax','cac40']:
    v = d.get(name, {})
    print(f"  {name}: {v.get('price','?')} ({v.get('pct',0):+.2f}%)")

print(f"\n=== DXY ===")
print(f"  {d.get('dxy',{})}")

print(f"\n=== Top Gainers ===")
tg = d.get('top_gainers', [])
print(f"  count: {len(tg)}")
for s in tg[:10]:
    print(f"  {s.get('symbol','?')}: {s.get('name','?')} @ {s.get('price','?')} ({s.get('pct',0):+.2f}%)")
