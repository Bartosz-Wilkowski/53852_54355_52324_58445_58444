from flask import render_template, request, jsonify, redirect, url_for, session
from .database import create_connection
from mysql.connector import Error, errorcode
import bcrypt

#renders the home page of the website
def home():
    return render_template('index.html', logged_in=is_logged_in())
    
def is_logged_in():
    return 'username' in session

# Funkcja wylogowująca użytkownika
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

#function tests the database connection, prints a success message if connected, or an error message if it fails to connect.
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

#function handles user login. It retrieves user credentials, verifies them, and sets a session if successful.
#Returns appropriate JSON responses for success, invalid credentials, and errors.
def login():
    if request.method == 'GET':
        return render_template('login.html', logged_in=is_logged_in())
    elif request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
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
        except Exception as e:
            return jsonify({'message': str(e)}), 400


#function handles user registration. Renders the registration form for GET requests and processes the form data for POST requests.
#Inserts new user data into the database, hashes passwords, and handles errors, including duplicate entries.
def register():
    if request.method == 'GET':
        return render_template('register.html', logged_in=is_logged_in())
    elif request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = data['username']
            name = data['name']
            surname = data['surname']
            email = data['email']
            password = data['password']
            
            connection = create_connection()
            if connection is None:
                print("Failed to connect to the database.")
                return jsonify({"message": "Failed to connect to the database."}), 500

            cursor = connection.cursor()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            try:
                cursor.execute("INSERT INTO users (username, email, password, name, surname, plan) VALUES (%s, %s, %s, %s, %s, %s)",
                               (username, email, hashed_password.decode('utf-8'), name, surname, 'Basic'))
                connection.commit()
                return redirect(url_for('login'))
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
        
#function serves the user profile page. It checks if the user is logged in by verifying the session.
#Redirects to the login page if the user is not logged in.
def userprofile():
    if 'username' in session:
        return render_template('userprofile.html', logged_in=is_logged_in())
    else:
        return redirect(url_for('login'))

#function retrieves user data from the database. Checks if the user is logged in, fetches user details from the database, and returns them as JSON.
#Handles errors and returns appropriate status codes.
def get_user_data():
    if 'username' not in session:
        return jsonify({"message": "User not logged in."}), 401

    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Failed to connect to the database."}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (session['username'],))
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
        
#function serves the purchase form page.        
def purchase_form():
    if 'username' in session:
        return render_template('purchase.html', logged_in=is_logged_in())
    else:
        return redirect(url_for('login'))

#function processes plan purchases. It verifies if the user is logged in, processes the payment details, and updates the user's plan in the database.
#Returns success or error messages as JSON responses, and assumes payment processing is successful for this example.    
def purchase_plan():
    if 'username' not in session:
        return jsonify({"message": "User not logged in."}), 401

    data = request.get_json()
    plan = data['newplan']
    card_number = data['cardNumber']
    card_name = data['cardName']
    expiry_date = data['expiryDate']
    cvc = data['cvc']

    # Add logic to process the payment here
    # For the sake of example, we assume payment is always successful

    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Failed to connect to the database."}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE users SET plan = %s WHERE username = %s", (plan, session['username']))
        connection.commit()
        return jsonify({"message": "Plan purchased successfully!"})
    except Error as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()