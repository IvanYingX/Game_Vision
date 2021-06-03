import cv2
import mediapipe as mp
import time
import numpy as np

class HandTracking:
    def __init__(self, mode=False, hands=2, detect_conf=0.5, tracking_conf=0.5):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(mode, hands, detect_conf, tracking_conf)
        self.mpDraw = mp.solutions.drawing_utils

    def detect_hand(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLMs in results.multi_hand_landmarks:
                if draw:  
                    self.mpDraw.draw_landmarks(img,
                                           handLMs,
                                           self.mpHands.HAND_CONNECTIONS)
        return img

    def identify_point(self, img, point=0, hand=0):
        h, w, c = img.shape
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        lm_list = []
        if results.multi_hand_landmarks:
            my_hand = results.multi_hand_landmarks[hand]
            lm = my_hand.landmark[point]
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list = [cx, cy]
            cv2.circle(img, (lm_list[0], lm_list[1]),
                   10, (255, 0, 255), cv2.FILLED)
        return lm_list
    
    def get_positions(self, img, hand=0):
        h, w, c = img.shape
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        lm_list = []
        if results.multi_hand_landmarks:
            hand_lm = results.multi_hand_landmarks[hand]
            for id, lm in enumerate(hand_lm.landmark):
                cx, cy, cz = int(lm.x * w), int(lm.y * h), int(lm.z * 500)
                lm_list.append([id, cx, cy, cz])
        return lm_list
    
    def fingers_up(self, img, lm_list, letters=False):
        fingers = [0] * 5
        wrist = np.array([lm_list[0][1], lm_list[0][2], lm_list[0][3]])
        index_tip = np.array([lm_list[8][1], lm_list[8][2], lm_list[8][3]])
        index_pip = np.array([lm_list[6][1], lm_list[6][2], lm_list[6][3]])
        middle_tip = np.array([lm_list[12][1], lm_list[12][2], lm_list[12][3]])
        middle_pip = np.array([lm_list[10][1], lm_list[10][2], lm_list[10][3]])
        ring_tip = np.array([lm_list[16][1], lm_list[16][2], lm_list[16][3]])
        ring_pip = np.array([lm_list[14][1], lm_list[14][2], lm_list[14][3]])
        pinky_tip = np.array([lm_list[20][1], lm_list[20][2], lm_list[20][3]])
        pinky_pip = np.array([lm_list[18][1], lm_list[18][2], lm_list[18][3]])
        thumb_tip = np.array([lm_list[4][1], lm_list[4][2], lm_list[4][3]])
        thumb_pip = np.array([lm_list[3][1], lm_list[3][2], lm_list[2][3]])
        
        distance_it = np.sqrt(np.sum((index_tip - wrist)**2))
        distance_ip = np.sqrt(np.sum((index_pip - wrist)**2))
        distance_mt = np.sqrt(np.sum((middle_tip - wrist)**2))
        distance_mp = np.sqrt(np.sum((middle_pip - wrist)**2))
        distance_rt = np.sqrt(np.sum((ring_tip - wrist)**2))
        distance_rp = np.sqrt(np.sum((ring_pip - wrist)**2))
        distance_pt = np.sqrt(np.sum((pinky_tip - wrist)**2))
        distance_pp = np.sqrt(np.sum((pinky_pip - wrist)**2))
        distance_tt = np.sqrt(np.sum((thumb_tip - wrist)**2))
        distance_tp = np.sqrt(np.sum((thumb_pip - wrist)**2))
            
    
        if distance_it - distance_ip > 50:
            if letters:
                cv2.putText(img, 'O',
                            (index_tip[0], index_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (255, 0, 0), 2)
            fingers[1] = 1
        else:
            if letters:
                cv2.putText(img, 'C',
                            (index_tip[0], index_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 150), 2)
            fingers[1] = 0
        if distance_mt - distance_mp > 50:
            if letters:
                cv2.putText(img, 'O',
                            (middle_tip[0], middle_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (255, 0, 0), 2)
            fingers[2] = 1
        else:
            if letters:
                cv2.putText(img, 'C',
                            (middle_tip[0], middle_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 150), 2)
            fingers[2] = 0
        if distance_rt - distance_rp > 30:
            if letters:
                cv2.putText(img, 'O',
                            (ring_tip[0], ring_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (255, 0, 0), 2)
            fingers[3] = 1
        else:
            if letters:
                cv2.putText(img, 'C',
                            (ring_tip[0], ring_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 150), 2)
            fingers[3] = 0
        if distance_pt - distance_pp > 50:
            if letters:
                cv2.putText(img, 'O',
                            (pinky_tip[0], pinky_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (255, 0, 0), 2)
            fingers[4] = 1
        else:
            if letters:
                cv2.putText(img, 'C',
                            (pinky_tip[0], pinky_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 150), 2)
            fingers[4] = 0
        if distance_tt - distance_tp > 20:
            if letters:
                cv2.putText(img, 'O',
                            (thumb_tip[0], thumb_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (255, 0, 0), 2)
            fingers[0] = 1
        else:
            if letters:
                cv2.putText(img, 'C',
                            (thumb_tip[0], thumb_tip[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 150), 2)
            fingers[0] = 0
        cv2.circle(img, (wrist[0], wrist[1]), 15, (0, 0, 150), cv2.FILLED)
        return fingers