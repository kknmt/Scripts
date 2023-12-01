# unbound_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://nlnetlabs.nl/projects/unbound/download/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/unbound/"

# データベースの設定
db_connection = create_connection()
table_name = "unbound"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# ソフトウェアのバージョン情報とダウンロードリンクを取得
for version_section in soup.find_all("div", class_="section"):
    version_header = version_section.find("h3")
    if version_header:
        version_match = re.match(r'Unbound (\d+\.\d+\.\d+)', version_header.string)
        if version_match:
            version = version_match.group(1)

            if not is_version_downloaded(table_name, version, db_connection):
                download_links = version_section.find_all("a", href=re.compile(r'\.tar\.gz$'))
                for download_link in download_links:
                    download_href = download_link.get("href")

                    # ファイルのLast Modifiedを取得
                    date_element = version_section.find("dt", string="Date:")
                    if date_element:
                        last_modified_date = datetime.strptime(date_element.find_next("dd").text.strip(), "%d %b, %Y").date()

                        # ファイルをダウンロードし、保存
                        response = requests.get(base_url + download_href)
                        file_path = os.path.join(download_dir, download_href.split("/")[-1])
                        save_file(response, file_path)

                        # データベースに格納
                        if db_connection:
                            data = (version, last_modified_date, file_path)
                            insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
