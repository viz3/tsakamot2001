import argparse
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import re

def extract_post_id(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    return f"{path_parts[1]}{path_parts[2]}"

# 引数の処理
parser = argparse.ArgumentParser(description="Export a single goo blog post to markdown.")
parser.add_argument("url", help="URL of the goo blog article to export")
args = parser.parse_args()

ARTICLE_URL = args.url

# === 保存先 ===
SAVE_DIR = ".."
IMAGE_DIR = os.path.join(SAVE_DIR, "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

res = requests.get(ARTICLE_URL)
soup = BeautifulSoup(res.text, "html.parser")

# === タイトルと日付 ===
title_tag = soup.select_one("div.entry-top h3")
title = title_tag.get_text(strip=True) if title_tag else "Untitled"

date_tag = soup.select_one("span.entry-top-info-time")
date = date_tag.get_text(strip=True) if date_tag else "Unknown Date"

# === カテゴリ情報の抽出 ===
category_tag = soup.select_one("span.entry-top-info-category")
category_text = category_tag.get_text(strip=True) if category_tag else "No Category"

category_link_id = ""
if category_tag:
    if category_tag.parent.name == "a" and category_tag.parent.has_attr("href"):
        full_link = category_tag.parent["href"]
    else:
        prev_a = category_tag.find_previous("a", href=True)
        full_link = prev_a["href"] if prev_a else ""
    if full_link.startswith("/tsakamot2001/"):
        # ベースパスを取り除いて、残りを / を削除して結合
        remaining_path = full_link.replace("/tsakamot2001/", "")
        category_link_id = remaining_path.replace("/", "")  # 例: 'c/xxxx' → 'cxxxx'

# === 本文 ===
def convert_internal_links(body_tag):
    for a in body_tag.find_all("a", href=True):
        href = a["href"]
        if "/tsakamot2001/" in href:
            article_id = extract_post_id(href)
            a["href"] = f"{article_id}.md"
    return body_tag

body_tag = soup.select_one("div.entry-body-text")
body_tag = convert_internal_links(body_tag)

markdown_body = ""

def process_element(elem):
    global markdown_body
    if isinstance(elem, str):
        markdown_body += elem
    elif elem.name == "br":
        markdown_body += "\n\n"
    elif elem.name == "img":
        # 親が <a> タグなら、その href を使う
        parent = elem.parent
        if parent and parent.name == "a" and parent.has_attr("href"):
            img_url = parent["href"]
        elif elem.has_attr("src"):
            img_url = urljoin(ARTICLE_URL, elem["src"])
        else:
            return  # src も href もなければスキップ

        img_filename = os.path.basename(img_url.split("?")[0])
        img_path = os.path.join(IMAGE_DIR, img_filename)

        # 画像保存
        try:
            img_data = requests.get(img_url).content
            with open(img_path, "wb") as f:
                f.write(img_data)
            markdown_body += f"\n\n![{img_filename}](images/{img_filename})\n\n"
        except Exception as e:
            print(f"⚠️ 画像保存失敗: {img_url}, エラー: {e}")
    elif elem.name == "a":
        href = elem.get("href", "")
        text = "".join(elem.strings).strip()
        markdown_body += f"[{text}]({href})"
    else:
        for child in elem.children:
            process_element(child)

# 本文処理開始
if body_tag:
    process_element(body_tag)
    markdown_body = markdown_body.strip()

markdown_body += "\n"  # 最後に1行入れて整える

# === コメント ===
comment_blocks = []
comment_dls = soup.select("div.comment-list-body dl[data-id]")

for dl in comment_dls:
    title_tag = dl.select_one("span.comment-list-title")
    name_tag = dl.select_one("span.comment-list-name")
    date_tag = dl.select_one("dd.comment-list-date")
    text_tag = dl.select_one("dd.comment-list-text")

    c_title = title_tag.get_text(strip=True) if title_tag else "Unknown"
    c_name = name_tag.get_text(strip=True) if name_tag else "匿名"
    c_date = date_tag.get_text(strip=True) if date_tag else "Unknown Date"

    # コメント本文の <br> 改行対応
    if text_tag:
        comment_html = str(text_tag)
        comment_soup = BeautifulSoup(comment_html, "html.parser")
        for br in comment_soup.find_all("br"):
            br.replace_with("\n\n")
        c_text = comment_soup.get_text().strip()
    else:
        c_text = ""

    comment_md = f"""### 💬 コメント by {c_name}
**タイトル**: {c_title}
**投稿日**: {c_date}

{c_text}
"""
    comment_blocks.append(comment_md)

# === Markdown保存 ===
safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
post_id = extract_post_id(ARTICLE_URL)
md_filename = os.path.join(SAVE_DIR, f"{post_id}.md")

with open(md_filename, "w", encoding="utf-8") as f:
    f.write(f"# {title}\n\n")
    f.write(f"📅 投稿日時: {date}\n\n")
    f.write(f"🏷️ カテゴリ: [{category_text}]({category_link_id}.md)\n\n")
    f.write(markdown_body)

    if comment_blocks:
        f.write("\n## 💬 コメント一覧\n\n")
        for block in comment_blocks:
            f.write(block + "\n")

print(f"✅ 完了！Markdownを保存しました: {md_filename}")

