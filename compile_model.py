import os
import numpy as np
import cv2
import mediapipe as mp
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical

# get mp
mp_hands = mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

# test and train set
train_dataset_path = '/Users/wiola/Desktop/sign-language-interpreter/dataset/train'
test_dataset_path = '/Users/wiola/Desktop/sign-language-interpreter/dataset/test'

# labels
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

# data process
def process_dataset(dataset_path):
    X = []
    y = []
    for label in labels:
        label_path = os.path.join(dataset_path, label)
        for img_name in os.listdir(label_path):
            img_path = os.path.join(label_path, img_name)
            img = cv2.imread(img_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # mp hd
            results = mp_hands.process(img_rgb)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y, lm.z])
                
                landmarks = np.array(landmarks).flatten() 
                
                X.append(landmarks)
                y.append(labels.index(label))
    
    X = np.array(X)
    y = np.array(y)
    return X, y

# process dataset
X_train, y_train = process_dataset(train_dataset_path)
X_test, y_test = process_dataset(test_dataset_path)

# one-hot encoding 
y_train = to_categorical(y_train, num_classes=len(labels))
y_test = to_categorical(y_test, num_classes=len(labels))

# def model
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(len(labels), activation='softmax')
])

# compile model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# train for x epochs
epochs = 20
for epoch in range(epochs):
    print(f"Epoch {epoch + 1}/{epochs}")
    history = model.fit(X_train, y_train, epochs=1, batch_size=32, validation_data=(X_test, y_test))
    print()

# save model
model.save('/Users/wiola/Desktop/sign-language-interpreter/sign_language_model.h5')