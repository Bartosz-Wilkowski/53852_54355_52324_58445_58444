from flask import render_template, request, jsonify, redirect, url_for, session
from .database import create_connection
from mysql.connector import Error, errorcode
import bcrypt
import re



# renders the home page of the website
def home():
    return render_template('index.html', logged_in=is_logged_in())


def is_logged_in():
    return 'username' in session


# function for logout
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


# function tests the database connection, prints a success message if connected, or an error message if it fails to connect.
def test_connection():
    try:
        connection = create_connection()
        if connection and connection.is_connected():
            print("Connected to the database.")
        else:
            print("Failed to connect to the database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

test_connection()


# function handles user login. It retrieves user credentials, verifies them, and sets a session if successful.
# Returns appropriate JSON responses for success, invalid credentials, and errors.
def login():
    if is_logged_in():
        return redirect('/')

    if request.method == 'GET':
        return render_template('login.html', logged_in=is_logged_in())
    
    elif request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()

            # Validate username and password
            if not username or not password:
                return jsonify({"message": "Both username and password are required."}), 400
            if len(password) < 8:
                return jsonify({"message": "Password must be at least 8 characters long."}), 400

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
        except Exception as e:
            return jsonify({'message': str(e)}), 400


# function handles user registration. Renders the registration form for GET requests and processes the form data for POST requests.
# Inserts new user data into the database, hashes passwords, and handles errors, including duplicate entries.
def register():
    if is_logged_in():
        return redirect('/')

    if request.method == 'GET':
        return render_template('register.html', logged_in=is_logged_in())
    
    elif request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            name = data.get('name', '').strip()
            surname = data.get('surname', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()

            # Validate input
            if not all([username, name, surname, email, password]):
                return jsonify({"message": "All fields are required."}), 400
            if len(password) < 8:
                return jsonify({"message": "Password must be at least 8 characters long."}), 400

            email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            if not email_pattern.match(email):
                return jsonify({"message": "Invalid email format."}), 400

            connection = create_connection()
            if connection is None:
                return jsonify({"message": "Failed to connect to the database."}), 500

            cursor = connection.cursor()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            try:
                cursor.execute(
                    "INSERT INTO users (username, email, password, name, surname) VALUES (%s, %s, %s, %s, %s)",
                    (username, email, hashed_password.decode('utf-8'), name, surname)
                )
                connection.commit()
                return jsonify({"message": "Registration successful! Please log in."})
            except Error as e:
                print(f"Error during user registration: {e}")
                if e.errno == errorcode.ER_DUP_ENTRY:
                    return jsonify({"message": "Username or email already exists."}), 409
                else:
                    return jsonify({"message": str(e)}), 500
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"Exception during registration: {e}")
            return jsonify({"message": str(e)}), 500
        
        
# function serves the user profile page. It checks if the user is logged in by verifying the session.
# Redirects to the login page if the user is not logged in.
def userprofile():
    if 'username' in session:
        return render_template('userprofile.html', logged_in=is_logged_in())
    else:
        return redirect(url_for('login'))


# function retrieves user data from the database. Checks if the user is logged in, fetches user details from the database, and returns them as JSON.
# Handles errors and returns appropriate status codes.
def get_user_data():
    if 'username' not in session:
        return jsonify({"message": "User not logged in."}), 401

    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Failed to connect to the database."}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s",
                       (session['username'],))
        user_data = cursor.fetchone()
        if user_data:
            return jsonify(user_data)
        else:
            return jsonify({"message": "User not found."}), 404
    except Error as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# function serves the purchase form page.
def purchase_form():
    if 'username' in session:
        return render_template('purchase.html', logged_in=is_logged_in())
    else:
        return redirect(url_for('login'))


# function processes plan purchases. It verifies if the user is logged in, processes the payment details, and updates the user's plan in the database.
# Returns success or error messages as JSON responses, and assumes payment processing is successful for this example.
def purchase_plan():
    if 'username' not in session:
        return jsonify({"message": "User not logged in."}), 401

    data = request.get_json()

    plan = data.get('newplan', '').strip()
    card_number = data.get('cardNumber', '').strip()
    card_name = data.get('cardName', '').strip()
    expiry_date = data.get('expiryDate', '').strip()
    cvc = data.get('cvc', '').strip()
    amount = 10.0 

    # Validate input fields
    if not all([plan, card_number, card_name, expiry_date, cvc]):
        return jsonify({"message": "All fields are required."}), 400

    if len(card_number) != 16 or not card_number.isdigit():
        return jsonify({"message": "Invalid card number. It should be 16 digits."}), 400

    if not all(c.isalpha() or c.isspace() for c in card_name):
        return jsonify({"message": "Card name should only contain letters and spaces."}), 400

    if not re.match(r'^(0[1-9]|1[0-2])\/?([0-9]{2})$', expiry_date):
        return jsonify({"message": "Invalid expiry date format. Use MM/YY."}), 400

    if not re.match(r'^[0-9]{3,4}$', cvc):
        return jsonify({"message": "Invalid CVC. It should be 3 or 4 digits."}), 400

    # Add payment logic (assuming payment is successful for this example)
    
    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Failed to connect to the database."}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
        user_id = cursor.fetchone()
        if user_id is None:
            return jsonify({"message": "User not found."}), 404
        user_id = user_id[0]

        cursor.execute("UPDATE users SET plan = %s WHERE username = %s", (plan, session['username']))
        connection.commit()

        cursor.execute(
            "INSERT INTO payments (user_id, payment_date, amount) VALUES (%s, CURDATE(), %s)",
            (user_id, amount)
        )
        connection.commit()

        return jsonify({"message": "Plan purchased and payment recorded successfully!"})
    except Error as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def interpreter():
    return render_template('sli.html')

