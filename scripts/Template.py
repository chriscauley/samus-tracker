import cv2
import numpy as np
from pathlib import Path

import urcv

DIR = Path('templates')
DIR.mkdir(exist_ok=True)

_templates = {}

ONES = np.ones((5, 5), dtype=np.uint8)
# ONES = np.array([
#     [0.5,0.5,0.5,0.5,0.5],
#     [0.5,1,1,1,0.5],
#     [0.5,1,1,1,0.5],
#     [0.5,1,1,1,0.5],
#     [0.5,0.5,0.5,0.5,0.5],
# ], dtype=np.uint8)
def init():
    for f in DIR.iterdir():
        _load(*f.stem.split("__"))


def get_bounds_for_contours(contours):
    boxes = []
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        boxes.append([x,y, x+w,y+h])

    boxes = np.asarray(boxes)
    left, top = np.min(boxes, axis=0)[:2]
    right, bottom = np.max(boxes, axis=0)[2:]

    return (left, top, right - left, bottom - top)


def _load(video_id, frame_number, item_name):
    key = _key(video_id, frame_number, item_name)
    path = DIR / f'{key}.png'
    _templates[key] = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2GRAY)


def _key(video_id, frame_number, item_name):
    return f'{video_id}__{frame_number}__{item_name}'


def exists(video_id, frame_number, item_name):
    return _key(video_id, frame_number, item_name) in _templates


def create(video_id, frame_number, item_name, content):
    key = _key(video_id, frame_number, item_name)
    if not key in _templates:
        path = DIR / f'{key}.png'
        print(f'saving {path}')
        cv2.imwrite(str(path), content)
        _load(video_id, frame_number, item_name)


def get(video_id, frame_number, item_name):
    key = _key(video_id, frame_number, item_name)
    return _templates[key]


def match_all(content):
    gray = cv2.cvtColor(content, cv2.COLOR_BGR2GRAY)
    results = []
    for key, template in _templates.items():
        _, _, item_name = key.split("__")
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
        results.append((maxVal, maxLoc, item_name, template))
    return sorted(results)