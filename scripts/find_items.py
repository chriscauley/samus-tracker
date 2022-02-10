import cv2
import numpy as np
import sys
from pathlib import Path
import datetime

from unrest.utils import JsonCache

xy_scan = np.array(
    [
        [0,1,0],
        [1,0,1],
        [0,1,0],
    ],
    dtype="int"
)

def hyper_invert(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.filter2D(image, -1, xy_scan)
    image = cv2.filter2D(image, -1, xy_scan)
    return np.invert(image)
    return image

def wait_key(keys, max_time=60000, default=None):
    delay = 500
    time = 0
    while time < max_time:
        pressed = cv2.waitKey(delay)
        for key, value in keys.items():
            if ord(key) == pressed:
                return value
        time += delay
    return default


def get_scaled_roi(image, scale):
    w = image.shape[1] * scale
    h = image.shape[0] * scale
    return cv2.selectROI(cv2.resize(image, (w, h)))


def main(youtube_id):
    video_dir = Path(f'.cache/youtube/{youtube_id}')
    video_dir.mkdir(exist_ok=True)
    frame_dir = video_dir / 'frames'
    config = JsonCache(f'.cache/youtube/{youtube_id}/config.json', {
        'external_id': 'Syygh_qwaTU',
        'i_frame': 0,
    })
    frames = sorted([i for i in list(frame_dir.iterdir()) if i.suffix == '.png'])
    max_frame = len(frames)
    while config['i_frame'] < max_frame:
        frame_path = frames[config['i_frame']]
        frame = cv2.imread(str(frame_path))
        if not 'timer_bounds' in config:
            config['timer_bounds'] = get_scaled_roi(frame, 4)
        if not 'game_bounds' in config:
            config['game_bounds'] = get_scaled_roi(frame, 3)

        #convert from BGR to HSV color space
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_h, frame_w = gray.shape

        #apply threshold
        thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)[1]
        scanned = cv2.filter2D(thresh, -1, xy_scan)

        # find contours and get one with area about 180*35
        # draw all contours in green and accepted ones in red
        contours = cv2.findContours(scanned, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        #area_thresh = 0
        min_area = 0.95*180*35
        max_area = 1.05*180*35
        result = frame.copy()
        for c in contours:
            area = cv2.contourArea(c)
            if area < min_area:
                continue
            x, y, w, h = cv2.boundingRect(c)
            center_x = x + w / 2
            center_y = y + h / 2
            print(center_x, frame_w / 2,center_x - frame_w / 2)
            cv2.rectangle(result, (x,y),(x+w,y+h),(0,255,0),2)
            if abs(center_x - frame_w / 2) < 50 and abs(center_y - frame_h / 2) < 50:
                cv2.drawContours(result, [c], -1, (0, 0, 255), 1)

        cv2.imshow('gray', gray)
        cv2.imshow('thresh', thresh)
        cv2.imshow('scanned', scanned)
        cv2.imshow('result', result)
        config['i_frame'] = wait_key({
            "q": max_frame + 1,
            "f": config['i_frame'] + 1,
            "b": config['i_frame'] - 1,
            "n": config['i_frame'] + 10,
            "p": config['i_frame'] - 10,
        })


if __name__ == "__main__":
    main(sys.argv[1])