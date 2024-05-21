import os
import numpy as np
import cv2
import mediapipe as mp
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint

# get mediapipe
mp_hands = mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

# existing model
existing_model_path = '/Users/wiola/Desktop/sign-language-interpreter/sign_language_model.h5'

# new dataset for training
new_dataset_path = '/Users/wiola/Desktop/sign-language-interpreter/dataset/train'

# labels
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

# get ohv
def process_new_dataset(dataset_path):
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
                
                landmarks = np.array(landmarks).flatten()  # Spłaszczenie tablicy
                
                X.append(landmarks)
                y.append(labels.index(label))
    
    X = np.array(X)
    y = np.array(y)
    return X, y

# load model
existing_model = load_model(existing_model_path)

# process new dataset
X_new_train, y_new_train = process_new_dataset(new_dataset_path)

# compile model
existing_model.compile(optimizer=Adam(),
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

# get best results
checkpoint_path = "checkpoint_model.h5"
checkpoint = ModelCheckpoint(checkpoint_path, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')

# train on new data
history = existing_model.fit(X_new_train, y_new_train, epochs=10, batch_size=32, validation_split=0.2, callbacks=[checkpoint])

# save after training
existing_model.save("final_model.h5")
print("saved as 'final_model.h5'")