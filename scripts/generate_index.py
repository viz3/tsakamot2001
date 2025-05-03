import os
import re
import fnmatch
from datetime import datetime

SAVE_DIR = ".."
OFNAME_PATH = os.path.join(SAVE_DIR, "ARTICLES.md")

entries = []

# === Markdown ファイルを走査 ===
for filename in os.listdir(SAVE_DIR):
    if not fnmatch.fnmatch(filename, "e*.md"):
        continue

    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 3:
        continue  # 最低限の情報がない場合はスキップ

    # タイトル（1行目の # 見出し）
    title_line = lines[0].strip()
    title_match = re.match(r"#\s+(.*)", title_line)
    title = title_match.group(1) if title_match else "Untitled"

    # 投稿日時（3行目にある 📅）
    date_line = lines[2].strip()
    date_match = re.search(r"📅 投稿日時:\s*(.+)", date_line)
    date_str = date_match.group(1) if date_match else "1900-01-01 00:00:00"

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime(1900, 1, 1)

    entries.append((dt, title, filename))

# === 投稿日時でソート ===
entries.sort()

# === ARTICLES.md を生成 ===
with open(OFNAME_PATH, "w", encoding="utf-8") as f:
    f.write("## 記事一覧\n\n")
    for dt, title, filename in entries:
        f.write(f"- [{title}]({filename}) ({dt.strftime('%Y-%m-%d %H:%M')})\n")

print(f"✅ ARTICLES.md を作成しました: {OFNAME_PATH}")

