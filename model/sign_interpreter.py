import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
from signs_list import labels_dict

# load the model
model = load_model('./model/tf_model.keras')

# set up MediaPipe Hands module
mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils
mpDrawingStyles = mp.solutions.drawing_styles

# start capturing video from webcam
cap = cv2.VideoCapture(0)

# main loop for real-time processing
with mpHands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)

        # draw landmarks on the frame
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mpDrawing.draw_landmarks(
                    frame, hand_landmarks, mpHands.HAND_CONNECTIONS,
                    mpDrawingStyles.get_default_hand_landmarks_style(),
                    mpDrawingStyles.get_default_hand_connections_style())

            # extract keypoints for sign recognition
            keypoints = []
            for hand_landmarks in results.multi_hand_landmarks:
                for landmark in hand_landmarks.landmark:
                    keypoints.append(landmark.x)
                    keypoints.append(landmark.y)

            # perform sign recognition
            keypoints = np.array(keypoints)
            keypoints = keypoints.flatten()
            # ensure that the number of keypoints matches the expected input shape (42)
            if len(keypoints) == 42:
                prediction = model.predict(
                    np.expand_dims(keypoints, axis=0))[0]
                predicted_character = labels_dict[np.argmax(prediction)]

                # display the predicted letter on the frame
                cv2.putText(frame, predicted_character, (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        cv2.imshow('Sign Recognition', frame)

        # break the loop when 'q' is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# release resources
cap.release()
cv2.destroyAllWindows()
