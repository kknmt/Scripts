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

def create_table(connection, table_name):
    """Create a table in the MySQL database if it doesn't exist."""
    cursor = connection.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            version VARCHAR(255) NOT NULL,
            url TEXT NOT NULL,
            file_path TEXT NOT NULL,
            last_modified DATE NOT NULL
        );
    """)
    connection.commit()

def insert_data(db_connection, table_name, data_dict):
    try:
        cursor = db_connection.cursor()
        placeholders = ', '.join(['%s'] * len(data_dict))
        columns = ', '.join(data_dict.keys())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        cursor.execute(sql, tuple(data_dict.values()))
        db_connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
