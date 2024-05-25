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

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            surname VARCHAR(255),
            plan VARCHAR(255),
            last_reset datetime,       
            UNIQUE (username),
            UNIQUE (email),
            FOREIGN KEY (plan) REFERENCES subscription_plan(plan_id)       
        )
    ''')

    # Create subscription_plan table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plan (
            plan_id INT AUTO_INCREMENT PRIMARY KEY,
            plan_name VARCHAR(255) NOT NULL,
            daily_limit INT NOT NULL,
            price DOUBLE       
        )
    ''')

    # Create payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            payment_date date,       
            amount double,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":

    init_db()