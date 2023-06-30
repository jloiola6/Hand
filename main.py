import cv2
import mediapipe as mp
import math
import json
import pyautogui


def calculate_palm(real_coordinates, direction):
    if direction == 'Up':
        palm = 'Frente' if real_coordinates[1][0] < real_coordinates[0][0] else 'Costa'
    elif direction == 'Right':
        palm = 'Frente' if real_coordinates[1][1] < real_coordinates[0][1] else 'Costa'
    elif direction == 'Down':
        palm = 'Frente' if real_coordinates[1][0] > real_coordinates[0][0] else 'Costa'
    elif direction == 'Left':
        palm = 'Frente' if real_coordinates[1][1] > real_coordinates[0][1] else 'Costa'
    else:
        palm = 'ERROR!'

    return palm


def calculate_together(real_coordinates):
    distance_0 = round(math.dist(real_coordinates[4], real_coordinates[8]), 2)
    distance_1 = round(math.dist(real_coordinates[8], real_coordinates[12]), 2)
    distance_2 = round(math.dist(real_coordinates[12], real_coordinates[16]), 2)
    distance_3 = round(math.dist(real_coordinates[16], real_coordinates[20]), 2)

    together_0 = 1 if distance_0 > 25 else 0 # 1 significa que esta aberto e 0 fechado
    together_1 = 1 if distance_1 > 35 else 0 # 1 significa que esta aberto e 0 fechado
    together_2 = 1 if distance_2 > 22 else 0 # 1 significa que esta aberto e 0 fechado
    together_3 = 1 if distance_3 > 42 else 0 # 1 significa que esta aberto e 0 fechado

    return [together_0, together_1, together_2, together_3]


def angle_between_points(coordinates):
    x1 = coordinates[0][0]
    y1 = coordinates[0][1]
    x2 = coordinates[9][0]
    y2 = coordinates[9][1]

    angle_rad = math.atan2(y2-y1, x2-x1)

    angle_deg = math.degrees(angle_rad) * -1

    return angle_deg


def calculate_direction(coordinates):
    angle_deg = angle_between_points(coordinates)
    # return angle_deg

    if 130 > angle_deg > 60:
        return "Up"
    elif 60 > angle_deg > -50:
        return "Right"
    elif -50 > angle_deg > -140:
        return "Down"
    elif -140 < angle_deg > 130:
        return "Left"
    else:
        return "nenhuma das anteriores"


def calculate_distance(real_coordinates, direction, palm):
    if direction == 'Up':
        if palm == 'Frente':
            distance_0 = real_coordinates[4][0] - real_coordinates[3][0]
        else:
            distance_0 = real_coordinates[3][0] - real_coordinates[4][0]

        distance_1 = real_coordinates[8][1] - real_coordinates[7][1]
        distance_2 = real_coordinates[12][1] - real_coordinates[11][1]
        distance_3 = real_coordinates[16][1] - real_coordinates[15][1]
        distance_4 = real_coordinates[20][1] - real_coordinates[19][1]

    elif direction == 'Right':
        if palm == 'Frente':
            distance_0 = (real_coordinates[4][1] - real_coordinates[3][1])
        else:
            distance_0 = (real_coordinates[3][1] - real_coordinates[4][1])

        distance_1 = (real_coordinates[8][0] - real_coordinates[7][0]) * -1
        distance_2 = (real_coordinates[12][0] - real_coordinates[11][0]) * -1
        distance_3 = (real_coordinates[16][0] - real_coordinates[15][0]) * -1
        distance_4 = (real_coordinates[20][0] - real_coordinates[19][0]) * -1

    elif direction == 'Down':
        if palm == 'Frente':
            distance_0 = real_coordinates[3][0] - real_coordinates[4][0]
        else:
            distance_0 = real_coordinates[4][0] - real_coordinates[3][0]

        distance_1 = real_coordinates[7][1] - real_coordinates[8][1]
        distance_2 = real_coordinates[11][1] - real_coordinates[12][1]
        distance_3 = real_coordinates[15][1] - real_coordinates[16][1]
        distance_4 = real_coordinates[19][1] - real_coordinates[20][1]

    elif direction == 'Left':
        if palm == 'Frente':
            distance_0 = real_coordinates[3][1] - real_coordinates[4][1]
        else:
            distance_0 = real_coordinates[4][1] - real_coordinates[3][1]

        distance_1 = (real_coordinates[7][0] - real_coordinates[8][0]) * -1
        distance_2 = (real_coordinates[11][0] - real_coordinates[12][0]) * -1
        distance_3 = (real_coordinates[15][0] - real_coordinates[16][0]) * -1
        distance_4 = (real_coordinates[19][0] - real_coordinates[20][0]) * -1

    else:
        distance_0 = distance_1 = distance_2 = distance_3 = distance_4 = 0


    return distance_0, distance_1, distance_2, distance_3, distance_4


