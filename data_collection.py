import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time

# set img source as webcam
capture = cv2.VideoCapture(0)

# set detecting only one hand simultaneously
detector = HandDetector(maxHands=1)

# set padding for detected hand in px
offset = 20

# set captured hand image size in px
imgSize = 300

# TODO CUSTOMIZABLE DIRECTORY
# directory to saved img
folder = "Data/A"

# initalize taken img count
counter = 0

while True:
    # get img from webcam
    success, img = capture.read()
    hands, img = detector.findHands(img)

    # initalize a matrix which contains captured img
    imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

    if hands:
        hand = hands[0]
        x, y, width, height = hand['bbox']

        # create an img which contains captured hand picture
        imgCrop = img[y-offset:y + height+offset, x-offset:x + width+offset]

        imgCropShape = imgCrop.shape

        # adjust the captured imgCrop size
        if height > width:
            # if the height > width calculate and increase img width
            widthFactor = imgSize / height
            widthCalc = math.ceil(widthFactor * width)
            imgResize = cv2.resize(imgCrop, (widthCalc, imgSize))
            imgResizeShape = imgResize.shape

            # calculate gap to get the value to center img vertically
            widthGap = math.ceil((imgSize-widthCalc)/2)

            # put the imgResize in a limited area of imgWhite and center img
            imgWhite[:, widthGap:widthCalc + widthGap] = imgResize

        else:
            # if the width < height calculate and increase img height
            heightFactor = imgSize / width
            heightCalc = math.ceil(heightFactor * height)
            imgResize = cv2.resize(imgCrop, (imgSize, heightCalc))
            imgResizeShape = imgResize.shape

            # calculate gap to get the value to center img horizontally
            heightGap = math.ceil((img.size - heightCalc) / 2)

            # put the imgResize in a limited area of imgWhite and center img
            imgWhite[heightGap:heightCalc + heightGap, :] = imgResize

        cv2.imshow("ImageCrop", imgCrop)
        cv2.imshow("ImageWhite", imgWhite)
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    # save img on pressing "s" key
    if key == ord("s"):
        counter += 1
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', imgWhite)
        print(counter)
