# mariadb_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://archive.mariadb.org/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/mariadb/"

# データベースの設定
db_connection = create_connection()
table_name = "mariadb"

# ダウンロード先ディレクトリを作成
os.makedirs(download_dir, exist_ok=True)

# ダウンロードページのベースURL
download_page_base_url = "https://archive.mariadb.org/{}/source/"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# ダウンロードリンクの一覧を取得
download_links = soup.find_all("a", href=re.compile(r"mariadb-\d+\.\d+\.\d+\/"))

# ダウンロード先ディレクトリを作成
os.makedirs(download_dir, exist_ok=True)

# ダウンロードリンクからバージョンとダウンロードURLを取得
for link in download_links:
    version_match = re.match(r'mariadb-(\d+\.\d+\.\d+)\/', link.get("href"))
    if version_match:
        version = version_match.group(1)

        # バージョンの後に"-"がついている場合はスキップ
        if "-" in version:
            continue

        # ダウンロードページのURLを構築
        download_page_url = download_page_base_url.format(link.get("href"))

        # HTMLを取得
        download_response = requests.get(download_page_url)
        download_soup = BeautifulSoup(download_response.text, "html.parser")

        # ファイル一覧のテーブルを取得
        file_table = download_soup.find("pre")

        # ファイル一覧からバージョンとLast Modifiedを取得
        if file_table:
            for file_link in file_table.find_all("a"):
                file_href = file_link.get("href")

                if file_href == "../":
                    continue

                # ファイル名が.tar.gzで終わる場合のみ処理
                if file_href.endswith(".tar.gz"):
                    # ファイルのLast Modifiedを取得
                    last_modified_text = file_link.find_next("a").text.strip()

                    # 日付として正しくパースできるか確認
                    try:
                        last_modified_date = datetime.strptime(last_modified_text, "%d-%b-%Y %H:%M").date()
                    except ValueError:
                        # パースできない場合はスキップ
                        continue

                    # ダウンロードURLを構築
                    file_download_url = f"{base_url}{download_page_url}{file_href}"

                    if not is_version_downloaded(table_name, version, db_connection):
                        # ファイルをダウンロードし、保存
                        response = requests.get(file_download_url)
                        file_path = os.path.join(download_dir, file_href)
                        save_file(response, file_path)

                        # データベースに格納
                        if db_connection:
                            data = (version, last_modified_date, file_path)
                            insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
