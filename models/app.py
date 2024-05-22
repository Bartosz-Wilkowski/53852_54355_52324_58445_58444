from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import base64
import mediapipe as mp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
model = load_model('model/final_model/final_model.h5')

# get hd from mp
mp_hands = mp.solutions.hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# labels
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
          'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('image')
def handle_image(data):
    img_data = base64.b64decode(data['image'])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # mp hd
    results = mp_hands.process(img)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # get landmarks
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])

            landmarks = np.array(landmarks).flatten()

            # normalization
            landmarks = (landmarks - np.min(landmarks)) / \
                (np.max(landmarks) - np.min(landmarks))

            # batch dimension
            landmarks = np.expand_dims(landmarks, axis=0)

            # predicition
            prediction = model.predict(landmarks)

            # A-Z
            predicted_class = labels[np.argmax(prediction)]

            emit('prediction', {'prediction': predicted_class})
            return

    emit('prediction', {'prediction': 'No hand detected'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
