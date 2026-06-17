#!/usr/bin/env python3
"""Debug sector page format."""
import urllib.request
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

url = "https://vip.stock.finance.sina.com.cn/q/go.php/vIndustryRank/kind/jg/index.phtml"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
    html = resp.read().decode("gbk", errors="replace")

# Save raw HTML for inspection
with open("/home/hermes_agent/digest/sector_page.html", "w", encoding="utf-8") as f:
    f.write(html)

# Print first 2000 chars
print(html[:2000])
print("\n\n=== Looking for table rows ===")
import re
# Look for <tr> patterns
trs = re.findall(r'<tr[^>]*>', html)
print(f"Found {len(trs)} <tr> tags")
for t in trs[:10]:
    print(f"  {t[:100]}")

# Try alternative: look for stock names
stocks = re.findall(r'[\u4e00-\u9fff]{2,}[（(]\d{6}[）)]', html)
print(f"\nStock codes found: {len(stocks)}")
for s in stocks[:5]:
    print(f"  {s}")
