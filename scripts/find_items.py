import cv2
import numpy as np
import sys
from pathlib import Path
import datetime

from unrest.utils import JsonCache

kernels = {
    'ones': np.ones((5,5), np.uint8),
    'xy_scan3': np.array(
        [
            [0,1,0],
            [1,0,1],
            [0,1,0],
        ],
        dtype="int"
    ),
    'xy_scan5': np.array(
        [
            [0,0,1,0,0],
            [0,0,1,0,0],
            [1,1,0,1,1],
            [0,0,1,0,0],
            [0,0,1,0,0],
        ],
        dtype="int"
    )
}

def hyper_invert(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.filter2D(image, -1, kernels['xy_scan3'])
    image = cv2.filter2D(image, -1, kernels['xy_scan3'])
    return np.invert(image)
    return image

def wait_key(max_time=60000, default=None):
    delay = 500
    time = 0
    while time < max_time:
        pressed = cv2.waitKey(delay)
        if pressed != -1:
            return chr(pressed)
        time += delay
    return default


def get_scaled_roi(image, scale):
    w = image.shape[1] * scale
    h = image.shape[0] * scale
    bounds = cv2.selectROI(cv2.resize(image, (w, h)))
    return [int(i/scale) for i in bounds]


def crop(image, bounds):
    print(bounds)
    x, y, w, h = bounds
    return image[y:y+h,x:x+w]


def highlight_contours(image, contours):
    for c in contours:
        area = cv2.contourArea(c)
        min_area = 0.95*180*35
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(image, (x,y),(x+w,y+h),(0,255,0),2)
        cv2.drawContours(image, [c], -1, (0, 0, 255), 1)

def main(youtube_id):
    video_dir = Path(f'.cache/youtube/{youtube_id}')
    video_dir.mkdir(exist_ok=True)
    frame_dir = video_dir / 'frames'
    config = JsonCache(str(video_dir / 'config.json'), {
        'external_id': 'Syygh_qwaTU',
        'i_frame': 0,
    })
    data = JsonCache(str(video_dir / 'data.json'), {
        'item_frames': [],
    })
    if not 'fps' in config:
        config['fps'] = int(input('What is the fps?'))
    frames = sorted([i for i in list(frame_dir.iterdir()) if i.suffix == '.png'])
    current_title = None
    while True:
        config['i_frame'] = config['i_frame'] % len(frames)
        _i = config['i_frame']
        frame_path = frames[config['i_frame']]
        frame = cv2.imread(str(frame_path))
        if not 'timer_bounds' in config:
            config['timer_bounds'] = get_scaled_roi(frame, 4)
        if not 'game_bounds' in config:
            config['game_bounds'] = get_scaled_roi(frame, 3)

        frame = crop(frame, config['game_bounds'])

        #convert from BGR to HSV color space
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_h, frame_w = gray.shape

        eroded = cv2.erode(gray, kernels['ones'], iterations=1)
        dilated = cv2.dilate(eroded, kernels['ones'], iterations=1)

        #apply threshold
        thresh = cv2.threshold(dilated, 1, 255, cv2.THRESH_BINARY)[1]
        scanned = cv2.filter2D(thresh, -1, kernels['xy_scan5'])

        # find contours and get one with area about 180*35
        # draw all contours in green and accepted ones in red
        contours = cv2.findContours(scanned, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        #area_thresh = 0
        result = frame.copy()
        if _i in data['item_frames']:
            matched = []
            for c in contours:
                area = cv2.contourArea(c)
                min_area = 0.95*180*35
                if area < min_area:
                    continue
                x, y, w, h = cv2.boundingRect(c)
                center_x = x + w / 2
                center_y = y + h / 2
                if frame_w / 2 > x and frame_w / 2 < x + w and frame_h / 2 > y and frame_h / 2 < y + h:
                    matched.append(c)
            c = sorted(matched, key=lambda c: cv2.contourArea(c))[0]
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(result, (x,y),(x+w,y+h),(255, 0, 0),2)
        else:
            highlight_contours(result, contours)

        cv2.imshow('gray', gray)
        cv2.imshow('thresh', thresh)
        cv2.imshow('scanned', scanned)
        cv2.putText(result, f'{_i} - {len(data["item_frames"])}', (5, frame_h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
        cv2.imshow('result', result)
        key = wait_key()
        if key == 'q':
            break
        if key == 'f':
            config['i_frame'] += 1
        if key == 'b':
            config['i_frame'] -= 1
        if key == 'n':
            config['i_frame'] += 10
        if key == 'p':
            config['i_frame'] -= 10
        if key == '0':
            config['i_frame'] = 0
        if key == 'i':
            if _i in data['item_frames']:
                data['item_frames'].remove(_i)
                print(data)
                data._save()
            else:
                data['item_frames'].append(_i)
                data['item_frames'] = sorted(data['item_frames'])

if __name__ == "__main__":
    main(sys.argv[1])