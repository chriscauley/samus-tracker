import cv2
import numpy as np
from mss import mss
from PIL import Image
import time
import urcv

# define dimensions of screen w.r.t to given monitor to be captured
GAME_LEFT = 500 # min width of chrome window!
SCREEN_WIDTH = 1920
GAME_HEIGHT = 1065 # Taken from screenshot
GAME_TOP = 99
GAME_WIDTH = SCREEN_WIDTH-GAME_LEFT
frames = []
options = {
    'left': GAME_LEFT,
    'width': GAME_WIDTH,
    'top': GAME_TOP,
    'height': GAME_HEIGHT,
}

with mss() as sct:
    last = None
    while True:
        now = time.time()

        screenShot = sct.grab(options)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        frame = np.array(img)
        mini_h = int(GAME_LEFT * GAME_HEIGHT / GAME_WIDTH)
        mini = cv2.resize(frame, (GAME_LEFT, mini_h))
        gray_mini = cv2.cvtColor(mini, cv2.COLOR_RGB2GRAY)
        frames.append(time.time())
        frames = [f for f in frames if f > time.time() - 5]
        if last is not None:
            frameDelta = cv2.absdiff(last, gray_mini)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            diff = cv2.bitwise_and(mini, mini, mask=thresh)
            urcv.text.write(diff, f'fps: {int(10*len(frames)/5)/10}')
            cv2.imshow('diff', diff)

        cv2.imshow('test', mini)
        pressed = urcv.wait_key(max_time=1, delay=33)
        if pressed == 'q':
            break
        last = gray_mini