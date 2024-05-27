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
model = load_model('/Users/wiola/Desktop/sign-language-interpreter/model/checkpoint_model.h5')

# mp hd
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
        
            h, w, _ = img.shape
            x_min = int(min(lm.x for lm in hand_landmarks.landmark) * w)
            x_max = int(max(lm.x for lm in hand_landmarks.landmark) * w)
            y_min = int(min(lm.y for lm in hand_landmarks.landmark) * h)
            y_max = int(max(lm.y for lm in hand_landmarks.landmark) * h)

           
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(w, x_max)
            y_max = min(h, y_max)

            # ROI
            roi = img[y_min:y_max, x_min:x_max]
            if roi.size == 0:
                continue
            zoomed_roi = cv2.resize(roi, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)

           
            new_y_max = min(y_min + zoomed_roi.shape[0], h)
            new_y_min = max(0, new_y_max - zoomed_roi.shape[0])
            new_x_max = min(x_min + zoomed_roi.shape[1], w)
            new_x_min = max(0, new_x_max - zoomed_roi.shape[1])

    
            zoomed_roi = zoomed_roi[:new_y_max-new_y_min, :new_x_max-new_x_min]

       
            img[new_y_min:new_y_max, new_x_min:new_x_max] = zoomed_roi

            # landmarks
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])

            landmarks = np.array(landmarks).flatten()
            landmarks = (landmarks - np.min(landmarks)) / (np.max(landmarks) - np.min(landmarks))
            landmarks = np.expand_dims(landmarks, axis=0)

            # prediction
            prediction = model.predict(landmarks)
            predicted_class = labels[np.argmax(prediction)]

            emit('prediction', {'prediction': predicted_class})
            return

    emit('prediction', {'prediction': 'No hand detected'})


if __name__ == '__main__':
    socketio.run(app, debug=True)