# wordpress_crawler.py
import os
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from file_utils import is_version_downloaded, mark_version_as_downloaded, save_file
from database_utils import create_connection, insert_data

# ダウンロード済みのバージョン情報ファイル
downloaded_versions_file = "/var/repository/downloaded_versions.txt"
downloaded_versions = []

# WordPress REST APIのベースURL
rest_api_url = "https://api.wordpress.org/core/version-check/1.7/"

# ダウンロード先ディレクトリ
download_dir = "/var/repository/wordpress/"

# データベースの設定
db_connection = create_connection()
table_name = "wordpress"

# 最新バージョンの情報を取得
response_latest = requests.get(rest_api_url)
latest_data = response_latest.json()
latest_version = latest_data["offers"][0]["version"]

# 各バージョンの情報を取得
for version_info in latest_data["offers"]:
    version = version_info["version"]
    tar_gz_url = version_info["download"]

    # ファイルがダウンロード済みか確認
    if not is_version_downloaded("wordpress", version, downloaded_versions):
        # ファイルをダウンロードし、保存
        response_tar_gz = requests.get(tar_gz_url)
        file_name_tar_gz = f"wordpress-{version}.tar.gz"
        file_path_tar_gz = os.path.join(download_dir, file_name_tar_gz)
        save_file(response_tar_gz, file_path_tar_gz)

        # データベースに格納
        if db_connection:
            # WordPress REST APIではリリース日時の情報が提供されていないため、現在の日時を使用します。
            current_date = datetime.now().date()
            data = (version, current_date, file_path_tar_gz)
            insert_data(db_connection, table_name, data)

        # ダウンロード済みのバージョン情報を追加
        mark_version_as_downloaded("wordpress", version, downloaded_versions, downloaded_versions_file)

# データベース接続を閉じる
if db_connection:
    db_connection.close()
