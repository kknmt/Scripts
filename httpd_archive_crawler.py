import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, mark_version_as_downloaded, save_file
from database_utils import create_connection, create_table, insert_data

# ダウンロード済みのバージョン情報ファイル
downloaded_versions_file = "/var/repository/downloaded_versions.txt"
downloaded_versions = []

# ソフトウェアのベースURL
base_url = "https://archive.apache.org/dist/httpd/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/apache/"

# データベースの設定
db_connection = create_connection()
table_name = "apache"
create_table(db_connection, table_name)

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# 正規表現: beta版を除外
beta_regex = re.compile(r".*beta.*", re.IGNORECASE)

# aタグからバージョンとLast Modifiedを取得
for link in soup.find_all("a"):
    href = link.get("href")

    # ファイル名が.tar.gzで終わり、beta版を除外
    if href and href.endswith(".tar.gz") and not beta_regex.match(href):
        # ファイル名からバージョン情報を正規表現で抽出
        version_match = re.match(r'httpd-(\d+\.\d+\.\d+).*', href)
        if version_match:
            version = version_match.group(1)

            # ファイルがダウンロード済みか確認
            if not is_version_downloaded("httpd", version, downloaded_versions):
                # ファイルのLast Modifiedを取得
                # 直後のテキストを取得
                next_sibling = link.find_next("a").find_next_sibling(string=True)
                if next_sibling:  # Noneでないことを確認
                    # 数字とハイフン、コロン以外の文字を削除
                    last_modified = re.sub(r"[^0-9:-]", "", next_sibling).strip()

                    # デバッグ出力
                    print(f"DEBUG: Last Modified Before: {last_modified}")

                    # 日付部分だけ取得
                    date_part = re.search(r"\d{4}-\d{2}-\d{2}", last_modified)
                    if date_part:
                        date_part = date_part.group()
                    else:
                        print(f"Error: Could not extract date from {last_modified}")
                        continue

                    # デバッグ出力
                    print(f"DEBUG: Date Part: {date_part}")

                    # 日付部分だけ取得
                    last_modified_date = datetime.strptime(date_part, "%Y-%m-%d").date()

                    # デバッグ出力
                    print(f"DEBUG: Last Modified After: {last_modified_date}")

                    print(f"Downloading Version: {version}, File URL: {base_url + href}, Last Modified: {last_modified_date}")

                    # ファイルをダウンロードし、保存
                    response = requests.get(base_url + href)
                    file_path = os.path.join(download_dir, href)
                    save_file(response, file_path)

                    data_dict = {
                        'version': version,
                        'url': base_url + href,
                        'file_path': file_path,
                        'last_modified': last_modified_date
                    }
                    

                    # データベースに格納
                    if db_connection:
                        data = (None, version, base_url + href, file_path, last_modified_date)
                        insert_data(db_connection, table_name, data_dict)

                    # ダウンロード済みのバージョン情報を追加
                    mark_version_as_downloaded("httpd", version, downloaded_versions, downloaded_versions_file)
                    print(f"Version {version} processed successfully!")
                else:
                    print("Error: Could not find Last Modified information.")
            else:
                print(f"Version {version} is already downloaded.")

# データベース接続を閉じる
if db_connection:
    db_connection.close()
