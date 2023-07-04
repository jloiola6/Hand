import cv2
import mediapipe as mp
import math
import json
import pyautogui

from utils.Hand import Hand

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read each frame from the webcam
    _, frame = cap.read()
    x, y, c = frame.shape

    frame = cv2.flip(frame, 1)

    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get hand landmark prediction
    result = hands.process(framergb)

    debug = False # Padrão do debug False
    details = None 
    if debug:
        details = cv2.rectangle(frame, (25, 25), (250, 250), (0, 0, 0), -1)

    # post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        real_coordinates = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)
                lmz = float(lm.z)
                landmarks.append([lmx, lmy])
                real_coordinates.append((lmx, lmy, lmz))

            # Drawing landmarks on frames
            points = mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)
            # points = None

            Hand(frame, points, real_coordinates, details)


    # Show the final output
    cv2.imshow("Output", frame) 

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()