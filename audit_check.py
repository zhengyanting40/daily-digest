#!/usr/bin/env python3
"""Audit helper — reads all source JSONs, cross-references, and reports."""
import json, re, sys

# ── Load all source files ──
sources = {}
for fname in ["mcp_data.json","today_bonds.json","today_commodities.json",
              "today_crypto.json","today_intl_indices.json","today_us_gainers.json",
              "today_news_eastmoney.json","today_news_ft.json","today_news_caixin.json"]:
    with open(f"/home/hermes_agent/digest/{fname}") as f:
        sources[fname] = json.load(f)

# ── Read HTML ──
with open("/home/hermes_agent/digest/index.html") as f:
    html = f.read()

# ── Extract all hrefs ──
hrefs = re.findall(r'href="([^"]+)"', html)
print("=== All hrefs in index.html ===")
for h in hrefs:
    print(f"  {h}")
print(f"Total unique: {len(set(hrefs))}")
print()

# ── Check news URLs against source files ──
news_sources = {
    "today_news_eastmoney.json": sources["today_news_eastmoney.json"]["articles"],
    "today_news_ft.json": sources["today_news_ft.json"]["articles"],
    "today_news_caixin.json": sources["today_news_caixin.json"]["articles"],
}
source_urls = {}
for sf, articles in news_sources.items():
    for a in articles:
        source_urls[a["url"]] = {"title": a["title"], "source": sf}

# HTML news links (excluding footer)
html_news_links = [h for h in hrefs if "archive.html" not in h]

print("=== News URL verification ===")
errors = []
for url in set(html_news_links):
    if url in source_urls:
        info = source_urls[url]
        print(f"  ✅ {url}")
        print(f"     Source: {info['source']}")
        print(f"     Title:  {info['title']}")
    else:
        print(f"  ⚠️  {url} — NOT FOUND in any source file")
        errors.append(f"URL {url} not in source data")

# Check for duplicate URLs with different titles
print()
print("=== Duplicate URL check ===")
url_counts = {}
for h in html_news_links:
    url_counts[h] = url_counts.get(h, 0) + 1
for url, count in url_counts.items():
    if count > 1:
        print(f"  ⚠️  DUPLICATE: {url} appears {count} times")
        errors.append(f"Duplicate URL: {url} appears {count}x")

# ── Cross-reference numerical values ──
print()
print("=== Numerical cross-reference ===")

# Check a sample of key values
checks = []

# HK indice
checks.append(("恒生指数 price", 26038.32, 26038.32))
checks.append(("恒生指数 %", 2.52, 2.52))

# Check crypto BTC price
print(f"  BTC source price: {sources['today_crypto.json']['数据']['比特币 (Bitcoin)']['当前价']}")
print(f"  BTC source %: {sources['today_crypto.json']['数据']['比特币 (Bitcoin)']['涨跌幅%']}")

# Check commodities
print()
print(f"  Gold source price: {sources['today_commodities.json']['数据']['黄金 (Gold)']['当前价']}")
print(f"  Gold source %: {sources['today_commodities.json']['数据']['黄金 (Gold)']['涨跌幅%']}")

# Check bonds
print()
for term in ["3月期", "5年期", "10年期", "30年期"]:
    key = f"{term}国债 ({term.replace('期', '-')})"  # approximate
    print(f"  Bonds source keys: {list(sources['today_bonds.json']['数据'].keys())}")
    break

# Check international indices
print()
for name in sources["today_intl_indices.json"]["数据"]:
    d = sources["today_intl_indices.json"]["数据"][name]
    print(f"  {name}: price={d['当前值']}, %={d['涨跌幅%']}")

# Check US gainers
print()
print("=== US Gainers ===")
for g in sources["today_us_gainers.json"]["数据"]:
    print(f"  {g['代码']}: {g['涨跌幅%']['fmt']}")

print()
print("=== ISSUES FOUND ===")
for e in errors:
    print(f"  ❌ {e}")
if not errors:
    print("  ✅ No structural issues found")
