#!/bin/bash
# Git push to daily-digest repo
set -e
cd /home/hermes_agent/digest

# Setup git config
git config user.name "Hermes Agent" 2>/dev/null || true
git config user.email "hermes@nousresearch.com" 2>/dev/null || true

TODAY=$(date +%Y-%m-%d)
ARCHIVE_DIR="archive"

mkdir -p "$ARCHIVE_DIR"

# Backup current index if it exists
if [ -f index.html ] && [ ! -f "$ARCHIVE_DIR/$TODAY.html" ]; then
    cp index.html "$ARCHIVE_DIR/$TODAY.html"
    echo "Archived to $ARCHIVE_DIR/$TODAY.html"
fi

# Update archive.html (simple listing)
{
    echo '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>每日新闻速递 - 存档</title><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{font-family:sans-serif;background:#0d1117;color:#c9d1d9;padding:20px;max-width:640px;margin:0 auto}h1{color:#f0f6fc}a{color:#58a6ff;text-decoration:none}ul{list-style:none;padding:0}li{padding:6px 0;border-bottom:1px solid #21262d}.date{color:#8b949e;font-size:13px}</style></head><body><h1>📅 每日新闻速递 存档</h1><ul>'
    for f in $(ls archive/*.html 2>/dev/null | sort -r); do
        d=$(basename "$f" .html)
        echo "<li><a href=\"$f\">📊 $d</a></li>"
    done
    echo '<li><a href="index.html">📊 最新今日速递</a></li>'
    echo '</ul><div class="footer" style="text-align:center;color:#484f58;padding:20px;font-size:12px">每日自动更新</div></body></html>'
} > archive.html.new
mv archive.html.new archive.html

# Commit and push
git add index.html archive/ archive.html
git diff --cached --quiet || git commit -m "📊 每日新闻速递 $TODAY"
GIT_ASKPASS=/tmp/git-askpass.sh git push origin main 2>&1 || {
    echo "Git push failed. Trying without askpass..."
    git push origin main 2>&1 || echo "FAILED: Need token"
}
