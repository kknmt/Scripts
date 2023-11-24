# file_utils.py
def is_version_downloaded(table_name, version, db_connection):
    cursor = db_connection.cursor()
    try:
        # SQLクエリを実行して該当するバージョンがあるか確認
        cursor.execute("SELECT version FROM {} WHERE version = %s".format(table_name), (version,))
        result = cursor.fetchone()

        return result is not None  # バージョンが見つかればTrue、見つからなければFalseを返す

    except Exception as e:
        print("Error checking if version is downloaded:", e)
        return False

    finally:
        try:
            cursor.fetchall()  # 未読の結果を読み取る
        except mysql.connector.errors.InternalError as e:
            pass  # すでに読み取り済みの場合はスキップ
        cursor.close()

def save_file(response, file_path):
    """Save the downloaded file."""
    with open(file_path, 'wb') as file:
        file.write(response.content)
