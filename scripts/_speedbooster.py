import setup

import cv2
import numpy as np
from pathlib import Path
import sys
import urcv

root_dir = Path(f'.cache/speedbooster/{sys.argv[1]}')
frames_dir = root_dir / 'frames'


if not frames_dir.exists() or '--reset' in sys.argv:
    def _sorter(s):
        return s.replace('-1.png', '1.png')
    screenshots = sorted([str(s) for s in root_dir.iterdir() if str(s).endswith('.png')], key=_sorter)
    frames_dir.mkdir(exist_ok=True)
    ss0 = cv2.imread(screenshots[0])
    bounds = urcv.input.get_scaled_roi(ss0, 1, pixel_fix=True)
    for i, ss in enumerate(screenshots):
        fixed = urcv.transform.crop(cv2.imread(ss), bounds)
        cv2.imwrite(str(frames_dir / f'{i}.png'), fixed)
    print(f'wrote {len(screenshots)} frames')

canvas = None
og_canvas = None
gray_canvas = None

dw = 0

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
    if len(cols) != 240:
        print('warning: bad column size', len(cols))
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


for i_frame in range(len(list(frames_dir.iterdir()))):
    frame = og = cv2.imread(f'{frames_dir}/{i_frame}.png')
    frame = compactify(og)
    print(og.shape, frame.shape)
    # gray = cv2.medianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 3)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if i_frame == 0:
        # first loop, start canvas
        canvas = frame.copy()
        og_canvas = frame.copy()
        gray_canvas = gray
        continue

    w, h = frame.shape[:2]
    template = gray[:, 0:16]
    target = gray_canvas[:,dw:dw+128]
    # matches = urcv.template.match(target, template)

    # if len(matches) == 0:
    #     print('no matches!')
    #     urcv.wait_key()
    #     exit()

    # dx, _, _, _ = matches[0]

    # if not dx:
    #     print('no delta for frame', i_frame)
    #     continue


    # print(len(matches), 'matches', f'dw={dw}, dx={dx}')

    dx = invert_match(target, template)
    print(i_frame, dx)
    if not dx:
        continue

    # draw a white line to prevent back shifting
    canvas[:,dw] = 255
    gray_canvas[:,dw] = 255
    target[0:5,dx] = 255

    dw += dx
    canvas = urcv.draw.paste_expandable(canvas, frame, dw, 0)
    gray_canvas = urcv.draw.paste_expandable(gray_canvas, gray, dw, 0)
    og_canvas = urcv.draw.paste(np.zeros(canvas.shape, dtype=np.uint8), og_canvas, 0, 0)

    cv2.imshow('template', template)
    cv2.imshow('target', target)
    cv2.imshow('canvas', np.vstack([canvas, og_canvas[-32:]]))
    cv2.imshow('frame', frame)
    pressed = urcv.wait_key()
    if pressed == 'q':
        break
