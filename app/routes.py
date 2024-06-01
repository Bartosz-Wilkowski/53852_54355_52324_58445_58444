"""
Module: user_authentication

This module handles user authentication and related functionalities.

Classes:
    - UserDataManagement: Manages user data operations.
        - get_user_data(): Retrieves user data from the database.
        - delete_account(): Deletes the user account.

    - PlansManagement: Manages subscription plans.
        - get_plans(): Retrieves subscription plans.
        - get_plan_price(plan_name): Retrieves the price of a specific plan.
        - format_price(price): Splits price into dollars and cents.
        - pricing(): Retrieves subscription plans from the database and formats prices.

    - PaymentManagement: Manages payment operations.
        - purchase_plan(): Processes plan purchases.
        - purchase_form(): Serves the purchase form page.

    - PasswordManagement: Manages password reset operations.
        - reset_password(): Handles password reset request.
        - generate_reset_token(): Generates a password reset token.
        - reset_with_token(token): Handles password reset form submission.
        - send_reset_email(to_email, token): Sends a password reset email.
        - reset_password_link(): Generates a password reset link.

    - Authentication: Manages user authentication.
        - home(): Renders the home page of the website.
        - interpreter(): Renders the SLI (Sign Language Interpreter) page.
        - login(): Handles user login.
        - register(): Handles user registration.
        - userprofile(): Serves the user profile page.
        - is_logged_in(): Checks if a user is logged in.
        - logout(): Logs out the user.
        - test_connection(): Tests the database connection.

Dependencies:
    - Flask
    - flask_mail
    - bcrypt
    - re
    - uuid
    - smtplib
    - email.mime
"""

from flask import render_template, request, jsonify, redirect, url_for, session, flash
from .database import create_connection
from mysql.connector import Error, errorcode
import bcrypt
import re
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class UserDataManagement:
    """
    Class to manage user data operations.
    """
    @staticmethod
    def get_user_data():
        """
        Retrieves user data from the database.

        Returns:
            JSON response: User data including payment history if the user is logged in and found in the database,
            otherwise returns an error message with appropriate status code.
        """
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
                cursor.execute("SELECT payment_date, amount FROM payments WHERE user_id = %s", (user_data['id'],))
                payment_history = cursor.fetchall()
                if payment_history:
                    user_data['payment_history'] = payment_history
                else:
                    user_data['payment_history'] = []
                return jsonify(user_data)
            else:
                return jsonify({"message": "User not found."}), 404
        except Error as e:
            return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def delete_account():
        """
        Deletes the user account along with related payment records.
        Also logs out the user and deletes session data.

        Returns:
            Response: JSON response indicating success, errors, and redirection.
        """
        if 'username' not in session:
            print("User not logged in.")
            return jsonify({"message": "User not logged in."}), 401

        connection = create_connection()
        if connection is None:
            print("Failed to connect to the database.")
            return jsonify({"message": "Failed to connect to the database."}), 500

        cursor = connection.cursor()
        try:
            # Fetch user ID based on session username
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user_id = cursor.fetchone()
            if not user_id:
                print("User not found.")
                return jsonify({"message": "User not found."}), 404

            user_id = user_id[0]

            # Delete related records in payments table
            cursor.execute("DELETE FROM payments WHERE user_id = %s", (user_id,))
            connection.commit()

            # Delete user from the users table
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()

            # Logout user and delete session data
            session.pop('username', None)
            print("Account deleted successfully.")
            return jsonify({"message": "Account deleted successfully.", "redirect": url_for('home')})
        except Error as e:
            print(f"Error deleting account: {e}")
            return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

