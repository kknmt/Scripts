# subversion_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://archive.apache.org/dist/subversion/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/subversion/"

# データベースの設定
db_connection = create_connection()
table_name = "subversion"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# タグからファイル情報を取得
for tag in soup.find_all(["img", "a"]):
    if tag.name == "a" and tag.get("href") and tag.get("href").endswith(".tar.gz"):
        href = tag.get("href")

        # ファイル名からバージョン情報を正規表現で抽出
        version_match = re.match(r'subversion-(\d+\.\d+(\.\d+)*).*', href)
        if version_match:
            version = version_match.group(1)

            # rc版やalpha版を除外
            if not any(keyword in version for keyword in ["-rc", "-alpha", "-beta"]):
                if not is_version_downloaded(table_name, version, db_connection):
                    # 直前のテキストを取得（親の直前にあるimgタグ）
                    prev_sibling = tag.find_previous_sibling("img")
                    if prev_sibling:
                        # 数字とハイフン、コロン以外の文字を削除
                        last_modified = re.sub(r"[^0-9:-]", "", prev_sibling.find_previous_sibling(string=True)).strip()

                        # 日付部分だけ取得
                        date_part = re.search(r"\d{4}-\d{2}-\d{2}", last_modified)
                        if date_part:
                            date_part = date_part.group()
                        else:
                            continue

                        # 日付部分だけ取得
                        last_modified_date = datetime.strptime(date_part, "%Y-%m-%d").date()

                        # ファイルをダウンロードし、保存
                        response = requests.get(base_url + href)
                        file_path = os.path.join(download_dir, href)
                        save_file(response, file_path)

                        # データベースに格納
                        if db_connection:
                            data = (version, last_modified_date, file_path)
                            insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
