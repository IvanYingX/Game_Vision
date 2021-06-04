import autopy
from HandTracking import HandTracking
import cv2
import numpy as np
import time 

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
wCam = 1280
hCam = 720
rectangle = 200
smooth = 12

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap.set(3, wCam)
cap.set(4, hCam)
count = 0
hand = HandTracking(hands=1, detect_conf=0.7)
wScr, hScr = autopy.screen.size()
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = hand.detect_hand(img)
    lm_list = hand.get_positions(img)
    if lm_list:
        
        x1, y1 = lm_list[8][1:3]
        x2, y2 = lm_list[12][1:3]
        fingers = hand.fingers_up(img, lm_list)
        if fingers[1] == 1 and fingers[2] == 0:
            count = 0
            # Convert Coordinates
            x3 = np.interp(x1, (rectangle, wCam - rectangle), (0, wScr))
            y3 = np.interp(y1, (rectangle, hCam - rectangle), (0, hScr))
            # Smooth Values
            clocX = plocX + (x3 - plocX) / smooth
            clocY = plocY + (y3 - plocY) / smooth

            # Move q
            autopy.mouse.move(clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
            plocX, plocY = clocX, clocY
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
            print(fingers)
            cv2.putText(img, 'Quitting', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            count += 1
            if count >= 60:
                break
        elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1:
            print(fingers)
            count = 0
            index = np.array(lm_list[8][1:3])
            middle = np.array(lm_list[12][1:3])
            distance = np.sqrt(np.sum((index - middle) ** 2))
            if distance < 40:
                cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                autopy.mouse.click()

    cv2.imshow('Image', img)
    if cv2.waitKey(1) == ord('q'):
        break