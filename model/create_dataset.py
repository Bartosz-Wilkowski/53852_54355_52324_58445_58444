import os
import pickle
import mediapipe as mp
import cv2

# Setting the data directory path
DATA_DIR = './model/data'

# Initialize hands recognition using MediaPipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Initialize arrays for landmarks' coordinates and signs' categories
data = []
labels = []

# For each sign category file within 'data' folder
for signLabel in os.listdir(DATA_DIR):
    # For each image within sign category folder
    for img_path in os.listdir(os.path.join(DATA_DIR, signLabel)):

        # Load image and convert to RGB format
        img = cv2.imread(os.path.join(DATA_DIR, signLabel, img_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process image to detect hand landmarks
        results = hands.process(img_rgb)

        # If hand is detected, extract landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.extend([landmark.x, landmark.y])
                data.append(landmarks)  # Append landmarks to data
                labels.append(signLabel)  # Append label to labels

# Save array of landmarks coordinates and labels
with open('model/data.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)
