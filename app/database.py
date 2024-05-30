import mysql.connector
from mysql.connector import Error
from datetime import datetime

def create_connection():
    """
    Function to create a database connection.
    Returns:
        connection: MySQL database connection object.
    """
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
    """
    Initialize the MySQL database by creating necessary tables.
    """
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    cursor = connection.cursor()
    
    # Create subscription_plan table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plan (
            plan_id INT AUTO_INCREMENT PRIMARY KEY,
            plan_name VARCHAR(255) NOT NULL,
            daily_limit INT,
            price DOUBLE,
            UNIQUE (plan_name)   
        )
    ''')
    
    # Insert three plans into subscription_plan table using INSERT IGNORE
    cursor.execute('''
        INSERT IGNORE INTO subscription_plan (plan_name, daily_limit, price) VALUES
        ('Basic', 25, 0),
        ('Standard', 250, 19.99),
        ('Unlimited', NULL, 49.99)
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            surname VARCHAR(255),
            plan_name VARCHAR(255),
            recognized_count INT,       
            last_reset datetime,
            UNIQUE (username),
            UNIQUE (email),
            reset_token VARCHAR(255),
            FOREIGN KEY (plan_name) REFERENCES subscription_plan(plan_name)
        )
    ''')
    
    # Insert aehuser user into users table using INSERT IGNORE
    cursor.execute('''
        INSERT IGNORE INTO users (username, email, password, name, surname, plan_name) VALUES
        ('aehuser', 'aehuser@aeh.pl', 'Aehuser1', 'Aeh', 'User', 'Unlimited')
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

def revoke_drop_privileges():
    """
    Revoke DROP privileges from specific users in the database.
    """
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT GROUP_CONCAT(CONCAT('REVOKE DROP ON `user_auth`.* FROM `', user, '`@`', host, '`;') SEPARATOR ' ')
            INTO @sql
            FROM mysql.db
            WHERE db = 'user_auth' AND user != 'root' AND user != 'mysql.sys';
        ''')
        
        cursor.execute("SET @sql = IFNULL(@sql, '');")
        cursor.execute('PREPARE stmt FROM @sql;')
        cursor.execute('EXECUTE stmt;')
        cursor.execute('DEALLOCATE PREPARE stmt;')
        print("DROP privileges revoked successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def reset_recognized_count():
    """
    Reset recognized count and last reset for Basic and Standard plans in the database.
    """
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    cursor = connection.cursor()
    try:
        now = datetime.now()
        midnight = datetime.combine(now.date(), datetime.min.time())
        cursor.execute('''
            UPDATE users
            SET recognized_count = 0, last_reset = %s
            WHERE plan_name IN ('Basic', 'Standard') AND (last_reset IS NULL OR last_reset < %s)
        ''', (midnight, midnight))
        connection.commit()
        print("recognized_count reset and last_reset updated successfully for Basic and Standard plans.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    init_db()
    revoke_drop_privileges()
    reset_recognized_count()