# openssl_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, mark_version_as_downloaded, save_file
from database_utils import create_connection, insert_data

# ダウンロード済みのバージョン情報ファイル
downloaded_versions_file = "/var/repository/downloaded_versions.txt"
downloaded_versions = []

# ソフトウェアのベースURL
base_url = "https://www.openssl.org/source/old/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/openssl/"

# データベースの設定
db_connection = create_connection()
table_name = "openssl"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# バージョンごとのページに移動
for version_link in soup.find_all("a", href=re.compile(r'\d+\.\d+/$')):
    version_url = base_url + version_link.get("href")
    print("Version URL:", version_url)

    # HTMLを取得
    version_response = requests.get(version_url)
    version_soup = BeautifulSoup(version_response.text, "html.parser")

    for link in version_soup.find_all("a", href=re.compile(r'openssl-\d+\.\d+\.\d+.tar.gz$')):
        file_url = version_url + link.get("href")
        print("File URL:", file_url)

        version_match = re.match(r'openssl-(\d+\.\d+\.\d+).*', link.get("href"))
        if version_match:
            version = version_match.group(1)

            try:
                if not is_version_downloaded("openssl", version, downloaded_versions):
                    next_sibling = link.find_next("td").find_next_sibling(string=True)
                    if next_sibling:
                        last_modified = re.sub(r"[^0-9:-]", "", next_sibling).strip()

                        date_part = re.search(r"\d{4}-\d{2}-\d{2}", last_modified)
                        if date_part:
                            date_part = date_part.group()
                        else:
                            continue

                        last_modified_date = datetime.strptime(date_part, "%Y-%m-%d").date()

                        response = requests.get(file_url)
                        file_path = os.path.join(download_dir, link.get("href"))
                        save_file(response, file_path)

                        if db_connection:
                            data = (version, last_modified_date, file_path)
                            insert_data(db_connection, table_name, data)

                        mark_version_as_downloaded("openssl", version, downloaded_versions, downloaded_versions_file)
            except Exception as e:
                print(f"Error: {e}")

# データベース接続を閉じる
if db_connection:
    db_connection.close()
