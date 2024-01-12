# freeipa_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://releases.pagure.org/freeipa/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/freeipa/"

# データベースの設定
db_connection = create_connection()
table_name = "freeipa"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# 表からバージョンとLast Modifiedを取得
for row in soup.find_all("tr"):
    columns = row.find_all("td")
    if len(columns) >= 4:
        # ファイル名とリンクを取得
        file_link = columns[1].find("a")
        if file_link:
            href = file_link.get("href")
            file_name = file_link.text.strip()

            # ファイル名が.tar.gzで終わり、CHECKSUMSを除外
            if file_name.endswith(".tar.gz") and "CHECKSUMS" not in file_name:
                # ファイル名からバージョン情報を正規表現で抽出
                version_match = re.match(r'freeipa-(\d+\.\d+\.\d+).*', file_name)
                if version_match:
                    version = version_match.group(1)

                    if not is_version_downloaded(table_name, version, db_connection):
                        # ファイルのLast Modifiedを取得
                        last_modified_str = columns[2].text.strip()
                        last_modified_date = datetime.strptime(last_modified_str, "%Y-%m-%d %H:%M").date()

                        # ファイルをダウンロードし、保存
                        response = requests.get(base_url + href)
                        file_path = os.path.join(download_dir, file_name)
                        save_file(response, file_path)

                        # データベースに格納
                        if db_connection:
                            data = (version, last_modified_date, file_path)
                            insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