class PlansManagement:
    """
    Class to manage subscription plans.
    """
    @staticmethod
    def get_plans():
        """
        Retrieves subscription plans.

        Returns:
            JSON response: A list of dictionaries containing plan names and prices if successful,
            otherwise returns an error message with appropriate status code.
        """
        connection = create_connection()
        if connection is None:
            return jsonify({"message": "Failed to connect to the database."}), 500

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute('SELECT plan_name, price FROM subscription_plan')
            plans = cursor.fetchall()
            return jsonify(plans)
        except Error as e:
            return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_plan_price(plan_name):
        """
        Retrieves the price of a specific plan.

        Args:
            plan_name (str): The name of the plan for which the price is to be retrieved.

        Returns:
            JSON response: The price of the plan if found, otherwise returns an error message with appropriate status code.
        """
        connection = create_connection()
        if connection is None:
            return jsonify({"message": "Failed to connect to the database."}), 500

        cursor = connection.cursor()
        try:
            cursor.execute('SELECT price FROM subscription_plan WHERE plan_name = %s', (plan_name,))
            price = cursor.fetchone()
            if price:
                return jsonify(price[0])
            else:
                return jsonify({"message": "Price not found for the plan."}), 404
        except Error as e:
            return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def format_price(price):
        """
        Split price into dollars and cents.

        Args:
            price (float): The price to be formatted.

        Returns:
            tuple: A tuple containing the dollars and cents.
        """
        dollars = int(price)
        cents = int(round((price - dollars) * 100))
        return dollars, cents

    @staticmethod
    def pricing():
        """
        Retrieves subscription plans from the database and formats prices.
        Renders the pricing page template with the plans and logged-in status.

        Returns:
            Response: The pricing page template with plans and logged-in status.
        """
        connection = create_connection()
        if connection is None:
            return "Failed to connect to the database.", 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM subscription_plan')
        plans = cursor.fetchall()

        for plan in plans:
            dollars, cents = PlansManagement.format_price(plan['price'])
            plan['dollars'] = dollars
            plan['cents'] = f'{cents:02d}'

        cursor.close()
        connection.close()

        return render_template('pricing.html', plans=plans, logged_in=Authentication.is_logged_in())

class PaymentManagement:
    """
    Class to manage payment operations.
    """
    @staticmethod
    def purchase_plan():
        """
        Processes plan purchases. It verifies if the user is logged in, processes the payment details, 
        and updates the user's plan in the database.

        Returns:
            JSON response: Success message if the purchase is successful, or error message with appropriate status code.

        Note:
            This function assumes payment processing is successful for this example.
        """
        if 'username' not in session:
            return jsonify({"message": "User not logged in."}), 401

        data = request.get_json()

        plan_name = data.get('newplan', '').strip()[:255]  # Limiting to 255 characters
        card_number = data.get('cardNumber', '').strip()[:255]  # Limiting to 255 characters
        card_name = data.get('cardName', '').strip()[:255]  # Limiting to 255 characters
        expiry_date = data.get('expiryDate', '').strip()[:255]  # Limiting to 255 characters
        cvc = data.get('cvc', '').strip()[:255]  # Limiting to 255 characters

        # Check if any field exceeds 255 characters
        if len(plan_name) > 255 or len(card_number) > 255 or len(card_name) > 255 or len(expiry_date) > 255 or len(cvc) > 255:
            return jsonify({"message": "One or more fields exceed the maximum character limit of 255."}), 400
        
        connection = create_connection()
        if connection is None:
            return jsonify({"message": "Failed to connect to the database."}), 500

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user_id = cursor.fetchone()['id']

            # Fetch the plan price
            cursor.execute("SELECT price FROM subscription_plan WHERE plan_name = %s", (plan_name,))
            plan = cursor.fetchone()
            if not plan:
                return jsonify({"message": "Invalid plan selected."}), 400
            plan_price = plan['price']

            # Insert payment record
            cursor.execute(
                "INSERT INTO payments (user_id, plan_name, amount, card_number, card_name, expiry_date, cvc, payment_date) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())",
                (user_id, plan_name, plan_price, card_number, card_name, expiry_date, cvc)
            )
            connection.commit()

            # Update user's subscription plan
            cursor.execute("UPDATE users SET subscription_plan = %s WHERE id = %s", (plan_name, user_id))
            connection.commit()

            return jsonify({"message": "Plan purchased successfully."})
        except Error as e:
            return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def purchase_form():
        """
        Serves the purchase form page. It retrieves subscription plans from the database
        and renders the purchase form template.

        Returns:
            Response: The purchase form template with plans and logged-in status.
        """
        connection = create_connection()
        if connection is None:
            return "Failed to connect to the database.", 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT plan_name FROM subscription_plan')
        plans = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template('purchase.html', plans=plans, logged_in=Authentication.is_logged_in())

