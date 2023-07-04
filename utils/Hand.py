import cv2
import mediapipe as mp
import math
import json
import pyautogui
from time import sleep
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class Hand():
    def __init__(self, frame, points, real_coordinates, details=None) -> None:
        try:
            self.details = details
            self.hand = 1
            qtd_hand = len(real_coordinates) > 21
            for item in range(0, len(real_coordinates), 21):
                if self.hand == 1:
                    coordinates = real_coordinates[:21]
                # else:
                #     coordinates = real_coordinates[21:]

                self.direction = self.calculate_direction(coordinates)
                self.palm = self.calculate_palm(coordinates, self.direction)
                self.down = self.calculate_isdown(coordinates, self.direction, self.palm)
                self.together = self.calculate_together(coordinates)
                self.action = self.calculate_gest(self.down, self.together, self.direction)


                # Controlar pc futuramente
                if self.action == 'OK!':
                    self.controlMouse(frame, real_coordinates)
                elif self.calculate_gest(self.down, self.together, self.direction) == 'Legal':
                    pyautogui.click()
                    sleep(0.5)

                # if True:
                #     distance = round(math.dist(real_coordinates[4], real_coordinates[8]), 2) - 10
                #     valor = (distance * 100) // 150
                #     self.set_volume_percentage(valor)
                    

                if self.details != None:
                    self.debug()

                # self.hand += 1
        except:
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

            cv2.putText(self.details, f'Action: {self.action}', (30, 130), cv2.FONT_HERSHEY_PLAIN, 0.5, (255, 0, 0), 1)

        elif self.hand == 2:
            cv2.putText(self.details, f'Mão {self.hand}', (30, 150), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'down: {self.down}', (30, 165), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'together: {self.together}', (30, 180), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'palm: {self.palm}', (30, 195), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)
            cv2.putText(self.details, f'direction: {self.direction}', (30, 210), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 0, 255), 1)

            self.action = self.calculate_gest(self.down, self.together, self.direction)

            cv2.putText(self.details, f'Action: {self.action}', (30, 225), cv2.FONT_HERSHEY_PLAIN, 0.5, (255, 0, 0), 1)


    def calculate_palm(self, real_coordinates, direction):
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


    def calculate_together(self, real_coordinates):
        distance_0 = round(math.dist(real_coordinates[4], real_coordinates[8]), 2)
        distance_1 = round(math.dist(real_coordinates[8], real_coordinates[12]), 2)
        distance_2 = round(math.dist(real_coordinates[12], real_coordinates[16]), 2)
        distance_3 = round(math.dist(real_coordinates[16], real_coordinates[20]), 2)

        together_0 = 1 if distance_0 > 25 else 0 # 1 significa que esta aberto e 0 fechado
        together_1 = 1 if distance_1 > 35 else 0 # 1 significa que esta aberto e 0 fechado
        together_2 = 1 if distance_2 > 22 else 0 # 1 significa que esta aberto e 0 fechado
        together_3 = 1 if distance_3 > 42 else 0 # 1 significa que esta aberto e 0 fechado

        return [together_0, together_1, together_2, together_3]


    def angle_between_points(self, coordinates):
        x1 = coordinates[0][0]
        y1 = coordinates[0][1]
        x2 = coordinates[9][0]
        y2 = coordinates[9][1]

        angle_rad = math.atan2(y2-y1, x2-x1)

        angle_deg = math.degrees(angle_rad) * -1

        return angle_deg


    def calculate_direction(self, coordinates):
        angle_deg = self.angle_between_points(coordinates)
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
        distance_0, distance_1, distance_2, distance_3, distance_4 = self.calculate_distance(real_coordinates, direction, palm)

        down_0 = 1 if distance_0 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
        down_1 = 1 if distance_1 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
        down_2 = 1 if distance_2 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
        down_3 = 1 if distance_3 < 0 else 0  # 1 significa que esta esticado e 0 encolhido
        down_4 = 1 if distance_4 < 0 else 0  # 1 significa que esta esticado e 0 encolhido

        # return [distance_0, distance_1, distance_2, distance_3, distance_4]
        return [down_0, down_1, down_2, down_3, down_4]


    def calculate_gest(self, down, together, direction):
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