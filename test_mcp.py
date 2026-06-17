#!/usr/bin/env python3
"""Test MCP connection format."""
import json
import urllib.request
import urllib.error

MCP_URL = "http://mcp.finance.sina.com.cn/mcp-http"
AUTH_TOKEN = "0be4facb91bb0744437948d188471694"

# Try tools/list
payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
req = urllib.request.Request(
    MCP_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json", "X-Auth-Token": AUTH_TOKEN}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("Status:", resp.status)
        print("Response:", json.dumps(data, ensure_ascii=False)[:1000])
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    body = e.read().decode("utf-8", errors="replace")
    print("Body:", body[:1000])
except Exception as e:
    print(f"Error: {e}")

# Try a different format - maybe needs Content-Type header different
print("\n--- Try with different content type ---")
req2 = urllib.request.Request(
    MCP_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "text/plain", "X-Auth-Token": AUTH_TOKEN}
)
try:
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        data2 = json.loads(resp2.read().decode("utf-8"))
        print("Status:", resp2.status)
        print("Response:", json.dumps(data2, ensure_ascii=False)[:500])
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    body = e.read().decode("utf-8", errors="replace")
    print("Body:", body[:500])
except Exception as e:
    print(f"Error: {e}")
