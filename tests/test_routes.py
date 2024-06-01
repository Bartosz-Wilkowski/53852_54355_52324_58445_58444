from unittest.mock import patch
import unittest
import sys
import os
from flask import session, Response

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.routes import home, login, register, userprofile, get_user_data, purchase_plan, purchase_form, logout, interpreter, delete_account, reset_password, reset_with_token, reset_password_link, pricing, get_plan_price, get_plans, generate_reset_token, is_logged_in, test_connection

class TestRoutes(unittest.TestCase):
    
    #home
    def test_home_logged_in(self):
        """Test whether home page is rendered properly when user is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'test_user'
            response = client.get('/')
            self.assertIn(b'Profile', response.data)  # Assuming 'Profile' message is in the template

    def test_home_not_logged_in(self):
        """Test whether home page is rendered properly when user is not logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess.pop('username', None)
            response = client.get('/')
            self.assertIn(b'login', response.data)  # Assuming 'Login' link is in the template
    
    
    #is_logged_in
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
    
    
    #logout
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
    def test_login_get_request(self):
        """Tests whether the login form is correctly rendered for GET requests."""
        with app.test_request_context('/login', method='GET'):
            response = login()
            if isinstance(response, Response):
                self.assertIn(b'Login', response.data)  # Checks if the form contains the word 'Login'
            else:
                self.fail("Login function did not return a proper response object")

    def test_login_invalid_credentials(self):
        """Tests the response to invalid login credentials."""
        with app.test_request_context('/login', method='POST', data={'username': 'testuser', 'password': 'wrong_password'}):
            response = login()
            if isinstance(response, Response):
                self.assertEqual(response.status_code, 401)  # Expects response status code 401 (Unauthorized)
            else:
                self.fail("Login function did not return a proper response object")

    def test_login_successful(self):
        """Tests successful login."""
        with app.test_request_context('/login', method='POST', data={'username': 'testuser', 'password': 'testuser'}):
            response = login()
            self.assertEqual(response.status_code, 200)  # Expects response status code 200 (OK)

    def test_login_database_connection_error(self):
        """Tests the response to a database connection error during login."""
        with app.test_request_context('/login', method='POST', data={'username': 'testuser', 'password': 'testuser'}):
            with patch('app.routes.create_connection', return_value=None):  # Mocks the create_connection() function
                response, _ = login()  # Unpack the tuple to get the response object
                self.assertEqual(response.status_code, 500)  # Expects response status code 500 (Internal Server Error)
    
    #register
    def test_register_get_request(self):
        """Tests whether the registration form is correctly rendered for GET requests."""
        with app.test_client() as client:
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


    #userprofile
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
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'test_user'
            response = client.get('/userprofile')
            self.assertEqual(response.status_code, 200)  # Expects response status code 200 (OK)
            self.assertIn(b'User Profile', response.data)  # Expects the user profile page to contain the phrase 'User Profile'


    #get_user_data
    def test_user_not_logged_in(self, mock_create_connection):
        # Mock the create_connection function to return None
        mock_create_connection.return_value = None
        
        # Simulate user not being logged in
        with patch.dict('your_module.session', {'username': None}):
            response, status_code = get_user_data()
            self.assertEqual(status_code, 401)
            self.assertIn("User not logged in.", response.get_json()["message"])

    def test_database_connection_failure(self, mock_create_connection):
        # Mock the create_connection function to return None
        mock_create_connection.return_value = None
        
        # Simulate user being logged in
        with patch.dict('your_module.session', {'username': 'test_user'}):
            response, status_code = get_user_data()
            self.assertEqual(status_code, 500)
            self.assertIn("Failed to connect to the database.", response.get_json()["message"])
            
    def test_user_not_found(self, mock_create_connection):
        # Mock the create_connection function to return a connection
        mock_connection = mock_create_connection.return_value
        mock_cursor = mock_connection.cursor.return_value
        
        # Simulate user being logged in but not found in the database
        with patch.dict('your_module.session', {'username': 'non_existent_user'}):
            mock_cursor.fetchone.return_value = None
            response, status_code = get_user_data()
            self.assertEqual(status_code, 404)
            self.assertIn("User not found.", response.get_json()["message"])

    def test_successful_user_data_retrieval(self):
        # Mock the create_connection function to return a connection
        with patch('user_data_module.create_connection') as mock_create_connection:
            mock_connection = mock_create_connection.return_value
            mock_cursor = mock_connection.cursor.return_value
            
            # Simulate user being logged in and found in the database
            with patch.dict('user_data_module.session', {'username': 'test_user'}):
                mock_cursor.fetchone.return_value = {'id': 1, 'username': 'test_user', 'name': 'Test', 'surname': 'User'}
                mock_cursor.fetchall.return_value = [{'payment_date': '2024-05-30', 'amount': 50}]
                response, status_code = get_user_data()
                self.assertEqual(status_code, 200)
                self.assertEqual(response.get_json()["username"], "test_user")
                self.assertEqual(response.get_json()["name"], "Test")
                self.assertEqual(response.get_json()["surname"], "User")
                self.assertEqual(response.get_json()["payment_history"], [{'payment_date': '2024-05-30', 'amount': 50}])










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
