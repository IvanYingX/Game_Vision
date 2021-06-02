import pygame
import mediapipe as mp
from pygame.locals import *
import cv2
import numpy
import autopy

pygame.init()
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap.set(3, 600)
# cap.set(4, 800)

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Game Vision')
icon = pygame.image.load('camera.png')
pygame.display.set_icon(icon)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    success, img = cap.read()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)

    if results.multi_hand_landmarks:
            for handLMs in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img,
                                      handLMs,
                                      mpHands.HAND_CONNECTIONS)

    size = img.shape[1::-1]
    img = pygame.image.frombuffer(img.flatten(), size, 'RGB')
    screen.blit(img, (0, 0))
    pygame.display.update()
pygame.quit()