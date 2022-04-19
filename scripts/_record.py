import cv2
import numpy as np
from mss import mss
from pathlib import Path
from PIL import Image
import time
import urcv
import sys

# define dimensions of screen w.r.t to given monitor to be captured
target = sys.argv[1]
path = Path(sys.argv[1])

x, y, w, h = [0, 64, 1024, 896]

if sys.argv[1] == '--bounds':
    x, y, w, h  = [0,0,1400,1080]
else:
    print('starting in 3...2...1')
    time.sleep(3)
    if not path.exists():
        path.mkdir()

options = {
    'left': x,
    'width': w,
    'top': y,
    'height': h,
}

last = 0
i = 0
i_max = 250
with mss() as sct:
    last = None
    while True:
        screenShot = sct.grab(options)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        if sys.argv[1] == '--bounds':
            print(urcv.get_scaled_roi(frame, 1, pixel_fix=True))
            exit()
        if last != np.sum(frame):
            print(f'{path}/{i:04d}.png')
            cv2.imwrite(f'{path}/{i:04d}.png', frame)
            i += 1
            last = np.sum(frame)
            if i > i_max:
                break


        # img = Image.frombytes(
        #     'RGB',
        #     (screenShot.width, screenShot.height),
        #     screenShot.rgb,
        # )
        # frame = np.array(img)
        # mini_h = int(GAME_LEFT * GAME_HEIGHT / GAME_WIDTH)
        # mini = cv2.resize(frame, (GAME_LEFT, mini_h))
        # gray_mini = cv2.cvtColor(mini, cv2.COLOR_RGB2GRAY)
        # frames.append(time.time())
        # frames = [f for f in frames if f > time.time() - 5]
        # if last is not None:
        #     frameDelta = cv2.absdiff(last, gray_mini)
        #     thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        #     thresh = cv2.dilate(thresh, None, iterations=2)
        #     diff = cv2.bitwise_and(mini, mini, mask=thresh)
        #     urcv.text.write(diff, f'fps: {int(10*len(frames)/5)/10}')
        #     cv2.imshow('diff', diff)

        # cv2.imshow('test', mini)
        # pressed = urcv.wait_key(max_time=1, delay=33)
        # if pressed == 'q':
        #     break
        # last = gray_mini