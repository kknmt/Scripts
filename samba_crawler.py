# samba_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://download.samba.org/pub/samba/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/samba/"

# データベースの設定
db_connection = create_connection()
table_name = "samba"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# trタグからバージョンとLast Modifiedを取得
for row in soup.find_all("tr", class_=re.compile("even|odd")):
    columns = row.find_all("td")

    # ファイル名が.tar.gzで終わり、beta版、alpha版、deps版を除外
    if (
        len(columns) >= 2
        and columns[1].find("a") is not None
        and columns[1].find("a").get("href").endswith(".tar.gz")
        and not any(keyword in columns[1].find("a").get("href") for keyword in ["-alpha", "-deps", "-beta"])
    ):
        version_match = re.match(r'samba-(\d+\.\d+\.\d+).*', columns[1].find("a").text)
        if version_match:
            version = version_match.group(1)

            if not is_version_downloaded(table_name, version, db_connection):
                last_modified = columns[2].text.strip()

                # 日付部分だけ取得
                date_part = re.search(r"\d{4}-\d{2}-\d{2}", last_modified)
                if date_part:
                    date_part = date_part.group()
                else:
                    continue

                # 日付部分だけ取得
                last_modified_date = datetime.strptime(date_part, "%Y-%m-%d").date()

                # ファイルをダウンロードし、保存
                file_path = os.path.join(download_dir, columns[1].find("a").get("href"))
                response = requests.get(base_url + columns[1].find("a").get("href"))
                save_file(response, file_path)

                # データベースに格納
                if db_connection:
                    data = (version, last_modified_date, file_path)
                    insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
