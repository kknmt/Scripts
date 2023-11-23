# database_utils.py
import mysql.connector

# MySQL接続情報
mysql_host = "localhost"
mysql_user = "admin"
mysql_password = "password"
mysql_database = "repository"

def create_connection():
    """Create a MySQL database connection."""
    return mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )

def insert_data(db_connection, table_name, data):
    cursor = None
    sql = None
    try:
        cursor = db_connection.cursor()
        placeholders = ', '.join(['%s'] * len(data))
        columns = 'version, last_modified, file_path'
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        print("SQL:", sql)
        print("Data:", data)
        cursor.execute(sql, data)
        db_connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
