import unittest
import os
import sys
import base64
import cv2
import numpy as np
from flask import Flask
from flask_socketio import SocketIO
import tensorflow as tf
from unittest.mock import patch

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "..")
sys.path.insert(0, app_dir)

from app import app, socketio

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        # Flask
        self.app = app.test_client()
        self.app.testing = True
        self.socketio = socketio.test_client(app)

    def tearDown(self):
        self.socketio.disconnect()

    def test_app_initialization(self):
        assert isinstance(app, Flask), "App is not a Flask instance"
        assert isinstance(socketio, SocketIO), "SocketIO is not initialized properly"

    def test_model_loading(self):
        model_path = 'models/final_model/final_model.h5'
        assert os.path.exists(model_path), f"Model file {model_path} does not exist"
        try:
            loaded_model = tf.keras.models.load_model(model_path)
            assert loaded_model is not None, "Failed to load model"
        except Exception as e:
            self.fail(f"Failed to load model: {str(e)}")

    def test_routes(self):
        response = self.app.get('/')
        assert response.status_code == 200, "Root route failed"

        response = self.app.get('/login')
        assert response.status_code == 200, "Login GET route failed"

        response = self.app.get('/register')
        assert response.status_code == 200, "Register GET route failed"

    def test_websocket_connection(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, img_encoded = cv2.imencode('.jpg', img)
        img_data = base64.b64encode(img_encoded).decode('utf-8')

        self.socketio.emit('image', {'image': img_data})
        received = self.socketio.get_received()

        assert len(received) > 0, "No response received from WebSocket"
        assert received[0]['name'] == 'prediction', "Unexpected response name"
        assert received[0]['args'][0]['prediction'] == 'No hand detected', "Unexpected prediction response"

    @patch('app.models.get_user_sign_limit')
    def test_handle_image(self, mock_get_user_sign_limit):
        mock_get_user_sign_limit.return_value = 100

        img = np.zeros((224, 224, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        self.socketio.emit('image', {'image': img_base64})
        received = self.socketio.get_received()

        self.assertTrue(any(event['name'] == 'prediction' for event in received))

        for event in received:
            if event['name'] == 'prediction':
                response = event['args'][0]
                self.assertIn('prediction', response)
                self.assertIn(response['prediction'], ['Invalid data', 'No hand detected'])

    @patch('app.models.get_user_sign_limit')
    def test_handle_image_limit_reached(self, mock_get_user_sign_limit):
        mock_get_user_sign_limit.return_value = 1

        with self.app.session_transaction() as sess:
            sess['recognized_count'] = 1

        img = np.zeros((224, 224, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        self.socketio.emit('image', {'image': img_base64})

        received = self.socketio.get_received()

        self.assertTrue(any(event['name'] == 'limit_reached' for event in received))

if __name__ == '__main__':
    unittest.main()
