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

data['doors'] = []

door_text = '__'

max_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

last_is_door = False
last_door = 0

_show = 0
DOOR_THRESHOLD = 50
frame_no = 0

sums = moving_average(data['sums'], 3)
deltas = moving_average(data['deltas'], 3)
between_doors = []

while frame_no < len(sums):
    sums_below = sums[frame_no] < DOOR_THRESHOLD
    deltas_below = deltas[frame_no] < DOOR_THRESHOLD
    current_is_door = sums_below and deltas_below

    if last_is_door and not current_is_door:
        door_length = frame_no - last_door
        data['doors'].append([frame_no, door_length])
        if door_length < 15:
            pass
            # _show = 4
        last_is_door = False

    if not last_is_door and current_is_door:
        between_doors.append(frame_no - last_door)
        last_door = frame_no

    last_is_door = current_is_door

    if _show:
        cap.set(1, frame_no+1)
        ret, og = cap.read()
        _show -= 1
        last_door = frame_no
        frame = og.copy()
        percent = round(100 * frame_no / max_frame, 2)
        urcv.text.write(frame, f'{percent}%', pos="top right")
        urcv.text.write(frame, frame_no, pos='bottom')
        cv2.imshow('frame', frame)
        start = max(frame_no-1000, 0)
        plt.plot(sums[start:frame_no], label="sums")
        plt.plot(deltas[start:frame_no], label="deltas")
        cv2.imshow('plot', plot3())
        plt.clf()

        urcv.wait_key()
    frame_no += 1

data._save()
door_lengths = [d[1] for d in data['doors']]

n, bins, patches = plt.hist(door_lengths, 50)
# n, bins, patches = plt.hist([i for i in between_doors if i < 200], 50)
plt.show()
urcv.wait_key()