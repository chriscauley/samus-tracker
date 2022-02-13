import cv2
import numpy as np
from pathlib import Path

import urcv

DIR = Path('.cache/templates')
DIR.mkdir(exist_ok=True)

_templates = {}

ONES = np.ones((3, 3), dtype=np.uint8)

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


def isolate_name(frame_name):
    # isolate red channel
    hsv_name = cv2.cvtColor(frame_name, cv2.COLOR_BGR2HSV)
    red_hsv_name = urcv.hsv.filter(hsv_name, hue=[161, 172])
    red_name = cv2.cvtColor(red_hsv_name, cv2.COLOR_HSV2BGR)

    # threshold, erode and dilate
    gray = cv2.cvtColor(red_name, cv2.COLOR_BGR2GRAY)
    erode = cv2.erode(gray, ONES, iterations=1)
    _, mask = cv2.threshold(erode, 127, 255, cv2.THRESH_BINARY_INV)
    thresh = cv2.bitwise_and(erode, erode, mask=mask)
    dilate = cv2.dilate(thresh, ONES, iterations=1)


    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bounds = get_bounds_for_contours(contours)

    # useful for debugging
    # (x, y, w, h) = bounds
    # frame_name = cv2.rectangle(frame_name, (x, y), (x+w, y+h), (255,0,0), 1)
    # cv2.imshow('frame_name', urcv.transform.scale(frame_name, 2))
    # cv2.imshow('red_name', urcv.transform.scale(red_name, 2))
    # cv2.imshow('gray', urcv.transform.scale(gray, 2))
    # cv2.imshow('erode', urcv.transform.scale(erode, 2))
    # cv2.imshow('thresh', urcv.transform.scale(thresh, 2))
    # cv2.imshow('dilate', urcv.transform.scale(dilate, 2))
    # cv2.waitKey(0)
    # exit()

    return urcv.transform.crop(gray, bounds)

def _load(video_id, frame_number, item_name):
    key = _key(video_id, frame_number, item_name)
    path = DIR / f'{key}.png'
    frame_name = cv2.imread(str(path))
    _templates[key] = isolate_name(frame_name)


def _key(video_id, frame_number, item_name):
    return f'{video_id}__{frame_number}__{item_name}'


def exists(video_id, frame_number, item_name):
    return _key(video_id, frame_number, item_name) in _templates


def create(video_id, frame_number, item_name, content):
    key = _key(video_id, frame_number, item_name)
    if not key in _templates:
        path = DIR / f'{key}.png'
        print('saving {path}')
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