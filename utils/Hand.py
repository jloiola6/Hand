import cv2
import mediapipe as mp
import math
import json
import pyautogui
from time import sleep
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class Hand():
    def __init__(self, frame, points, real_coordinates, previous_actions, details=None) -> None:
        try:
            self.previous_actions = previous_actions
            self.details = details
            # total number of hands detected based on landmark count
            self.hand = 2 if len(real_coordinates) > 21 else 1

            self.directions = {
                'Up': lambda: 'Frente' if real_coordinates[1][0] < real_coordinates[0][0] else 'Costa',
                'Right': lambda: 'Frente' if real_coordinates[1][1] < real_coordinates[0][1] else 'Costa',
                'Down': lambda: 'Frente' if real_coordinates[1][0] > real_coordinates[0][0] else 'Costa',
                'Left': lambda: 'Frente' if real_coordinates[1][1] > real_coordinates[0][1] else 'Costa'
            }

            with open("sequence.json") as f:
                self.sequence_data = json.load(f)

            with open("model.json") as f:
                self.data = json.load(f)
            self.cache = {}


            for item in range(0, len(real_coordinates), 21):
                # slice the landmarks for each detected hand
                coordinates = real_coordinates[item:item + 21]
                self.hand = item // 21 + 1

                self.direction = self.calculate_direction(coordinates)
                self.palm = self.calculate_palm(self.direction)
                self.down = self.calculate_isdown(coordinates, self.direction, self.palm)
                self.together = self.calculate_together(coordinates)
                self.action = self.calculate_gest(self.down, self.together, self.direction)


                # Controlar pc futuramente
                # if self.action == 'OK!':
                #     self.controlMouse(frame, real_coordinates)
                #     pyautogui.click()
                # elif self.calculate_gest(self.down, self.together, self.direction) == 'OK!' and self.hand == 2:
                #     pyautogui.click()
                #     sleep(0.5)

                # if True:
                #     distance = round(math.dist(real_coordinates[4], real_coordinates[8]), 2) - 10
                #     valor = (distance * 100) // 150
                #     self.set_volume_percentage(valor)


                if self.details is not None:
                    # ensure debug data is drawn only when a debug frame is provided
                    if hasattr(self.details, "any"):
                        if self.details.any():
                            self.debug()
                    else:
                        self.debug()

                self.hand += 1
        except Exception as e:
            print(f"ERROR -> {e}")
            pass


    def debug(self):
        #Mostrar dados do status da mão
        if self.hand == 1:
            cv2.putText(self.details, f'Mão {self.hand}', (30, 50), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'down: {self.down}', (30, 65), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'together: {self.together}', (30, 80), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'palm: {self.palm}', (30, 95), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'direction: {self.direction}', (30, 110), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)

            self.action = self.calculate_gest(self.down, self.together, self.direction)

            cv2.putText(self.details, f'Action: {self.action}', (30, 130), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)

        elif self.hand == 2:
            cv2.putText(self.details, f'Mão {self.hand}', (30, 150), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'down: {self.down}', (30, 165), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'together: {self.together}', (30, 180), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'palm: {self.palm}', (30, 195), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'direction: {self.direction}', (30, 210), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)

            self.action = self.calculate_gest(self.down, self.together, self.direction)

            cv2.putText(self.details, f'Action: {self.action}', (30, 225), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)


    def calculate_palm(self, direction):
        try:
            return self.directions[direction]()
        except:
            raise ValueError(f"Direction '{direction}' is not recognized.")

    def calculate_together(self, real_coordinates):
        together = []
        thresholds = [25, 35, 22, 42]

        for i in range(4):
            distance = round(math.dist(real_coordinates[4 + i * 4], real_coordinates[8 + i * 4]), 2)
            together.append(1 if distance > thresholds[i] else 0)  # 1 significa que esta aberto e 0 fechado

        return together


    def angle_between_points(self, coordinates):
        # Verificar se as coordenadas são válidas
        if not coordinates or len(coordinates) < 10:
            raise ValueError("Invalid coordinates")

        # Obter as coordenadas x e y dos pontos
        x1, y1 = coordinates[0][0], coordinates[0][1]
        x2, y2 = coordinates[9][0], coordinates[9][1]

        # Calcular o ângulo em radianos entre os dois pontos
        angle_rad = math.atan2(y2 - y1, x2 - x1)

        # Converter o ângulo para graus e inverter o sinal
        angle_deg = -math.degrees(angle_rad)

        return angle_deg


    def calculate_direction(self, coordinates):
        angle_deg = self.angle_between_points(coordinates)

        # Dicionário para mapear intervalos de ângulos para direções
        directions = {
            "Up": range(60, 131),
            "Right": range(-50, 61),
            "Down": range(-140, -49),
            "Left": range(130, -141, -1)
        }

        # Verificar em qual intervalo o ângulo se encontra
        for direction, angle_range in directions.items():
            if int(angle_deg) in angle_range:
                return direction

        return "nenhuma das anteriores"



    def calculate_distance(self, real_coordinates, direction, palm):
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


    def calculate_isdown(self, real_coordinates, direction, palm):
        distances = self.calculate_distance(real_coordinates, direction, palm)
        down = [1 if distance < 0 else 0 for distance in distances]  # 1 significa que esta esticado e 0 encolhido
        if self.hand == 2:
            down[0] = 0 if down[0] == 1 else 1

        return down

    def calculate_gest(self, down, together, direction):
        cache_key = (tuple(down), tuple(together), direction)
        if cache_key in self.cache:
            return self.cache[cache_key]

        gests = []
        gests_1 = []
        gest_2 = []
        valor = '[]'

        for i in self.data:
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

        self.cache[cache_key] = valor
        return valor

    def check_gesture_sequence(self):
        # Verificar se a sequência de gestos ocorreu
        if len(self.previous_actions) >= 2:
            for i in self.sequence_data:
                qtd = len(i["sequence"])
                if self.previous_actions[-qtd:] == i["sequence"]:
                    print(f"Sequence detected: {i['action']}")
                    self.previous_actions = []
                    return i['action']

    def update(self):
        try:
            self.action = self.calculate_gest(self.down, self.together, self.direction)
            if self.previous_actions:
                if self.previous_actions[-1] != self.action:
                    self.previous_actions.append(self.action)
                    return self.check_gesture_sequence()
            else:
                self.previous_actions.append(self.action)
        except Exception as e:
            print(f"ERROR -> {e}")



    def controlMouse(self, frame, real_coordinates):
        # Coordenadas do retângulo do trackpad
        trackpad_x1 = 125
        trackpad_y1 = 125
        trackpad_x2 = 500
        trackpad_y2 = 400

        # Coordenadas do sistema de tela
        frame2_width, frame2_height = pyautogui.size()

        # Coordenadas da mão
        hand_x = real_coordinates[4][0] + trackpad_x1/2
        hand_y = real_coordinates[4][1]

        # Verificar se a mão está dentro do retângulo do trackpad
        if trackpad_x1 < hand_x < trackpad_x2 and trackpad_y1 < hand_y < trackpad_y2:
            # Calcular a posição relativa dentro do retângulo do trackpad
            trackpad_relative_x = hand_x - trackpad_x1
            trackpad_relative_y = hand_y - trackpad_y1

            # Calcular as coordenadas no sistema de tela
            frame2_x = int(trackpad_relative_x * frame2_width / (trackpad_x2 - trackpad_x1))
            frame2_y = int(trackpad_relative_y * frame2_height / (trackpad_y2 - trackpad_y1))

            # Mover o cursor do mouse
            pyautogui.moveTo(frame2_x, frame2_y)


    def set_volume_percentage(self, percentage):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(percentage / 100, None)