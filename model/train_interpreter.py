import numpy as np
import pickle
import os
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import TensorBoard
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

# load dataset to train
with open('./model/data.pickle', 'rb') as f:
    data_dict = pickle.load(f)

# convert dataset and labels to numpy arrays
data = np.array(data_dict['data'])
labels = np.array(data_dict['labels'])

# convert string labels to integers
label_to_int = {label: i for i, label in enumerate(np.unique(labels))}
int_labels = np.array([label_to_int[label] for label in labels])

# assuming each sequence has different lengths
max_length = len(data[0])

# split dataset arrays into two sets
x_train, x_test, y_train, y_test = train_test_split(
    data, int_labels, test_size=0.2, shuffle=True, stratify=int_labels)

# define model architecture
model = Sequential([
    Input(shape=(max_length,)),  # Input shape now is (max_length,)
    Dense(128, activation='relu'),
    Dense(64, activation='relu'),
    Dense(len(np.unique(labels)), activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# TensorBoard callback
log_dir = os.path.join('model/Logs')
tb_callback = TensorBoard(log_dir=log_dir)

# train model
model.fit(x_train, y_train, epochs=50, batch_size=32,
          validation_split=0.1, callbacks=[tb_callback])

# Save trained model
model.save('./model/tf_model.keras')

# make predictions
y_pred = np.argmax(model.predict(x_test), axis=1)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)

# build confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(conf_matrix)
