# openvpn_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://build.openvpn.net/downloads/releases/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/openvpn"

# データベースの設定
db_connection = create_connection()
table_name = "openvpn"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# バージョン情報を含む行を取得
version_rows = soup.find_all("a", href=re.compile(r"openvpn-\d+\.\d+\.\d+\.tar\.gz"))

for row in version_rows:
    href = row.get("href")
    version_match = re.match(r'openvpn-(\d+\.\d+\.\d+)\.tar\.gz', href)

    if version_match:
        version = version_match.group(1)

        if not is_version_downloaded(table_name, version, db_connection):
            # ファイルのLast Modifiedを取得
            # 直後のテキストを取得
            last_modified = row.find_next(string=True).strip()
            print(last_modified)
            # 日付部分だけ取得
            date_part = re.search(r"\d{2}-[a-zA-Z]{3}-\d{4}", last_modified)
            if date_part:
                date_part = date_part.group()
            else:
                continue

            # 日付部分だけ取得
            last_modified_date = datetime.strptime(date_part, "%d-%b-%Y").date()

            # ファイルをダウンロードし、保存
            file_url = base_url + href
            response = requests.get(file_url)
            file_path = os.path.join(download_dir, href)
            save_file(response, file_path)

            # データベースに格納
            if db_connection:
                data = (version, last_modified_date, file_path)
                insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
