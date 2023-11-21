import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from database_utils import connect_to_database, create_table_if_not_exists, insert_data, close_connection
from file_utils import is_version_downloaded, mark_version_as_downloaded, save_file

base_url = "https://archive.apache.org/dist/httpd/"
downloaded_versions_file = "/var/repository/downloaded_versions.txt"
download_dir = "/var/repository/apache/"
table_name = "apache"

# ダウンロード済みのバージョン情報を読み込む
downloaded_versions = set()
if os.path.exists(downloaded_versions_file):
    with open(downloaded_versions_file, "r") as file:
        downloaded_versions = set(file.read().splitlines())

# MySQLデータベースに接続
db_connection = connect_to_database()

# 接続が成功したか確認
if not db_connection:
    print("Error: Failed to connect to the database.")
else:
    # テーブルが存在しなければ作成
    create_table_query = (
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "version VARCHAR(20) NOT NULL, "
        "file_url VARCHAR(255) NOT NULL, "
        "file_path VARCHAR(255) NOT NULL, "
        "last_modified DATETIME NOT NULL"
    )
    create_table_if_not_exists(db_connection, table_name, create_table_query)

    try:
        # HTTP GETリクエストを送り、HTMLを取得
        print("Fetching HTML content...")
        response = requests.get(base_url)
        response.raise_for_status()  # エラーがあれば例外を発生させる
        print("HTML content fetched successfully!")

        # BeautifulSoupを使用してHTMLを解析
        soup = BeautifulSoup(response.content, "html.parser")

        # 正規表現でbeta版をフィルタリング
        beta_regex = re.compile(r'.*beta.*', re.IGNORECASE)

        # aタグからバージョンとLast Modifiedを取得
        for link in soup.find_all("a"):
            href = link.get("href")

            # ファイル名が.tar.gzで終わり、beta版を除外
            if href and href.endswith(".tar.gz") and not beta_regex.match(href):
                # ファイル名からバージョン情報を正規表現で抽出
                version_match = re.match(r'httpd-(\d+\.\d+\.\d+).*', href)
                if version_match:
                    version = version_match.group(1)

                    # ダウンロード済みのバージョンか確認
                    if not is_version_downloaded("httpd", version, downloaded_versions):
                        # ファイルのLast Modifiedを取得
                        # 次の行にあるテキストを取得
                        next_td = link.find_next("td")
                        if next_td:  # Noneでないことを確認
                            last_modified = next_td.find_next("td").text.strip()
                            last_modified_date = datetime.strptime(last_modified, "%Y-%m-%d %H:%M")
        
                            print(f"Downloading Version: {version}, File URL: {base_url + href}, Last Modified: {last_modified_date}")

                            # ファイルをダウンロードし、保存
                            response = requests.get(base_url + href)
                            file_path = os.path.join(download_dir, href)
                            save_file(response, file_path)

                            # データベースに格納
                            if db_connection:
                                data = (None, version, base_url + href, file_path, last_modified_date)
                                insert_data(db_connection, table_name, data)

                            # ダウンロード済みのバージョン情報を追加
                            mark_version_as_downloaded("httpd", version, downloaded_versions, downloaded_versions_file)
                            print(f"Version {version} processed successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # MySQLデータベースとの接続を閉じる
        close_connection(db_connection)
