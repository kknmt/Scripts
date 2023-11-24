# httpd_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ダウンロード済みのバージョン情報ファイル
downloaded_versions_file = "/var/repository/downloaded_versions.txt"
downloaded_versions = []

# ソフトウェアのベースURL
base_url = "https://archive.apache.org/dist/httpd/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/apache/"

# データベースの設定
db_connection = create_connection()
table_name = "apache"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# aタグからバージョンとLast Modifiedを取得
for link in soup.find_all("a"):
    href = link.get("href")

    # ファイル名が.tar.gzで終わり、beta版、alpha版、deps版を除外
    if (
        href
        and href.endswith(".tar.gz")
        and not any(keyword in href for keyword in ["-alpha", "-deps", "-beta"])
    ):
        # ファイル名からバージョン情報を正規表現で抽出
        version_match = re.match(r'httpd-(\d+\.\d+\.\d+).*', href)
        if version_match:
            version = version_match.group(1)

            if not is_version_downloaded(table_name, version, db_connection):
                # ファイルのLast Modifiedを取得
                # 直後のテキストを取得
                next_sibling = link.find_next("a").find_next_sibling(string=True)
                if next_sibling:  # Noneでないことを確認
                    # 数字とハイフン、コロン以外の文字を削除
                    last_modified = re.sub(r"[^0-9:-]", "", next_sibling).strip()

                    # 日付部分だけ取得
                    date_part = re.search(r"\d{4}-\d{2}-\d{2}", last_modified)
                    if date_part:
                        date_part = date_part.group()
                    else:
                        continue

                    # 日付部分だけ取得
                    last_modified_date = datetime.strptime(date_part, "%Y-%m-%d").date()

                    # ファイルをダウンロードし、保存
                    response = requests.get(base_url + href)
                    file_path = os.path.join(download_dir, href)
                    save_file(response, file_path)

                    # データベースに格納
                    if db_connection:
                        data = (version, last_modified_date, file_path)  
                        insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