class PasswordManagement:
    """
    Class to manage password reset operations.
    """
    @staticmethod
    def reset_password():
        """
        Handles password reset request. It sends a reset token to the user's email if the user exists.

        Returns:
            JSON response: Success message if the email is sent, otherwise error message with appropriate status code.
        """
        data = request.get_json()
        email = data.get('email', '').strip()[:255]  # Limiting to 255 characters

        # Check if email field exceeds 255 characters
        if len(email) > 255:
            return jsonify({"message": "Email exceeds the maximum character limit of 255."}), 400

        connection = create_connection()
        if connection is None:
            return jsonify({"message": "Failed to connect to the database."}), 500

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                return jsonify({"message": "User not found."}), 404

            token = PasswordManagement.generate_reset_token()

            cursor.execute("UPDATE users SET reset_token = %s WHERE email = %s", (token, email))
            connection.commit()

            PasswordManagement.send_reset_email(email, token)

            return jsonify({"message": "Password reset email sent."})
        except Error as e:
            return jsonify({"message": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def generate_reset_token():
        """
        Generates a unique password reset token.

        Returns:
            str: A unique reset token.
        """
        return str(uuid.uuid4())

    @staticmethod
    def reset_with_token(token):
        """
        Handles password reset form submission using a token.

        Args:
            token (str): The password reset token.

        Returns:
            Response: Renders the reset password form template.
        """
        if request.method == 'POST':
            data = request.form
            password = data.get('password', '').strip()
            confirm_password = data.get('confirm_password', '').strip()

            if password != confirm_password:
                flash('Passwords do not match.')
                return redirect(request.url)

            if len(password) > 255 or len(confirm_password) > 255:
                flash('Password exceeds the maximum character limit of 255.')
                return redirect(request.url)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            connection = create_connection()
            if connection is None:
                flash('Failed to connect to the database.')
                return redirect(request.url)

            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM users WHERE reset_token = %s", (token,))
                user = cursor.fetchone()

                if not user:
                    flash('Invalid or expired reset token.')
                    return redirect(request.url)

                cursor.execute("UPDATE users SET password = %s, reset_token = NULL WHERE reset_token = %s",
                               (hashed_password, token))
                connection.commit()

                flash('Password reset successful.')
                return redirect(url_for('login'))
            except Error as e:
                flash(f"Error: {str(e)}")
                return redirect(request.url)
            finally:
                cursor.close()
                connection.close()

        return render_template('reset_password.html', token=token)

    @staticmethod
    def send_reset_email(to_email, token):
        """
        Sends a password reset email to the specified address.

        Args:
            to_email (str): The recipient's email address.
            token (str): The password reset token.
        """
        msg = MIMEMultipart()
        msg['From'] = 'youremail@example.com'
        msg['To'] = to_email
        msg['Subject'] = 'Password Reset Request'
        link = url_for('reset_with_token', token=token, _external=True)
        body = f'Click the following link to reset your password: {link}'
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.example.com', 587)
            server.starttls()
            server.login('youremail@example.com', 'yourpassword')
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Error sending email: {e}")

    @staticmethod
    def reset_password_link():
        """
        Generates a password reset link form.

        Returns:
            Response: The password reset link form template.
        """
        return render_template('reset_password_link.html')

class Authentication:
    """
    Class to manage user authentication.
    """
    @staticmethod
    def home():
        """
        Renders the home page of the website.

        Returns:
            Response: The home page template with logged-in status.
        """
        return render_template('home.html', logged_in=Authentication.is_logged_in())

    @staticmethod
    def interpreter():
        """
        Renders the SLI (Sign Language Interpreter) page.

        Returns:
            Response: The SLI page template with logged-in status.
        """
        return render_template('interpreter.html', logged_in=Authentication.is_logged_in())

    @staticmethod
    def login():
        """
        Handles user login. It verifies the provided credentials and logs in the user if successful.

        Returns:
            Response: The login page template, or redirects to the user profile page on successful login.
        """
        if request.method == 'POST':
            username = request.form['username'].strip()[:255]  # Limiting to 255 characters
            password = request.form['password'].strip()[:255]  # Limiting to 255 characters

            if len(username) > 255 or len(password) > 255:
                flash('Username or password exceeds the maximum character limit of 255.')
                return render_template('login.html', logged_in=Authentication.is_logged_in())

            connection = create_connection()
            if connection is None:
                flash('Failed to connect to the database.')
                return render_template('login.html', logged_in=Authentication.is_logged_in())

            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    session['username'] = username
                    return redirect(url_for('userprofile'))
                else:
                    flash('Invalid username or password.')
            except Error as e:
                flash(f"Error: {str(e)}")
            finally:
                cursor.close()
                connection.close()

        return render_template('login.html', logged_in=Authentication.is_logged_in())

    @staticmethod
    def register():
        """
        Handles user registration. It creates a new user account with the provided details.

        Returns:
            Response: The registration page template, or redirects to the login page on successful registration.
        """
        if request.method == 'POST':
            username = request.form['username'].strip()[:255]  # Limiting to 255 characters
            password = request.form['password'].strip()[:255]  # Limiting to 255 characters
            email = request.form['email'].strip()[:255]  # Limiting to 255 characters

            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                flash('Invalid email format.')
                return render_template('register.html', logged_in=Authentication.is_logged_in())

            if len(username) > 255 or len(password) > 255 or len(email) > 255:
                flash('Input exceeds the maximum character limit of 255.')
                return render_template('register.html', logged_in=Authentication.is_logged_in())

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            connection = create_connection()
            if connection is None:
                flash('Failed to connect to the database.')
                return render_template('register.html', logged_in=Authentication.is_logged_in())

            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash('Username or email already exists.')
                else:
                    cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                                   (username, hashed_password, email))
                    connection.commit()
                    flash('Registration successful. Please log in.')
                    return redirect(url_for('login'))
            except Error as e:
                flash(f"Error: {str(e)}")
            finally:
                cursor.close()
                connection.close()

        return render_template('register.html', logged_in=Authentication.is_logged_in())

    @staticmethod
    def user_profile():
        """
        Renders the user profile page if the user is logged in.

        Returns:
            Response: The user profile page template, or redirects to the login page if not logged in.
        """
        if 'username' not in session:
            return redirect(url_for('login'))

        username = session['username']

        connection = create_connection()
        if connection is None:
            flash('Failed to connect to the database.')
            return redirect(url_for('login'))

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        except Error as e:
            flash(f"Error: {str(e)}")
            user = None
        finally:
            cursor.close()
            connection.close()

        return render_template('user_profile.html', user=user, logged_in=Authentication.is_logged_in())

    @staticmethod
    def logout():
        """
        Logs out the current user by clearing the session.

        Returns:
            Response: Redirects to the home page after logging out.
        """
        session.clear()
        return redirect(url_for('home'))

    @staticmethod
    def is_logged_in():
        """
        Checks if a user is currently logged in.

        Returns:
            bool: True if a user is logged in, False otherwise.
        """
        return 'username' in session

@app.route('/purchase', methods=['GET'])
def purchase_form():
    """
    Route for displaying the purchase form.
    """
    return SubscriptionPlan.purchase_form()

@app.route('/purchase', methods=['POST'])
def purchase_plan():
    """
    Route for handling the plan purchase.
    """
    return SubscriptionPlan.purchase_plan()

@app.route('/reset_password', methods=['POST'])
def reset_password():
    """
    Route for handling password reset requests.
    """
    return PasswordManagement.reset_password()

@app.route('/reset_password_link')
def reset_password_link():
    """
    Route for displaying the password reset link form.
    """
    return PasswordManagement.reset_password_link()

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    """
    Route for handling password reset with a token.
    """
    return PasswordManagement.reset_with_token(token)

@app.route('/')
def home():
    """
    Route for the home page.
    """
    return Authentication.home()

@app.route('/interpreter')
def interpreter():
    """
    Route for the SLI page.
    """
    return Authentication.interpreter()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for handling user login.
    """
    return Authentication.login()

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for handling user registration.
    """
    return Authentication.register()

@app.route('/userprofile')
def user_profile():
    """
    Route for displaying the user profile.
    """
    return Authentication.user_profile()

@app.route('/logout')
def logout():
    """
    Route for logging out the user.
    """
    return Authentication.logout()

# Run the application
if __name__ == '__main__':
    app.secret_key = 'your_secret_key'  # Set a secret key for the session
    app.run(debug=True)  # Run the application in debug mode
