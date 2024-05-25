from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import base64
import mediapipe as mp
from .routes import home, login_form, login, register, userprofile, get_user_data, purchase_plan, purchase_form
from .database import init_db, create_connection
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AEH'
socketio = SocketIO(app)
model = load_model('models/final_model/final_model.h5')

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Labels for the gesture recognition model
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
          'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

# Adding URL rules for the initial routes
app.add_url_rule('/', view_func=home)
app.add_url_rule('/login', view_func=login_form, methods=['GET'])
app.add_url_rule('/login', view_func=login, methods=['POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/userprofile', view_func=userprofile, methods=['GET'])
app.add_url_rule('/get-user-data', view_func=get_user_data, methods=['GET'])
app.add_url_rule('/purchase_form', view_func=purchase_form, methods=['GET'])
app.add_url_rule('/purchase_plan', view_func=purchase_plan, methods=['POST'])

# Initialize the database
init_db()


@app.route('/websocket')
def index():
    return render_template('index.html')


def get_user_sign_limit():
    if 'username' in session:
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT plan, last_reset, recognized_count FROM users WHERE username = %s", (session['username'],))
            user_data = cursor.fetchone()
            cursor.close()
            connection.close()
            if user_data:
                plan = user_data['plan']
                last_reset = user_data['last_reset']
                if last_reset is None or (datetime.now() - last_reset).days >= 1:
                    reset_recognition_count(session['username'])
                    last_reset = datetime.now()
                    update_last_reset(session['username'], last_reset)
                if plan == 'Basic':
                    return 100  # example limit for basic plan
                elif plan == 'Premium':
                    return 1000  # example limit for premium plan
                else:
                    return 10  # default limit
    return 10  # default limit for guests


def reset_recognition_count(username):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET recognized_count = 0 WHERE username = %s", (username,))
        connection.commit()
        cursor.close()
        connection.close()


def update_last_reset(username, last_reset):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET last_reset = %s WHERE username = %s", (last_reset, username))
        connection.commit()
        cursor.close()
        connection.close()


@socketio.on('image')
def handle_image(data):
    if 'recognized_count' not in session:
        session['recognized_count'] = 0

    limit = get_user_sign_limit()
    if session['recognized_count'] >= limit:
        emit('limit_reached')
        return

    img_data = base64.b64decode(data['image'])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the image using MediaPipe Hands
    results = mp_hands.process(img)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract landmarks
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])

            landmarks = np.array(landmarks).flatten()

            # Normalize landmarks
            landmarks = (landmarks - np.min(landmarks)) / \
                (np.max(landmarks) - np.min(landmarks))

            # Add batch dimension
            landmarks = np.expand_dims(landmarks, axis=0)

            # Make prediction
            prediction = model.predict(landmarks)

            # Get the predicted class
            predicted_class = labels[np.argmax(prediction)]

            session['recognized_count'] += 1
            emit('prediction', {'prediction': predicted_class})
            return

    emit('prediction', {'prediction': 'No hand detected'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
