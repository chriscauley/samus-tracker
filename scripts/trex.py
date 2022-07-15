import setup
from models import Video
import cv2
import io
import matplotlib.pyplot as plt
import numpy as np
import sys
from unrest.utils import JsonCache
import urcv

from misc import NumpyEncoder

cap = cv2.VideoCapture(sys.argv[1])

if not cap.isOpened():
    print("Error opening video stream or file")

if '-f' in sys.argv:
    cap.set(1, int(sys.argv[sys.argv.index('-f')+1]))
last_game = None
last_hud = None
last_map = None
in_door = False

trex1 = [0, 0, 0, 0, 0]
trex2 = [0, 0, 0, 0, 0]
frames = []
sums = []

ITEM_THRESH = 0.001
HUD_SPLIT = 31
MAP_BOUNDS = [243, 5, 50, 26]

fig, ax = plt.subplots()

def plot3():
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    plt.clf()
    return data.reshape((int(h), int(w), -1))

def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

sums = []
deltas = [0] # first frame has no last_frame, so no delta

PLOT_LEN = 20
DISPLAY_RATE = 1

def sumcells(img, size=16):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.dilate(img, np.ones((5, 5), np.uint8))

    H = int(img.shape[0] / size)
    W = int(img.shape[1] / size)

    return cv2.resize(img,(W,H)) > 5

max_frame_no = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
og = True
_show = False

while cap.isOpened():
    ret, og = cap.read()
    if og is None:
        break
    frame_no = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
    hud = og[:HUD_SPLIT]
    game = og[HUD_SPLIT:]

    frame = game.copy()

    sum_ = sumcells(game)
    sums.append(np.sum(sum_))

    if last_game is None:
        last_game = game
        continue


    delta = cv2.add(
        cv2.subtract(game, last_game),
        cv2.subtract(last_game, game)
    )

    sum_delta = sumcells(delta)
    deltas.append(np.sum(sum_delta))

    if frame_no % DISPLAY_RATE == 0 or _show:
        urcv.text.write(frame, frame_no, pos="bottom")
        percent = round(100 * frame_no / max_frame_no, 2)
        urcv.text.write(frame, f'{deltas[-1],sums[-1]}')
        urcv.text.write(frame, f'{percent}%', pos="bottom right")
        cv2.imshow('frame,delta', np.vstack([frame, delta]))

        sum_delta = np.multiply(255, sum_delta.astype(np.uint8))
        sum_ = np.multiply(255, sum_.astype(np.uint8))
        cv2.imshow('sum,delta', urcv.transform.scale(np.vstack([sum_,sum_delta]), 16))

        plt.plot(sums[-PLOT_LEN:], label="sums")
        plt.plot(deltas[-PLOT_LEN:], label="deltas")
        _deltas = deltas[-PLOT_LEN:]

        ddeltas = [0] + [_deltas[i+1] - _deltas[i] for i in range(len(_deltas)-1)]
        plt.plot(ddeltas, label="ddeltas")

        cv2.imshow('plot', plot3())
        pressed = urcv.wait_key()
        if pressed == 'q':
            exit()

    last_game = game


data = JsonCache(f'.data/{sys.argv[1].split("/")[-1]}.json', __encoder__=NumpyEncoder)
data['sums'] = sums
data['deltas'] = deltas

print(len(data['sums']))