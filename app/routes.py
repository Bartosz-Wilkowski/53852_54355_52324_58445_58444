from flask import render_template, request, jsonify, redirect, url_for, session
from .database import create_connection
from mysql.connector import Error, errorcode
import bcrypt

def home():
    return render_template('index.html')
    
def login_form():
    return render_template('login.html')

def registration_form():
    return render_template('register.html')

def login():
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

def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data['username']
        name = data['name'] 
        surname = data['surname']
        email = data['email']
        password = data['password']
        
        connection = create_connection()
        if connection is None:
            return jsonify({"message": "Failed to connect to the database."}), 500

        cursor = connection.cursor()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO users (username, email, password, name, surname, plan) VALUES (%s, %s, %s, %s, %s, %s)",
                           (username, email, hashed_password, name, surname, 'Basic'))
            connection.commit()
            return redirect(url_for('login_form'))
        except Error as e:
            if e.errno == errorcode.ER_DUP_ENTRY: 
                return jsonify({"message": "Username or email already exists."}), 409
            else:
                return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

def userprofile():
    if 'username' in session:
        return render_template('userprofile.html')
    else:
        return redirect(url_for('login_form'))

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
        
def purchase_form():
    if 'username' in session:
        return render_template('purchase.html')
    else:
        return redirect(url_for('login_form'))
    
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