# postgresql_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://www.postgresql.org/ftp/source/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/postgresql/"

# データベースの設定
db_connection = create_connection()
table_name = "postgresql"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# バージョンごとのリンクを取得
for version_link in soup.find_all("a", href=re.compile(r'^v\d+\.\d+/')):
    version_url = base_url + version_link.get("href")

    # バージョンごとのHTMLを取得
    version_response = requests.get(version_url)
    version_soup = BeautifulSoup(version_response.text, "html.parser")

    # ファイル情報を取得
    for file_row in version_soup.select("#pgFtpContent table tr"):
        file_link = file_row.find("a", href=True)
        file_date = file_row.find_all("td")[1].text.strip()

        if file_link:
            href = file_link["href"]

            # ファイル名が.tar.gzで終わる場合のみ処理
            if href.endswith(".tar.gz"):
                # ファイル名からバージョン情報を正規表現で抽出
                version_match = re.match(r'postgresql-(\d+(\.\d+)*)', href)
                if version_match:
                    version = version_match.group(1)

                    # ファイルのLast Modifiedを取得
                    last_modified_date = datetime.strptime(file_date, "%Y-%m-%d %H:%M:%S").date()

                    # ファイルをダウンロードし、保存
                    response = requests.get(version_url + href)
                    file_path = os.path.join(download_dir, href)
                    save_file(response, file_path)

                    # データベースに格納
                    if db_connection:
                        data = (version, last_modified_date, file_path)
                        insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
