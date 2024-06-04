import cv2
import mediapipe as mp
import math
import json
import pyautogui
from time import sleep

from utils.Hand import Hand

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize the face mesh
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

previous_actions = []

while True:
    debug = True
    # Read each frame from the webcam
    _, frame = cap.read()
    x, y, c = frame.shape

    frame = cv2.flip(frame, 1)

    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get face landmark prediction
    output = face_mesh.process(framergb)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    if landmark_points:
        landmarks = landmark_points[0].landmark
        for id, landmark in enumerate(landmarks[474:478]):

            if debug:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))

            if id == 1:
                screen_x = screen_w * landmark.x
                screen_y = screen_h * landmark.y

                pyautogui.moveTo(screen_x, screen_y)
        left = [landmarks[145], landmarks[159]]

        if debug:
            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))
        # if (left[0].y - left[1].y) < 0.004:
        #     pyautogui.click()

    # Get hand landmark prediction
    result = hands.process(framergb)

     # Padrão do debug False
    details = None
    # if debug:
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
            # points = mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)
            points = None

            hand = Hand(frame, points, real_coordinates, previous_actions, details)
            hand.update()



    # Show the final output
    cv2.imshow("Output", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()