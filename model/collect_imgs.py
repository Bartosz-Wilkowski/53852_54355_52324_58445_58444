import os
import time
import cv2
import mediapipe as mp
from signs_list import CHARS_LIST

# convert the chars list to a tuple
CHARS_TUPLE = tuple(CHARS_LIST)

# set the output data directory path
DATA_DIR = './model/data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# set the size of the dataset
datasetSize = 100

# initialize hands recognition using mediapipe
mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils
mpDrawingStyles = mp.solutions.drawing_styles

hands = mpHands.Hands(static_image_mode=True, min_detection_confidence=0.3)


def collect_imgs(dataDirectory,
                 dataClasses,
                 datasetSize,
                 imgSource=0,
                 drawLandmarks=True):
    """
    Function to collect images for each hand character sign.

    Parameters:
    - dataDirectory: Directory to save the collected images.
    - dataClasses: Tuple containing classes of characters.
    - datasetSize: Number of images to collect for each character sign.
    - imgSource: Source of images (e.g., camera index or file path).
    - drawLandmarks: Boolean to draw landmarks in live.
    """
    # capture video from the provided source
    capture = cv2.VideoCapture(imgSource)

    for i in range(len(CHARS_TUPLE)):
        # check if class directory exists within data directory
        if not os.path.exists(os.path.join(DATA_DIR, str(i))):
            os.makedirs(os.path.join(DATA_DIR, str(i)))

        while capture.isOpened():
            ret, frame = capture.read()

            if drawLandmarks:
                # detect hand landmarks
                results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mpDrawing.draw_landmarks(
                            frame, hand_landmarks, mpHands.HAND_CONNECTIONS,
                            mpDrawingStyles.get_default_hand_landmarks_style(),
                            mpDrawingStyles.get_default_hand_connections_style())

            # display instructions on the frame
            cv2.putText(frame, f"Collecting data for sign: {CHARS_TUPLE[i]}",
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2,
                        cv2.LINE_AA)
            cv2.putText(frame, "Start? Press 'S'",
                        (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2,
                        cv2.LINE_AA)
            cv2.putText(frame, "Next sign? Press 'N'",
                        (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2,
                        cv2.LINE_AA)
            cv2.putText(frame, "Quit? Press 'Q'",
                        (10, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2,
                        cv2.LINE_AA)
            cv2.imshow('Collect imgs', frame)
            key = cv2.waitKey(25)
            # checking key presses
            if key == ord('s') or key == ord('q') or key == ord('n'):
                break
        # skip collecting img for the current sign if 'n' key is pressed
        if key == ord("n"):
            continue

        # close the window and terminate the module if 'q' key is pressed
        if key == ord('q'):
            break

        # initialize the counter for number of collected images
        counter = 0

        # save every img until reaching number of collected images
        while counter < datasetSize:
            ret, frame = capture.read()
            cv2.imshow('frame', frame)
            cv2.waitKey(25)
            cv2.imwrite(os.path.join(DATA_DIR, str(
                i), '{}.jpg'.format(time.time())), frame)

            counter += 1

    capture.release()
    cv2.destroyAllWindows()


# calling the function to collect images
collect_imgs(DATA_DIR, CHARS_TUPLE, datasetSize)
