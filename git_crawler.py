# github_crawler.py
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from file_utils import save_file
from database_utils import create_connection, insert_data

# ソフトウェアのベースURL
base_url = "https://github.com/git/git/tags"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/git/"

# データベースの設定
db_connection = create_connection()
table_name = "git"

# HTMLを取得
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# タグ情報からバージョンとリリース日を取得
for tag_item in soup.find_all("h2", class_="f4 d-inline"):
    tag_link = tag_item.find("a")
    if tag_link:
        tag_name = tag_link.text.strip()

        # タグ名がバージョン番号の形式であることを確認
        version_match = re.match(r'v(\d+\.\d+\.\d+)', tag_name)
        if version_match:
            version = version_match.group(1)

            # ダウンロード済みのバージョンか確認
            if not os.path.exists(os.path.join(download_dir, f"git-{version}.tar.gz")):
                # バージョンの詳細ページにアクセスし、リリース日を取得
                release_url = f"https://github.com/git/git/releases/tag/{tag_name}"
                release_response = requests.get(release_url)
                release_soup = BeautifulSoup(release_response.text, "html.parser")

                # リリース日はHTML内の特定の要素から取得
                release_date_element = release_soup.find("relative-time")
                if release_date_element:
                    last_modified_str = release_date_element["datetime"]
                    last_modified_date = datetime.strptime(last_modified_str, "%Y-%m-%dT%H:%M:%SZ").date()

                    # ファイルをダウンロードし、保存
                    file_url = f"https://github.com/git/git/archive/{tag_name}.tar.gz"
                    file_response = requests.get(file_url)
                    file_path = os.path.join(download_dir, f"git-{version}.tar.gz")
                    save_file(file_response, file_path)

                    # データベースに格納
                    if db_connection:
                        data = (version, last_modified_date, file_path)
                        insert_data(db_connection, table_name, data)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
