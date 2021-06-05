import mediapipe as mp
from pygame.locals import *
import cv2
import numpy as np
import autopy
from HandTracking import HandTracking
import random
import os
import pygame as pg

# game constants
MAX_SHOTS = 2  # most player bullets onscreen
ALIEN_ODDS = 22  # chances a new alien appears
BOMB_ODDS = 60  # chances a new bomb will drop
ALIEN_RELOAD = 20  # frames between new aliens
SCREENRECT = pg.Rect(0, 0, 640, 480)
SCORE = 0

main_dir = os.path.split(os.path.abspath(__file__))[0]
print(main_dir)

def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()


class Alien(pg.sprite.Sprite):
    """ An alien space ship. That slowly moves down the screen.
    """

    speed = 20
    animcycle = 12
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % 3]

class Shot(pg.sprite.Sprite):
    """ a bullet the Player sprite fires.
    """
    images = []
    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.movex = pos[0] # move along X
        self.movey = pos[1] # move along Y
        self.frame = 0 # count frames
        self.image = self.images[0]
        self.rect = self.image.get_rect()
    def control(self, x, y):
        self.movex = x
        self.movey = y
    def update(self):
        """
        Update sprite position
        """
        self.rect.x = self.movex 
        self.rect.y = self.movey      


class Explosion(pg.sprite.Sprite):
    """ An explosion. Hopefully the Alien and not the player!
    """

    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        """ called every time around the game loop.
        Show the explosion surface for 'defaultlife'.
        Every game tick(update), we decrease the 'life'.
        Also we animate the explosion.
        """
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()

class Score(pg.sprite.Sprite):
    """ to keep track of the score.
    """

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.font = pg.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = pg.Color("white")
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self):
        """ We only update the score in update() when it has changed.
        """
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)


def main(winstyle=0):
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    # img = load_image("player1.gif")
    # Player.images = [img, pg.transform.flip(img, 1, 0)]
    img = load_image("explosion1.gif")
    Explosion.images = [img, pg.transform.flip(img, 1, 1)]
    Alien.images = [load_image(im) for im in ("alien1.gif", "alien2.gif", "alien3.gif")]
    Shot.images = [load_image("shot.gif")]
    # decorate the game window
    icon = pg.transform.scale(Alien.images[0], (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Aliens")
    pg.mouse.set_visible(0)

    hand = HandTracking(hands=1, detect_conf=0.7, tracking_conf=0.7)
    # Initialize Game Groups
    aliens = pg.sprite.Group()
    shots = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()
    lastalien = pg.sprite.GroupSingle()

    # assign default groups to each sprite class
    Alien.containers = aliens, all, lastalien
    Shot.containers = shots, all
    Explosion.containers = all
    Score.containers = all

    # Create Some Starting Values
    global score
    alienreload = ALIEN_RELOAD
    clock = pg.time.Clock()

    # initialize our starting sprites
    global SCORE
    bullet = Shot((300,200))
    Alien()  # note, this 'lives' because it goes into a sprite group
    if pg.font:
        all.add(Score())
    while True:

        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    if not fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    pg.display.flip()
                    fullscreen = not fullscreen
        _, img =  cap.read()
        img = cv2.flip(img, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = hand.detect_hand(img)
        lm_list = hand.get_positions(img)
        if lm_list:
            cv2.circle(img, (lm_list[8][1], lm_list[8][2]), 15, (0, 0, 150), cv2.FILLED)
            bullet.control(lm_list[8][1], lm_list[8][2])

            # print(lm_list)
        size = img.shape[1::-1]
        img = pg.image.frombuffer(img.flatten(), size, 'RGB')
        # update all the sprites

        # Create new alien
        if alienreload:
            alienreload = alienreload - 1
        elif not int(random.random() * ALIEN_ODDS):
            Alien()
            alienreload = ALIEN_RELOAD
        # See if shots hit the aliens.
        for alien in pg.sprite.groupcollide(aliens, shots, 1, 0).keys():
            # if pg.mixer:
            #     boom_sound.play()
            Explosion(alien)
            SCORE = SCORE + 1

        # draw the scene
        # all.clear(screen, img)
        all.update()
        screen.blit(img, (0, 0))
        pg.display.update()
        dirty = all.draw(screen)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        clock.tick(40)

    # if pg.mixer:
    #     pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)
    pg.quit()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
# pg.init()
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# # cap.set(3, 600)
# # cap.set(4, 800)

# screen = pg.display.set_mode((640, 480))
# pg.display.set_caption('Game Vision')
# icon = pg.image.load('camera.png')
# pg.display.set_icon(icon)

# hand = HandTracking(hands=1, detect_conf=0.7, tracking_conf=0.8)
# # mpHands = mp.solutions.hands
# # hands = mpHands.Hands()
# # mpDraw = mp.solutions.drawing_utils

# running = True
# while running:
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             running = False
#         if event.type == pg.MOUSEBUTTONUP:
#             pos = pg.mouse.get_pos()
#             print(pos)
#     success, img = cap.read()
#     img = cv2.flip(img, 1)
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     img = hand.detect_hand(img)
#     lm_list = hand.get_positions(img)
#     if lm_list:
#         cv2.circle(img, (lm_list[8][1], lm_list[8][2]), 15, (0, 0, 150), cv2.FILLED)
#         print(lm_list)
#     # results = hands.process(img)

#     # if results.multi_hand_landmarks:
#     #         for handLMs in results.multi_hand_landmarks:
#     #             mpDraw.draw_landmarks(img,
#     #                                   handLMs,
#     #                                   mpHands.HAND_CONNECTIONS)

#     size = img.shape[1::-1]
#     img = pg.image.frombuffer(img.flatten(), size, 'RGB')
#     screen.blit(img, (0, 0))
#     pg.display.update()
# pg.quit()