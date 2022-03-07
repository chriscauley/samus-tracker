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

from models import Playthrough, Template, MotionDetector
from unrest.utils import time_it

# define dimensions of screen w.r.t to given monitor to be captured
GAME_LEFT = 724 # min width of chrome window!
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GAME_TOP = 64
GAME_HEIGHT = 960 - GAME_TOP # Taken from screenshot
GAME_WIDTH = SCREEN_WIDTH-GAME_LEFT
frames = []
options = {
    'left': GAME_LEFT,
    'width': GAME_WIDTH,
    'top': 0,
    'height': GAME_HEIGHT + GAME_TOP,
}
frame_times = [time.time()]

world = 'super-metroid'
for i, arg in enumerate(sys.argv):
    if arg == '-t':
        world = sys.argv[i+1]
print('using template', world)

def render_dict(data):
    img = np.zeros((400, 500), dtype=np.uint8)
    y = 0
    for i, (key, value) in enumerate(sorted(list(stats.items()))):
        _w, h = urcv.text.write(img, f'{key}: {value}', pos=(0, y))
        y += h + 5
    return img

def detect_stopped(capture, gray_mini):
    bar = cv2.cvtColor(capture[0:GAME_TOP], cv2.COLOR_BGR2GRAY)
    _, bar_coords = template.search(bar, 'ui', ['bar'])
    why_stopped = None
    if not bar_coords:
        return 'tabbed away'

    # pause icon is slightly smaller than this in top right corner
    top_right = gray_mini[0:100,-100:]
    _, pause_coords = template.search(top_right, 'ui', ['pause'])
    if pause_coords:
        return 'paused'


with mss() as sct:
    stats = { 'frame': 0 }
    scale = 0.5
    template = Template(world)
    playthrough = Playthrough(sys.argv[1], world=world)
    capture_rate = int(1000 / playthrough.data['fps'])
    print('starting in 1 sec; delay=', capture_rate)
    time.sleep(1) # a little delay for switching windows

    windows_set = False

    cv2.namedWindow('inventory')
    cv2.namedWindow('mini')
    cv2.namedWindow('stats')
    trex = MotionDetector()

    # @time_it
    def search_item(template, gray_mini):
        return template.search(gray_mini, 'item')

    def search_zone(template, gray_mini):
        cropped = doot # name error!
        return template.search(cropped, 'zone')
    while True:
        now = time.time()

        screenShot = sct.grab(options)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        capture = np.array(img)

        frame = capture[GAME_TOP:]
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mini = urcv.transform.scale(frame, scale, interpolation=cv2.INTER_LINEAR)
        gray_mini = cv2.cvtColor(mini, cv2.COLOR_RGB2GRAY)
        why_stopped = detect_stopped(capture, gray_frame)
        is_focused = not why_stopped
        if is_focused:
            playthrough.save_frame(mini)

        frames.append(time.time())
        frames = [f for f in frames if f > time.time() - 5]

        motion = trex.check(frame)[-1]
        if motion < 10 and is_focused:
            item_name, item_coords = search_item(template, gray_mini)
        else:
            item_name, item_coords = None, []
        playthrough.touch(item_name)
        for x1, y1, x2, y2 in item_coords:
            cv2.rectangle(mini, [x1, y1], [x2, y2], (255,0,0), 3)
            urcv.text.write(mini, item_name)

        frame_times.append(time.time())
        frame_times = frame_times[-20:]

        if is_focused:
            cv2.imshow('mini', mini)
        cv2.imshow('inventory', playthrough.get_inventory_image())
        stats = playthrough.get_stats({ 'state': why_stopped or 'focused' })
        cv2.imshow('stats', render_dict(stats))
        # cv2.imshow('gray_mini', gray_mini)
        delay = max(60, int(capture_rate - (time.time() * 1000) % capture_rate))
        pressed = urcv.wait_key(max_time=1, delay=delay)
        if pressed == 'q':
            break
        elif pressed == 'i':
            template.save_from_frame('item', mini)
        elif pressed == 'd':
            playthrough.mark_duplicate()
        elif pressed == 'z':
            template.save_from_frame('zone', mini)
        elif pressed == 'u':
            template.save_from_frame('ui', mini)
        elif pressed == 'b':
            print('bounds is', get_scaled_roi(mini, 2))
        if not windows_set:
            x, y, w, h = cv2.getWindowImageRect('inventory')
            cv2.moveWindow('mini', 0, 0)
            cv2.moveWindow('stats', 0, 600)
            cv2.moveWindow('inventory', SCREEN_WIDTH-w, SCREEN_HEIGHT-h+65)
            windows_set = True