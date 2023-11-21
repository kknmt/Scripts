import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

base_url = "https://archive.apache.org/dist/httpd/"
downloaded_versions_file = "/var/repository/apache/downloaded_versions.txt"

# ダウンロード済みのバージョン情報を読み込む
downloaded_versions = set()
if os.path.exists(downloaded_versions_file):
    with open(downloaded_versions_file, "r") as file:
        downloaded_versions = set(file.read().splitlines())

# HTTP GETリクエストを送り、HTMLを取得
response = requests.get(base_url)
html_content = response.content

# BeautifulSoupを使用してHTMLを解析
soup = BeautifulSoup(html_content, "html.parser")

# 正規表現でbeta版をフィルタリング
beta_regex = re.compile(r'.*beta.*', re.IGNORECASE)

# aタグからバージョンとLast Modifiedを取得
for link in soup.find_all("a"):
    href = link.get("href")

    # ファイル名が.tar.gzで終わり、beta版を除外
    if href and href.endswith(".tar.gz") and not beta_regex.match(href):
        # ファイル名からバージョン情報を正規表現で抽出
        version_match = re.match(r'httpd-(\d+\.\d+\.\d+).*', href)
        if version_match:
            version = version_match.group(1)

            # ダウンロード済みのバージョンか確認
            if version not in downloaded_versions:
                file_url = base_url + href

                # ファイルのLast Modifiedを取得
                last_modified = link.parent.find_next("td").text.strip()
                last_modified_date = datetime.strptime(last_modified, "%Y-%m-%d %H:%M")

                print(f"Downloading Version: {version}, File URL: {file_url}, Last Modified: {last_modified_date}")

                # ファイルをダウンロードし、保存
                # ここにダウンロードの処理を追加

                # ダウンロード済みのバージョン情報を追加
                downloaded_versions.add(version)

# ダウンロード済みのバージョン情報を保存
with open(downloaded_versions_file, "w") as file:
    file.write("\n".join(downloaded_versions))
