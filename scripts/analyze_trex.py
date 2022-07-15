import setup
import cv2
import io
import matplotlib.pyplot as plt
import numpy as np
import sys
import urcv
from unrest.utils import JsonCache

from misc import NumpyEncoder, moving_average

cap = cv2.VideoCapture(sys.argv[1])

HUD_SPLIT = 31

fig, ax = plt.subplots()

def plot3():
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    return data.reshape((int(h), int(w), -1))

data = JsonCache(f'.data/{sys.argv[1].split("/")[-1]}.json', __encoder__=NumpyEncoder)

door_text = '__'

max_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

in_door = False
last_door = 0

while(cap.isOpened()):
    ret, og = cap.read()
    frame_no = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

    is_door = data['sums'][frame_no] < 50 and data['sums'][frame_no] < 50
    if in_door and not is_door:
        print(frame_no - last_door)
        in_door = False

    in_door = is_door

    if frame_no - last_door < 200:
        continue
    if not is_door:
        continue

    last_door = frame_no
    frame = og.copy()
    percent = round(100 * frame_no / max_frame, 2)
    urcv.text.write(frame, f'{percent}%', pos="top right")
    urcv.text.write(frame, frame_no, pos='bottom')
    cv2.imshow('frame', frame)
    start = max(frame_no-1000, 0)
    plt.plot(data['sums'][start:frame_no], label="sums")
    plt.plot(data['deltas'][start:frame_no], label="deltas")
    cv2.imshow('plot', plot3())
    plt.clf()

    urcv.wait_key(0.001)