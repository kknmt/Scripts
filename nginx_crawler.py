# nginx_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "http://nginx.org/download/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/nginx/"

# データベースの設定
db_connection = create_connection()
table_name = "nginx"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# リンクからバージョンとLast Modifiedを取得
for link in soup.find_all("a", href=re.compile(r"nginx-\d+\.\d+\.\d+\.tar\.gz")):
    href = link.get("href")

    # ファイル名からバージョン情報を正規表現で抽出
    version_match = re.match(r'nginx-(\d+\.\d+\.\d+).*', href)
    if version_match:
        version = version_match.group(1)

        if not is_version_downloaded(table_name, version, db_connection):
            # ファイル名からLast Modifiedを正規表現で抽出
            last_modified_match = re.search(r'\d{2}-[a-zA-Z]{3}-\d{4} \d{2}:\d{2}', link.next_sibling)
            if last_modified_match:
                last_modified_text = last_modified_match.group()
                # 日付部分だけ取得
                date_part = re.search(r"\d{2}-[a-zA-Z]{3}-\d{4}", last_modified_text)
                if date_part:
                    date_part = date_part.group()
                else:
                    continue

                # 日付部分だけ取得
                last_modified_date = datetime.strptime(date_part, "%d-%b-%Y").date()

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
