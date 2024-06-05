from unittest.mock import patch, MagicMock
import unittest
import sys
import os
from flask import session, Response, redirect, jsonify, url_for, json

# Adjust the import path based on your project structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.routes import *

class TestRoutes(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    # home
    def test_home_logged_in(self):
        """Test whether home page is rendered properly when user is logged in."""
        with self.app.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = self.app.get('/')
        self.assertIn(b'Profile', response.data)  # Assuming 'Profile' message is in the template

    def test_home_not_logged_in(self):
        """Test whether home page is rendered properly when user is not logged in."""
        with self.app.session_transaction() as sess:
            sess.pop('username', None)
        response = self.app.get('/')
        self.assertIn(b'login', response.data)  # Assuming 'Login' link is in the template
    
    
    # is_logged_in
    def test_is_logged_in(self):
        """Test whether is_logged_in function correctly identifies logged in users."""
        with app.test_request_context('/'):
            session['username'] = 'testuser'
            self.assertTrue(is_logged_in())

    def test_is_not_logged_in(self):
        """Test whether is_logged_in function correctly identifies users who are not logged in."""
        with app.test_request_context('/'):
            session.pop('username', None)
            self.assertFalse(is_logged_in())
    
    
    # logout
    def test_logout(self):
        """Tests user logout."""
        with app.test_request_context('/'):
            session['username'] = 'testuser'
            response = logout()
            self.assertNotIn('username', session)  # Checks if the user has been logged out
            self.assertEqual(response.status_code, 302)  # Checks if the user has been redirected to the home page


    # test_connection
    def test_connection(self):
        """Tests the database connection."""
        with app.app_context():
            self.assertIsNone(test_connection())  # Checks if the database connection has been established correctly


    # login
    def test_login_post_request(self):
        """Tests the login functionality for POST requests."""
        # Mock the request context for the login route with a POST request and valid credentials
        with app.test_request_context('/login', method='POST', data={'username': 'testuser', 'password': 'testpassword'}):
            # Call the login function
            response = login()
            # Check if the response is an instance of Response
            self.assertIsInstance(response, Response)
            # Check if the response contains the expected message indicating successful login
            self.assertIn(b'Welcome, testuser!', response.data)
            # Check if the session contains the logged-in user's username
            self.assertEqual(session['username'], 'testuser')

    def test_login_successful(self):
        """Tests successful login."""
        with app.test_request_context('/login', method='POST', data={'username': 'testuser', 'password': 'testuser'}):
            response = login()
            self.assertEqual(response.status_code, 200)  # Expects response status code 200 (OK)
    
    
    # register
    def test_register_get_request(self):
        """Tests whether the registration form is correctly rendered for GET requests."""
        with self.app as client:
            response = client.get('/register')
            self.assertEqual(response.status_code, 200)  # Expects response status code 200 (OK)
            self.assertIn(b'<form id="registerForm">', response.data)  # Checks if the registration form is present

    def test_register_existing_user(self):
        """Tests reaction to attempting to register a user who already exists."""
        with app.test_request_context('/register', method='POST', data={'username': 'testuser', 'name': 'testuser', 'surname': 'existinguser', 'email': 'existing_user@example.com', 'password': 'testpassword'}):
            response = register()
            self.assertEqual(response[1], 409)  # Expects status code 409 (Conflict)
            self.assertEqual(response[0]['message'], "User already exists.")  # Expects user already exists message

    def test_register_invalid_data(self):
        """Tests reaction to attempting registration with invalid data."""
        with app.test_request_context('/register', method='POST', data={'username': '', 'name': 'testuser', 'surname': 'existinguser', 'email': 'invalid_email', 'password': 'short'}):
            response = register()
            self.assertEqual(response[1], 400)  # Expects status code 400 (Bad Request)
            self.assertEqual(response[0]['message'], "Invalid data provided.")  # Expects invalid data message

    def test_register_successful(self):
        """Tests successful registration of a new user."""
        with app.test_request_context('/register', method='POST', data={'username': 'new_user', 'name': 'testuser', 'surname': 'existinguser', 'email': 'new_user@example.com', 'password': 'testpassword'}):
            response_data, status_code = register()  # Accessing the response data and status code correctly
            self.assertEqual(status_code, 200)  # Expects status code 200 (OK)
            self.assertEqual(response_data['message'], "Registration successful.")  # Expects success message

    def test_register_database_connection_error(self):
        """Tests reaction to a database connection error during registration."""
        with app.test_request_context('/register', method='POST', data={'username': 'new_user', 'name': 'testuser', 'surname': 'existinguser', 'email': 'new_user@example.com', 'password': 'testpassword'}):
            with patch('app.routes.create_connection', return_value=None):  # Mocks the create_connection() function
                response = register()
                self.assertEqual(response[1], 500)  # Expects status code 500 (Internal Server Error)
                self.assertEqual(response[0]['message'], "Failed to connect to the database.")  # Expects database connection error message


    # userprofile
    def test_userprofile_logged_in(self):
        """Tests the user profile page when the user is logged in."""
        with app.test_request_context('/userprofile'):
            session['username'] = 'testuser'
            response = userprofile()
            self.assertIn(b'UserProfile', response.data)  # Expects the user profile page to contain the phrase 'UserProfile'

    def test_userprofile_not_logged_in(self):
        """Tests the user profile page when the user is not logged in."""
        with app.test_request_context('/userprofile'):
            session.pop('username', None)
            response = userprofile()
            self.assertEqual(response.status_code, 302)  # Expects a redirection to the login page

    def test_userprofile_template_rendered(self):
        """Tests if the user profile page template is rendered correctly."""
        with self.app as client:
            with client.session_transaction() as sess:
                sess['username'] = 'test_user'
            response = client.get('/userprofile')
            self.assertEqual(response.status_code, 200)  # Expects response status code 200 (OK)
            self.assertIn(b'User Profile', response.data)  # Expects the user profile page to contain the phrase 'User Profile'


    # purchase_form
    @patch('app.routes.render_template')
    @patch('app.routes.is_logged_in')
    def test_purchase_form_logged_in(self, mock_is_logged_in, mock_render_template):
        """Test purchase_form when user is logged in."""
        mock_is_logged_in.return_value = True
        mock_render_template.return_value = 'Purchase Page'

        with self.app.session_transaction() as sess:
            sess['username'] = 'test_user'

        response = self.app.get('/purchase_form')

        mock_render_template.assert_called_once_with('purchase.html', logged_in=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Purchase Page')

    def test_purchase_form_not_logged_in(self):
        """Test purchase_form when user is not logged in."""
        with self.app.session_transaction() as sess:
            sess.pop('username', None)

        response = self.app.get('/purchase_form', follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)


    # get_plan_price
    @patch('app.routes.create_connection')
    def test_get_plan_price_plan_not_found(self, mock_create_connection):
        """Tests retrieval of a price for a non-existent plan."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_create_connection.return_value = mock_conn

        response = self.app.get('/get_plan_price?plan_name=NonExistentPlan')
        self.assertEqual(response.status_code, 404)

    @patch('app.routes.create_connection')
    def test_get_plan_price_db_connection_failure(self, mock_create_connection):
        mock_create_connection.return_value = None

        response = get_plan_price("test_plan")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['message'], "Failed to connect to the database.")



    # purchase_plan
    @patch('app.routes.create_connection')
    def test_purchase_plan_not_logged_in(self, mock_create_connection):
        """Tests purchase_plan when user is not logged in."""
        mock_create_connection.return_value = MagicMock()
        with self.app.session_transaction() as sess:
            sess.pop('username', None)

        response = self.app.post('/purchase_plan', json={})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"message": "User not logged in."})

    @patch('app.routes.create_connection')
    def test_purchase_plan_invalid_input_fields(self, mock_create_connection):
        """Tests purchase_plan with invalid or missing input fields."""
        mock_create_connection.return_value = MagicMock()

        response = self.app.post('/purchase_plan', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "All fields are required."})

    @patch('app.routes.create_connection')
    def test_purchase_plan_invalid_card_number(self, mock_create_connection):
        """Tests purchase_plan with an invalid card number."""
        mock_create_connection.return_value = MagicMock()

        response = self.app.post('/purchase_plan', json={'cardNumber': '123456789012345'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "Invalid card number. It should be 16 digits."})


    @patch('app.routes.create_connection')
    def test_purchase_plan_database_connection_failure(self, mock_create_connection):
        """Tests purchase_plan with a database connection failure."""
        mock_create_connection.return_value = None

        response = self.app.post('/purchase_plan', json={})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"message": "Failed to connect to the database."})

    @patch('app.routes.create_connection')
    def test_purchase_plan_sql_error(self, mock_create_connection):
        """Tests purchase_plan with an SQL error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception('SQL error')
        mock_conn.cursor.return_value = mock_cursor
        mock_create_connection.return_value = mock_conn

        response = self.app.post('/purchase_plan', json={})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"message": "SQL error"})


    # interpreter
    @patch('app.routes.is_logged_in', return_value=True)
    @patch('app.routes.render_template')
    def test_interpreter_logged_in(self, mock_render_template, mock_is_logged_in):
        """Test whether interpreter page is rendered properly when user is logged in."""
        # Mocking render_template to return a response object
        mock_render_template.return_value = Response(status=200)

        # Call the function
        response = interpreter()

        # Assertions
        mock_render_template.assert_called_once_with('sli.html', logged_in=True)
        self.assertEqual(response.status_code, 200)

    @patch('app.routes.is_logged_in', return_value=False)
    @patch('app.routes.render_template')
    def test_interpreter_not_logged_in(self, mock_render_template, mock_is_logged_in):
        """Test whether interpreter page is rendered properly when user is not logged in."""
        # Mocking render_template to return a response object
        mock_render_template.return_value = Response(status=200)

        # Call the function
        response = interpreter()

        # Assertions
        mock_render_template.assert_called_once_with('sli.html', logged_in=False)
        self.assertEqual(response.status_code, 200)


    #pricing 
    @patch('app.routes.create_connection')
    @patch('app.routes.format_price')
    @patch('app.routes.render_template')
    @patch('app.routes.is_logged_in')
    def test_pricing_successful(self, mock_is_logged_in, mock_render_template, mock_format_price, mock_create_connection):
        """Test pricing function with successful retrieval of plans and rendering."""
        # Mocking database connection and format_price function
        mock_create_connection.return_value = MagicMock()
        mock_create_connection.return_value.cursor.return_value.fetchall.return_value = [
            {'id': 1, 'plan_name': 'Basic', 'price': 10.00},
            {'id': 2, 'plan_name': 'Premium', 'price': 20.99},
            {'id': 3, 'plan_name': 'Ultimate', 'price': 30.50}
        ]
        mock_format_price.side_effect = lambda price: (int(price), int((price - int(price)) * 100))

        # Mocking is_logged_in function
        mock_is_logged_in.return_value = True

        # Call the function
        response = pricing()

        # Assertions
        mock_render_template.assert_called_once_with('pricing.html', plans=[
            {'id': 1, 'plan_name': 'Basic', 'price': 10.00, 'dollars': 10, 'cents': '00'},
            {'id': 2, 'plan_name': 'Premium', 'price': 20.99, 'dollars': 20, 'cents': '98'},
            {'id': 3, 'plan_name': 'Ultimate', 'price': 30.50, 'dollars': 30, 'cents': '50'}
        ], logged_in=True)
        self.assertEqual(response, mock_render_template.return_value)


    #delete_account
    @patch('app.routes.create_connection')
    @patch('app.routes.session', {'username': 'test_user'})
    @patch('app.routes.url_for')
    def test_delete_account_successful(self, mock_url_for, mock_create_connection):
        """Test delete_account function with successful account deletion."""
        # Mocking database connection
        mock_connection = mock_create_connection.return_value
        mock_cursor = mock_connection.cursor.return_value

        # Mocking user ID retrieval
        mock_cursor.fetchone.return_value = (1,)

        # Call the function
        response = delete_account()

        # Assertions
        mock_cursor.execute.assert_called_with("DELETE FROM payments WHERE user_id = %s", (1,))
        mock_connection.commit.assert_called()
        mock_cursor.execute.assert_called_with("DELETE FROM users WHERE id = %s", (1,))
        mock_connection.commit.assert_called()
        mock_url_for.assert_called_with('home')
        self.assertEqual(session, {})  # Session should be empty after logout
        self.assertEqual(response, jsonify({"message": "Account deleted successfully.", "redirect": mock_url_for.return_value}))


    #reset_password
    @patch('app.routes.create_connection')
    @patch('app.routes.send_reset_email')
    @patch('app.routes.uuid')
    @patch('app.routes.request')
    def test_reset_password_successful(self, mock_request, mock_uuid, mock_send_reset_email, mock_create_connection):
        """Test reset_password function with successful password reset."""
        # Mocking request data
        mock_request.get_json.return_value = {'email': 'test@example.com'}

        # Mocking database connection
        mock_connection = mock_create_connection.return_value
        mock_cursor = mock_connection.cursor.return_value

        # Mocking user retrieval
        mock_cursor.fetchone.return_value = {'id': 1}

        # Mocking UUID generation
        mock_uuid.uuid4.return_value = 'fake_token'

        # Call the function
        response = reset_password()

        # Assertions
        mock_cursor.execute.assert_called_with("SELECT * FROM users WHERE email = %s", ('test@example.com',))
        mock_cursor.execute.assert_called_with("UPDATE users SET reset_token = %s WHERE email = %s", ('fake_token', 'test@example.com'))
        mock_connection.commit.assert_called()
        mock_send_reset_email.assert_called_with('test@example.com', 'fake_token')
        self.assertEqual(response, jsonify({"message": "Password reset email sent.", "reset_link": "http://127.0.0.1:5000/reset/fake_token"}))


    #reset_with_token
    @patch('app.routes.render_template')
    @patch('app.routes.redirect')
    @patch('app.routes.url_for')
    def test_reset_with_token_render_form(self, mock_url_for, mock_redirect, mock_render_template):
        """Test reset_with_token function renders password reset form."""
        # Mocking request method and providing token
        with app.test_request_context('/reset/token123', method='GET'):
            response = reset_with_token('token123')

        # Assertions
        mock_render_template.assert_called_once_with('reset_password.html', token='token123')

    @patch('app.routes.flash')
    @patch('app.routes.bcrypt')
    @patch('app.routes.create_connection')
    @patch('app.routes.redirect')
    @patch('app.routes.url_for')
    def test_reset_with_token_successful_reset(self, mock_url_for, mock_redirect, mock_create_connection, mock_bcrypt, mock_flash):
        """Test reset_with_token function successfully resets password."""
        # Mocking request method and providing form data
        with app.test_request_context('/reset/token123', method='POST', data={'password': 'newpassword', 'confirm_password': 'newpassword'}):
            # Mocking bcrypt hashpw
            mock_bcrypt.hashpw.return_value = b'hashed_password'

            # Mocking database connection
            mock_connection = mock_create_connection.return_value
            mock_cursor = mock_connection.cursor.return_value

            # Call the function
            response = reset_with_token('token123')

            # Assertions
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
            mock_flash.assert_called_with("Password reset successfully.", "success")
            mock_redirect.assert_called_with(url_for('login'))
            
            
    #reset_password_link           
    @patch('app.routes.create_connection')
    def test_reset_password_link_generation(self, mock_create_connection):
        """Test reset_password_link function generates password reset link."""
        # Mocking request method and providing JSON data
        with app.test_request_context('/reset_password_link', method='POST', data=json.dumps({'email': 'test@example.com'})):
            # Mocking database connection
            mock_connection = mock_create_connection.return_value
            mock_cursor = mock_connection.cursor.return_value

            # Call the function
            response = reset_password_link()

            # Assertions
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
            self.assertIn("reset_link", response.get_json())            
            
            
    #generate_reset_token       
    @patch('app.routes.create_connection')
    def test_generate_reset_token_logged_in(self, mock_create_connection):
        """Test generate_reset_token function for a logged-in user."""
        # Simulate logged-in user in session
        with app.test_request_context('/generate_reset_token'):
            session['username'] = 'test_user'
            
            # Mocking database connection
            mock_connection = mock_create_connection.return_value
            mock_cursor = mock_connection.cursor.return_value
            # Mocking the database query result to simulate user found in the database
            mock_cursor.fetchone.return_value = {'username': 'test_user'}
            
            # Call the function
            response = generate_reset_token()

            # Assertions
            # Ensure that execute is called to retrieve the user and then to update the reset_token
            mock_cursor.execute.assert_called()
            # Ensure that commit is called after the update query
            mock_connection.commit.assert_called()
            # Ensure that the response contains the reset_link
            self.assertIn("reset_link", response.get_json())       
            
            
if __name__ == '__main__':
    # Ładowanie testów
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRoutes)

    # Tworzenie wyników testów
    result = unittest.TestResult()

    # Wykonanie testów
    suite.run(result)

    # Statystyki testów
    print("Total tests:", result.testsRun)
    print("Passed tests:", result.testsRun - len(result.failures) - len(result.errors))
    print("Failed tests:", len(result.failures) + len(result.errors))

    # Wyświetlenie informacji o błędach
    if result.failures or result.errors:
        print("\nErrors and Failures:")
        for err in result.failures + result.errors:
            test_case, message = err
            print(f"\nTest Case: {test_case._testMethodName}")
            print(f"Error Message: {message}")
