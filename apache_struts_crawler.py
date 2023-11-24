# apache_struts_crawler.py
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
base_url = "https://archive.apache.org/dist/struts/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/apache_struts/"

# データベースの設定
db_connection = create_connection()
table_name = "apache_struts"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# バージョンのサブディレクトリにアクセス
for version_link in soup.find_all("a", href=re.compile(r'^\d+\.\d+\.\d+/$')):
    version_url = base_url + version_link['href']

    # バージョンごとのHTMLを取得
    version_response = requests.get(version_url)
    version_soup = BeautifulSoup(version_response.text, "html.parser")

    # aタグからバージョンとLast Modifiedを取得
    for link in version_soup.find_all("a"):
        file_href = link.get("href")

        # ファイル名が.zipで終わり、.md5, .sha1などを除外
        if (
            file_href
            and file_href.endswith(".zip")
            and "all" in file_href
            and not any(ext in file_href for ext in [".md5", ".sha1", ".sha256", ".sha512", ".asc"])
        ):
            # ファイル名からバージョン情報を正規表現で抽出
            version_match = re.match(r'struts-(\d+\.\d+\.\d+).*', file_href)
            if version_match:
                version = version_match.group(1)

                # ファイルがダウンロード済みか確認
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
                        response = requests.get(version_url + file_href)
                        file_path = os.path.join(download_dir, file_href)
                        save_file(response, file_path)

                        # データベースに格納
                        if db_connection:
                            data = (version, last_modified_date, file_path)
                            insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
