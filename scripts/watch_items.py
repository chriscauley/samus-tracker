import setup
import cv2
from inputs import get_gamepad, UnknownEventCode
import numpy as np
from mss import mss
from pathlib import Path
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import json
import time
import urcv
import sys

from models import Playthrough, Template

# define dimensions of screen w.r.t to given monitor to be captured
GAME_LEFT = 724 # min width of chrome window!
SCREEN_WIDTH = 1920
GAME_TOP = 64
GAME_HEIGHT = 960 - GAME_TOP # Taken from screenshot
GAME_WIDTH = SCREEN_WIDTH-GAME_LEFT
frames = []
options = {
    'left': GAME_LEFT,
    'width': GAME_WIDTH,
    'top': GAME_TOP,
    'height': GAME_HEIGHT,
}
frame_times = [time.time()]

_template = 'super-metroid'
for i, arg in enumerate(sys.argv):
    if arg == '-t':
        _template = sys.argv[i+1]
print('using template', _template)

with mss() as sct:
    scale = 0.5
    frame_count = 1
    template = Template(_template)
    playthrough = Playthrough(sys.argv[1])
    capture_rate = int(1000 / playthrough.data['fps'])
    print('starting in 1 sec; delay=', capture_rate)
    time.sleep(1) # a little delay for switching windows

    while True:
        now = time.time()

        screenShot = sct.grab(options)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mini = urcv.transform.scale(frame, scale, interpolation=cv2.INTER_LINEAR)
        gray_mini = cv2.cvtColor(mini, cv2.COLOR_RGB2GRAY)

        frames.append(time.time())
        frames = [f for f in frames if f > time.time() - 5]

        item_name, coords = template.search(gray_mini, 'item')
        playthrough.touch(item_name)
        playthrough.save_frame(mini)
        frame_count += 1
        for x1, y1, x2, y2 in coords:
            cv2.rectangle(mini, [x1, y1], [x2, y2], (255,0,0), 3)
            urcv.text.write(mini, item_name)
        if not coords:
            text = f'last: {playthrough.last}'
            if playthrough.is_last_duplicate():
                text += ' DUPLICATED'
            else:
                text += f' {len(playthrough.data["item_names"])}'
            dt = len(frames) / (time.time() - frame_times[0])
            text += f'  {round(dt,1)} fps'
            urcv.text.write(mini, text)
        frame_times.append(time.time())
        frame_times = frame_times[-20:]

        cv2.imshow('mini', mini)
        # cv2.imshow('gray_mini', gray_mini)
        delay = int(capture_rate - (time.time() * 1000) % capture_rate)
        print(delay)
        pressed = urcv.wait_key(max_time=1, delay=delay)
        if pressed == 'q':
            break
        if pressed == 'i':
            template.save_from_frame(mini)
        if pressed == 'd':
            playthrough.mark_duplicate()
