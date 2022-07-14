import setup
from models import Video
import cv2
import io
import matplotlib.pyplot as plt
import numpy as np
import sys
import urcv

cap = cv2.VideoCapture(sys.argv[1])

if not cap.isOpened():
    print("Error opening video stream or file")

last_game = None
last_hud = None
last_map = None
in_door = False
last_door = None

trex1 = [0,0,0,0,0]
trex2 = [0,0,0,0,0]

ITEM_THRESH = 0.001
DOOR_THRESH = 0.1
HUD_SPLIT = 31
MAP_BOUNDS = [243, 5, 50, 26]

fig, ax = plt.subplots()

def plot3():
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    return data.reshape((int(h), int(w), -1))

def clamp(num, min_value, max_value):
        return max(min(num, max_value), min_value)

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

while(cap.isOpened()):
    ret, og = cap.read()
    frame_no = cap.get(cv2.CAP_PROP_POS_FRAMES)
    hud = og[:HUD_SPLIT]
    game = og[HUD_SPLIT:]

    if frame_no %2 == 1:
        continue
    # game = cv2.blur(game, (7,7))
    frame = game.copy()

    if last_game is None:
        last_game = game
        continue
    # diff1 = cv2.subtract(frame, last_game)
    # cv2.imshow('diff1', diff1)
    # diff1 = np.sum(diff1)
    # diff2 = np.sum(cv2.subtract(last_game, frame))
    # urcv.text.write(frame, diff1, pos=(0, frame.shape[0]), align="bottom")
    # urcv.text.write(frame, diff2, pos=(200, frame.shape[0]), align="bottom")
    # trex1.append(clamp(diff1 / np.sum(frame), 0, 2))
    # trex2.append(clamp(diff2 / np.sum(frame), 0, 2))
    value = (int(np.sum(frame)) - int(np.sum(last_game))) / int(np.sum(frame) or 1e24)
    trex1.append(clamp(value, -1, 1))
    urcv.text.write(frame, round(value,2), pos=(0, frame.shape[0]), align="bottom")
    urcv.text.write(frame, frame_no)

    if in_door:
        door_text = 'in_door'
        if all([i > DOOR_THRESH for i in trex1[-5:]]):
            in_door = False
            last_door = frame_no
    else:
        door_text = f'last: {last_door}'
        if all([i < -DOOR_THRESH for i in trex1[-5:]]):
            in_door = True

    h, w = game.shape[:2]
    urcv.text.write(frame, door_text, pos=(w,h), align='bottom right')

    cv2.imshow('frame', urcv.transform.scale(frame, 4))
    if frame_no % 60 == 0 or True:
        trex1 = trex1[-120:]
        trex2 = trex2[-120:]
        plt.plot(trex1, label="trex1")
        plt.ylim([-0.003, 0.003])
        # plt.plot(moving_average(trex2, 5), label="trex2")
        cv2.imshow('plot', plot3())
        plt.clf()

    urcv.wait_key()
    last_game = game
