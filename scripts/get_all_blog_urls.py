import requests
from bs4 import BeautifulSoup
import time

START_URL = "https://blog.goo.ne.jp/tsakamot2001/e/c2e9e21de4a6795cd0bcc871a42c1f1b"
visited_urls = []

current_url = START_URL

while current_url:
    print(f"Fetching: {current_url}")
    visited_urls.append(current_url)

    try:
        res = requests.get(current_url)
        res.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {current_url}: {e}")
        break

    soup = BeautifulSoup(res.text, "html.parser")

    # 「次の記事」リンクを探す
    next_link_tag = soup.select_one("li.mod-pre-nex-next a")
    if next_link_tag and "href" in next_link_tag.attrs:
        next_url = next_link_tag["href"]
        if not next_url.startswith("http"):
            # 絶対URLにする（gooブログは相対URL）
            next_url = "https://blog.goo.ne.jp" + next_url
        if next_url in visited_urls:
            print("循環リンクを検出。終了します。")
            break
        current_url = next_url
    else:
        print("次の記事が見つかりません。終了します。")
        break

    time.sleep(1)  # サーバーに優しく（必要なら）

# URL一覧をファイルに保存
with open("blog_urls.txt", "w", encoding="utf-8") as f:
    for url in visited_urls:
        f.write(url + "\n")

print(f"取得完了：{len(visited_urls)} 件のURLを保存しました。")

