import os
import re
from datetime import datetime
from collections import defaultdict

EXPORT_DIR = "exported_blog"

# カテゴリID → (カテゴリ名, [(タイトル, ファイル名, 投稿日時)]) の辞書
category_map = defaultdict(list)
category_name_map = {}

for filename in os.listdir(EXPORT_DIR):
    if not filename.endswith(".md"):
        continue

    path = os.path.join(EXPORT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 5:
        continue

    # タイトル・日付・カテゴリ行抽出
    title = lines[0].strip().lstrip("#").strip()
    date_line = lines[2].strip()
    category_line = lines[4].strip()

    # 投稿日時の抽出
    date_match = re.search(r"📅 投稿日時: ([\d\-]+\s[\d:]+)", date_line)
    if not date_match:
        continue
    try:
        published_at = datetime.strptime(date_match.group(1), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        continue

    # カテゴリ名とIDの抽出
    cat_match = re.search(r'\[(.+?)\]\((.+?)\.md\)', category_line)
    if cat_match:
        category_name = cat_match.group(1)
        category_id = cat_match.group(2)

        category_map[category_id].append((title, filename, published_at))
        category_name_map[category_id] = category_name

# 各カテゴリごとにリンク集を作成（投稿日順）
for category_id, entries in category_map.items():
    category_name = category_name_map.get(category_id, category_id)
    md_path = os.path.join(EXPORT_DIR, f"{category_id}.md")

    # 投稿日時順でソート
    entries.sort(key=lambda x: x[2])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 🏷️ {category_name}\n\n")
        for title, fname, published_at in entries:
            date_str = published_at.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"- [{title}]({fname}) （{date_str}）\n")

print("✅ カテゴリリンク集を投稿日時順で作成しました！")

# === 全カテゴリのリンク集を README.md に出力 ===
category_path = os.path.join(EXPORT_DIR, "CATEGORY.md")

with open(category_path, "w", encoding="utf-8") as f:
    f.write("# 🗂️ カテゴリ一覧\n\n")
    # カテゴリ名の五十音順（またはアルファベット順）でソート
    for category_id, category_name in sorted(category_name_map.items(), key=lambda x: x[1]):
        f.write(f"- [{category_name}]({category_id}.md)\n")

print("✅ 全カテゴリ一覧 CATEGORY.md を作成しました！")

