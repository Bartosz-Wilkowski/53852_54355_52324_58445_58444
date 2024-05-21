from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'


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


@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login_form'))


@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data is None:
        data = request.form
    username = data['username']
    password = data['password']

    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Failed to connect to the database."}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            session['username'] = username
            return jsonify({'message': f'Welcome, {username}!'})
        else:
            return jsonify({'message': 'Invalid username or password!'}), 401
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        data = request.get_json()
        if data is None:
            data = request.form
        username = data['username']
        email = data['email']
        password = data['password']
        name = data.get('name', 'defaultName')  # Add proper input fields for name in HTML and get their values
        surname = data.get('surname', 'defaultSurname')

        connection = create_connection()
        if connection is None:
            return jsonify({"message": "Failed to connect to the database."}), 500

        cursor = connection.cursor()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO users (username, email, password, name, surname) VALUES (%s, %s, %s, %s, %s)",
                           (username, email, hashed_password, name, surname))
            connection.commit()
            return redirect(url_for('login_form'))
        except Error as e:
            if e.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                return jsonify({"message": "Username or email already exists."}), 409
            else:
                return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()


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
                      UNIQUE (username),
                      UNIQUE (email))''')
    connection.commit()
    cursor.close()
    connection.close()


init_db()

if __name__ == '__main__':
    app.run(debug=True)
