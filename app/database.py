import mysql.connector
from mysql.connector import Error

# Remember to change the 'database' and 'password' fields to the appropriate values.
# Function to create a database connection


def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='AEHprojekt'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS user_auth")
            cursor.close()
            connection.close()

        connection = mysql.connector.connect(
            host='localhost',
            database='user_auth',
            user='root',
            password='AEHprojekt'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def init_db():
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INT AUTO_INCREMENT PRIMARY KEY,
                      username VARCHAR(255) NOT NULL,
                      email VARCHAR(255) NOT NULL,
                      password VARCHAR(255) NOT NULL,
                      name VARCHAR(255),
                      surname VARCHAR(255),
                      plan VARCHAR(255),
                      UNIQUE (username),
                      UNIQUE (email))''')
    connection.commit()
    cursor.close()
    connection.close()
