import os
import numpy as np
import cv2
import mediapipe as mp
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# mp
mp_hands = mp.solutions.hands.Hands(
    static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

# existing model
model_path = 'model/final_model/final_model.h5'

# test datset
test_dataset_path = 'model/dataset/test'

# labels
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
          'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

# process data


def process_test_dataset(dataset_path):
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


# load model
model = load_model(model_path)

# process dataset
X_test, y_test = process_test_dataset(test_dataset_path)

# prediction
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)

# create and save confusion matrix
try:
    # conf mx
    conf_matrix = confusion_matrix(
        y_test, y_pred_classes, labels=np.arange(len(labels)))

    # display conf mx
    disp = ConfusionMatrixDisplay(
        confusion_matrix=conf_matrix, display_labels=labels)
    disp.plot(cmap=plt.cm.Blues)

    # save as jpg
    output_path = 'models/results'
    plt.savefig(output_path, format='jpg')
    plt.close()

    print(f"confusion matrix jpg saved at: {output_path}")

except Exception as e:
    print("an error occurred while generating confusion matrix:", e)
