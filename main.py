import pygame
import mediapipe as mp
from pygame.locals import *
import cv2
import numpy as np
import autopy
from HandTracking import HandTracking

pygame.init()
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap.set(3, 600)
# cap.set(4, 800)

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Game Vision')
icon = pygame.image.load('camera.png')
pygame.display.set_icon(icon)

hand = HandTracking(hands=1, detect_conf=0.7, tracking_conf=0.8)
# mpHands = mp.solutions.hands
# hands = mpHands.Hands()
# mpDraw = mp.solutions.drawing_utils

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            print(pos)
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = hand.detect_hand(img)
    lm_list = hand.get_positions(img)
    if lm_list:
        cv2.circle(img, (lm_list[8][1], lm_list[8][2]), 15, (0, 0, 150), cv2.FILLED)
        print(lm_list)
    # results = hands.process(img)

    # if results.multi_hand_landmarks:
    #         for handLMs in results.multi_hand_landmarks:
    #             mpDraw.draw_landmarks(img,
    #                                   handLMs,
    #                                   mpHands.HAND_CONNECTIONS)

    size = img.shape[1::-1]
    img = pygame.image.frombuffer(img.flatten(), size, 'RGB')
    screen.blit(img, (0, 0))
    pygame.display.update()
pygame.quit()