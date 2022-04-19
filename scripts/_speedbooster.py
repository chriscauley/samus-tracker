import setup

import cv2
import numpy as np
from pathlib import Path
import sys
import urcv
from unrest.utils import time_it, JsonCache

import matplotlib.pyplot as plt

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def compactify(image):
    image = image[::4, ::4] # down pixel
    current = image[:,0]
    last = 0
    h0, w0 = image.shape[:2]
    cols = []
    for i_col in range(w0):
        if not np.array_equal(image[:,i_col], current):
            current = image[:, i_col]
            cols.append(i_col)
            last = i_col
    for i_col in range(w0)[::-1]:
        if not i_col in cols:
            image = np.delete(image, i_col, 1)
    return image

def invert_match(back, front):
    bw = back.shape[1]
    fw = front.shape[1]
    values = []

    for i in range(1, bw - fw):
        back_slice = back[:,i:i+fw]
        combined = cv2.add(cv2.bitwise_not(back_slice), front)
        # cv2.imshow('doot', np.hstack([back_slice, front, combined]))
        values.append(255 * combined.size - np.sum(combined))
        # print(combined.flatten() == 255, np.sum(combined) - 255 * combined.size)
        # urcv.wait_key()
        if all(combined.flatten() == 255):
            return i
    min_ = min(values)
    return values.index(min_)


def get_box(frame):
    ys, xs = np.where(np.all(frame == (0,0,255), axis=-1))
    return (min(*xs), min(*ys), max(*xs), max(*ys))


def main(number, show=False):
    frames_dir = Path(f'.cache/speedbooster/{number}')

    xs = []
    canvas = None
    og_canvas = None
    gray_canvas = None
    dw = 0
    last = 0

    for i_frame in range(len(list(frames_dir.iterdir()))):
        og = cv2.imread(f'{frames_dir}/{i_frame:04d}.png')
        last = np.sum(og)
        frame = compactify(og)
        urcv.replace_color(frame, (255, 65, 66), (0,0,255))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if i_frame == 0:
            # first loop, start canvas
            canvas = frame.copy()
            og_canvas = frame.copy()
            gray_canvas = gray
            continue

        w, h = frame.shape[:2]
        template = gray[:, 0:64]
        template[16:-32] = 0
        target = gray_canvas[:,dw:dw+128]
        target[16:-32] = 0


        dx = invert_match(target, template)
        box_bounds = get_box(frame)
        xs.append(box_bounds[0] + dw)

        # draw a white line to prevent back shifting
        canvas[:,dw] = 255
        gray_canvas[:,dw] = 255
        target[0:5,dx] = 255

        dw += dx
        canvas = urcv.draw.paste_expandable(canvas, frame, dw, 0)
        gray_canvas = urcv.draw.paste_expandable(gray_canvas, gray, dw, 0)
        og_canvas = urcv.draw.paste(np.zeros(canvas.shape, dtype=np.uint8), og_canvas, 0, 0)

        if show:
            cv2.imshow('template', template)
            cv2.imshow('target', target)
            cv2.imshow('canvas', urcv.transform.scale(canvas, 2))
            cv2.imshow('frame', frame)
            pressed = urcv.wait_key()

            if pressed == 'q':
                break

    dxs = []
    for i, x in enumerate(xs):
        if i:
            dxs.append(x-xs[i-1])

    if show:
        plt.plot(dxs)
        plt.plot(moving_average(dxs, 4))
        plt.ylabel('dxs')
        plt.show()
    return [int(i) for i in dxs]


if __name__ == '__main__':
    if sys.argv[1] == 'all':
        folders = Path('.cache/speedbooster').iterdir()
        folders = [f for f in folders if str(f).split('/')[-1].isdigit()]
        cached = JsonCache('.cache/speedbooster/data.json')
        for i,f in enumerate(folders):
            if not str(f) in cached:
                print('processed', f)
                cached[str(f)] = main(str(f).split('/')[-1])
            dxs = cached[str(f)]
            # plt.plot(dxs)
            data = moving_average(dxs, 4)
            # normalize speed vs timer.py data (see notes.org)
            data = [i * 10.23 / 2.753 for i in data]
            # i/20 here is because the lines are too close to differentiate
            # data = [dx+i/20 for dx in data]
            plt.plot([i/60 for i in range(len(data))], data)
        plt.ylabel('dxs')
        plt.show()
    else:
        main(sys.argv[1], show = True)