def calculate_isdown(real_coordinates, direction, palm):
    distance_0, distance_1, distance_2, distance_3, distance_4 = calculate_distance(real_coordinates, direction, palm)

    down_0 = 1 if distance_0 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
    down_1 = 1 if distance_1 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
    down_2 = 1 if distance_2 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
    down_3 = 1 if distance_3 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
    down_4 = 1 if distance_4 < 0 else 0  # 1 significa que esta esticado e 0 encolhido

    # return [distance_0, distance_1, distance_2, distance_3, distance_4]
    return [down_0, down_1, down_2, down_3, down_4]


def calculate_gest(down, together, direction):
    with open("model.json") as f:
        data = json.load(f)

    gests = []
    gests_1 = []
    gest_2 = []
    valor = '[]'

    for i in data:
        if i['down'] == down:
            gests.append(i)

    if len(gests) == 1:
        valor = gests[0]['action']

    elif len(gests) > 1:
        for i in gests:
            if direction in i['direction']:
                gests_1.append(i)

        if len(gests_1) > 1:
            for i in gests_1:
                if i['together'] == together:
                    gest_2.append(i)

            if not gest_2:
                for i in gests_1:
                    if i['together'] == None:
                        gest_2.append(i)

            if len(gest_2) == 1:
                valor = gest_2[0]['action']
            else:
                return_list = []
                for i in gest_2:
                    return_list.append(i['action'])

                valor = return_list

        elif len(gests_1) == 1:
            valor = gests_1[0]['action']
        else:
            return_list = []
            for i in gests_1:
                return_list.append(i['action'])

            valor = return_list

    return valor

def controlPc(frame, real_coordinates):
    frame1_width, frame1_height, z = frame.shape
    frame2_width, frame2_height = pyautogui.size()

    frame1_x = real_coordinates[4][0]
    frame1_y = real_coordinates[4][1] 

    frame2_x = int((frame1_x-frame1_width/2) * frame2_width / (frame1_width/2))
    frame2_y = int((frame1_y-frame1_height/2) * frame2_height / (frame1_height/2))

    pyautogui.moveTo(frame2_x, frame2_y)


def load_fingers(frame, details, points, real_coordinates):
    try:
        hand = 1
        qtd_hand = len(real_coordinates) > 21
        for item in range(0, len(real_coordinates), 21):
            if hand == 1:
                coordinates = real_coordinates[:21]
            else:
                coordinates = real_coordinates[21:]

            direction = calculate_direction(coordinates)
            palm = calculate_palm(coordinates, direction)
            down = calculate_isdown(coordinates, direction, palm)
            together = calculate_together(coordinates)

            # Controlar pc futuramente
            # action = calculate_gest(down, together, direction)
            # if action == 'OK!':
            #     controlPc(frame, real_coordinates)

            #Mostrar dados do status da mão
            if hand == 1:
                cv2.putText(details, f'Mão {hand}', (30, 50), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'down: {down}', (30, 65), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'together: {together}', (30, 80), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'palm: {palm}', (30, 95), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'direction: {direction}', (30, 110), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)

                action = calculate_gest(down, together, direction)

                cv2.putText(details, f'Action: {action}', (30, 130), cv2.FONT_HERSHEY_PLAIN, 0.5, (255, 0, 0), 1)

            elif hand == 2:
                cv2.putText(details, f'Mão {hand}', (30, 150), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'down: {down}', (30, 165), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'together: {together}', (30, 180), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'palm: {palm}', (30, 195), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
                cv2.putText(details, f'direction: {direction}', (30, 210), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)

                action = calculate_gest(down, together, direction)

                cv2.putText(details, f'Action: {action}', (30, 225), cv2.FONT_HERSHEY_PLAIN, 0.5, (255, 0, 0), 1)

            hand += 1
    except:
        pass



# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7)
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

            load_fingers(frame, details, points, real_coordinates)


    # Show the final output
    cv2.imshow("Output", frame) 

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()