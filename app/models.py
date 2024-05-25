from flask import render_template
from flask_socketio import emit
import numpy as np
import cv2
import base64
from tensorflow.keras.models import load_model
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Labels for the gesture recognition model
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
          'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

model = load_model('models/final_model/final_model.h5')

def websocket_index():
    return render_template('index.html')

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
            landmarks = (landmarks - np.min(landmarks)) / (np.max(landmarks) - np.min(landmarks))

            # Add batch dimension
            landmarks = np.expand_dims(landmarks, axis=0)

            # Make prediction
            prediction = model.predict(landmarks)

            # Get the predicted class
            predicted_class = labels[np.argmax(prediction)]

            emit('prediction', {'prediction': predicted_class})
            return

    emit('prediction', {'prediction': 'No hand detected'})
