import mysql.connector
from mysql.connector import errorcode

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='repo_user',
            password='your_password',
            database='repository'
        )
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Access denied.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist.")
        else:
            print(f"Error: {err}")
        return None

def create_table_if_not_exists(connection, table_name, columns):
    cursor = connection.cursor()
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()

def insert_data(connection, table_name, data):
    cursor = connection.cursor()
    placeholders = ', '.join(['%s'] * len(data))
    insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    cursor.execute(insert_query, data)
    connection.commit()
    cursor.close()

def close_connection(connection):
    connection.close()
