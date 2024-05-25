
from flask import Flask, render_template
from .routes import home, login, register, userprofile, get_user_data, purchase_plan, purchase_form, logout
from .database import init_db
from flask_socketio import SocketIO, emit
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import base64
import mediapipe as mp


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
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/userprofile', view_func=userprofile, methods=['GET'])
app.add_url_rule('/get-user-data', view_func=get_user_data, methods=['GET'])
app.add_url_rule('/purchase_form', view_func=purchase_form, methods=['GET'])
app.add_url_rule('/purchase_plan', view_func=purchase_plan, methods=['POST'])
app.add_url_rule('/logout', view_func=logout, methods=['GET'])

# Initialize the database
init_db()


@app.route('/websocket')
def index():
    return render_template('index.html')


@socketio.on('image')
def handle_image(data):
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

            emit('prediction', {'prediction': predicted_class})
            return

    emit('prediction', {'prediction': 'No hand detected'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
