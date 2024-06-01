"""
Module: gesture_recognition

This module contains classes and WebSocket event handlers for performing gesture recognition using
the MediaPipe Hands library and a trained deep learning model.

Classes:
    - GestureRecognizer: Class responsible for managing the gesture recognition process.
    - UserManager: Class responsible for managing user data and limits.

WebSocket Event Handlers:
    - handle_image(data): Handle image data received from the client and perform gesture recognition.

Dependencies:
    - Flask
    - Flask-SocketIO
    - TensorFlow
    - OpenCV (cv2)
    - Base64
    - MediaPipe
    - datetime
    - uuid
"""

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import base64
import mediapipe as mp
from .database import create_connection, init_db, reset_recognized_count, revoke_drop_privileges
from datetime import datetime, timedelta
import uuid  # Import to generate unique guest IDs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AEH'
socketio = SocketIO(app)
model = load_model('models/final_model/final_model.h5')

class GestureRecognizer:
    """
    A class to handle gesture recognition using MediaPipe Hands and a trained model.

    Attributes:
        model (keras.Model): The trained deep learning model.
        mp_hands (mp.solutions.hands.Hands): The MediaPipe Hands solution.
        labels (list): The labels for the gesture recognition model.
    """

    def __init__(self, model_path):
        """
        Initialize the GestureRecognizer class.

        Args:
            model_path (str): Path to the trained model.
        """
        self.model = load_model(model_path)
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                       'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

    def recognize_gesture(self, img):
        """
        Perform gesture recognition on the provided image.

        Args:
            img (numpy.ndarray): The image to perform gesture recognition on.

        Returns:
            str: The predicted gesture label.
        """
        results = self.mp_hands.process(img)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = img.shape
                x_min = int(min(lm.x for lm in hand_landmarks.landmark) * w)
                x_max = int(max(lm.x for lm in hand_landmarks.landmark) * w)
                y_min = int(min(lm.y for lm in hand_landmarks.landmark) * h)
                y_max = int(max(lm.y for lm in hand_landmarks.landmark) * h)

                # Ensure coordinates are within image bounds
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(w, x_max)
                y_max = min(h, y_max)

                # Region of Interest (ROI)
                roi = img[y_min:y_max, x_min:x_max]
                if roi.size == 0:
                    continue
                zoomed_roi = cv2.resize(roi, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)

                # Adjusting new ROI coordinates to stay within bounds
                new_y_max = min(y_min + zoomed_roi.shape[0], h)
                new_y_min = max(0, new_y_max - zoomed_roi.shape[0])
                new_x_max = min(x_min + zoomed_roi.shape[1], w)
                new_x_min = max(0, new_x_max - zoomed_roi.shape[1])

                zoomed_roi = zoomed_roi[:new_y_max-new_y_min, :new_x_max-new_x_min]

                img[new_y_min:new_y_max, new_x_min:new_x_max] = zoomed_roi

                # Prepare landmarks for prediction
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y, lm.z])

                landmarks = np.array(landmarks).flatten()
                landmarks = (landmarks - np.min(landmarks)) / (np.max(landmarks) - np.min(landmarks))
                landmarks = np.expand_dims(landmarks, axis=0)

                # Make prediction
                prediction = self.model.predict(landmarks)
                predicted_class = self.labels[np.argmax(prediction)]
                return predicted_class

        return 'No hand detected'

class UserManager:
    """
    A class to manage user data and recognition limits.

    Attributes:
        session (dict): The Flask session object.
    """

    def __init__(self, session):
        """
        Initialize the UserManager class.

        Args:
            session (dict): The Flask session object.
        """
        self.session = session

    def get_user_sign_limit(self):
        """
        Get the sign limit for the current user.

        Returns:
            int: The sign limit for the user. If the user is not logged in or the limit cannot be retrieved,
            a default limit of 10 is returned.
        """
        if 'username' in self.session:
            username = self.session['username']
        else:
            if 'guest_id' not in self.session:
                self.session['guest_id'] = str(uuid.uuid4())  # Generate a unique guest ID
            username = self.session['guest_id']

        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT users.plan_name, users.last_reset, users.recognized_count, subscription_plan.daily_limit
                FROM users
                JOIN subscription_plan ON users.plan_name = subscription_plan.plan_name
                WHERE users.username = %s
            ''', (username,))
            user_data = cursor.fetchone()
            cursor.close()
            connection.close()
            if user_data:
                last_reset = user_data['last_reset']
                daily_limit = user_data['daily_limit']
                if last_reset is None or (datetime.now() - last_reset).days >= 1:
                    reset_recognition_count(username)
                    last_reset = datetime.now()
                    self.update_last_reset(username, last_reset)
                return daily_limit if daily_limit is not None else float('inf')  # Handle unlimited plan
        return 10  # Default limit for guests

    def reset_recognition_count(self, username):
        """
        Reset the recognition count for the specified user.

        Args:
            username (str): The username for which the recognition count should be reset.
        """
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET recognized_count = 0 WHERE username = %s", (username,))
            connection.commit()
            cursor.close()
            connection.close()

    def update_last_reset(self, username, last_reset):
        """
        Update the last reset time for the specified user.

        Args:
            username (str): The username for which the last reset time should be updated.
            last_reset (datetime): The new last reset time.
        """
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET last_reset = %s WHERE username = %s", (last_reset, username))
            connection.commit()
            cursor.close()
            connection.close()

    def update_recognized_count(self, username, count):
        """
        Update the recognized count for the specified user.

        Args:
            username (str): The username for which the recognized count should be updated.
            count (int): The new recognized count.
        """
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET recognized_count = %s WHERE username = %s", (count, username))
            connection.commit()
            cursor.close()
            connection.close()


gesture_recognizer = GestureRecognizer('models/final_model/final_model.h5')
user_manager = UserManager(session)


def websocket_index():
    """
    Render the index.html template for the WebSocket application.

    Returns:
        Response: The rendered index.html template.
    """
    return render_template('index.html')


@socketio.on('image')
def handle_image(data):
    """
    Handle image data received from the client and perform gesture recognition.

    Args:
        data (dict): A dictionary containing the image data.
    """
    if 'recognized_count' not in session:
        session['recognized_count'] = 0

    limit = user_manager.get_user_sign_limit()
    if session['recognized_count'] >= limit:
        emit('limit_reached')
        return

    img_data = base64.b64decode(data['image'])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    predicted_class = gesture_recognizer.recognize_gesture(img)

    session['recognized_count'] += 1

    # Update the recognized count in the database
    if 'username' in session:
        username = session['username']
    else:
        username = session['guest_id']
    user_manager.update_recognized_count(username, session['recognized_count'])

    emit('prediction', {'prediction': predicted_class})
