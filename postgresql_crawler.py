# postgresql_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://www.postgresql.org/ftp/source/"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# ダウンロード先ディレクトリ
download_dir = "/var/repository/postgresql/"

# データベースの設定
db_connection = create_connection()
table_name = "postgresql"

# フォルダのリンクを取得
folder_links = soup.find_all("a", href=re.compile(r"v\d+\.\d+(\.\d+)?/"))

for folder_link in folder_links:
    folder_url = base_url + folder_link["href"]
    folder_response = requests.get(folder_url)
    folder_soup = BeautifulSoup(folder_response.text, "html.parser")

    # ファイル情報を含む行を取得
    file_rows = folder_soup.find_all("tr")

    for row in file_rows:
        file_info = row.find("a", href=re.compile(r"postgresql-\d+(\.\d+){0,2}\.tar\.gz$"))
        print(file_info)
        if file_info:
            file_url = folder_url + file_info["href"]
            file_name = file_info.get_text(strip=True)
            version_match = re.match(r'postgresql-(\d+\.\d+(\.\d+)?)\.tar\.gz', file_name)
    
            if version_match:
                version = version_match.group(1)


                # ここにダウンロードとデータベースへの保存処理を追加
                print("Version found:", version)

                if not is_version_downloaded(table_name, version, db_connection):
                    last_modified = row.find_all("td")[1].get_text(strip=True)

                    if last_modified:
                        last_modified_date = datetime.strptime(last_modified, "%Y-%m-%d %H:%M:%S").date()
                        response = requests.get(file_url)
                        file_path = os.path.join(download_dir, f"postgresql-{version}.tar.gz")
                        save_file(response, file_path)

                        if db_connection:
                            data = (version, last_modified_date, file_path)
                            insert_data(db_connection, table_name, data)
                else:
                    print("Version not found for file:", file_url)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
