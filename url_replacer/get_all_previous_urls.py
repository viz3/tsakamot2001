import requests
from bs4 import BeautifulSoup

def get_all_previous_urls(start_url):
    current_url = start_url
    visited_urls = []

    while current_url:
        print(f"Fetching: {current_url}")
        visited_urls.append(current_url)
        
        response = requests.get(current_url)
        if response.status_code != 200:
            print(f"Failed to fetch {current_url}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        prev_link_div = soup.find('div', class_='pager_entry_prev')

        if prev_link_div is None:
            break

        a_tag = prev_link_div.find('a')
        if a_tag and 'href' in a_tag.attrs:
            current_url = a_tag['href']
        else:
            break

    return visited_urls

# 実行とファイル保存
start_url = "https://turedureski.blog.fc2.com/blog-entry-3.html"
all_urls = get_all_previous_urls(start_url)

# 出力ファイル名
output_filename = "fc2_blog_urls.txt"

# ファイルに保存（新しい順）
with open(output_filename, 'w', encoding='utf-8') as f:
    for url in all_urls:
        f.write(url + '\n')

print(f"\nURL一覧をファイルに保存しました: {output_filename}")

