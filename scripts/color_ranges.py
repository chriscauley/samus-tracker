import cv2
from collections import OrderedDict
import numpy as np

HIGH_RED = [ np.array([170,120,70]), np.array([180,255,255]) ]
LOW_RED = [ np.array([0,120,70]), np.array([10,255,255]) ]
YELLOW = [ np.array([35,120,70]), np.array([45,255,255]) ]


ALL = [
    [ np.array([i*15,120,70]), np.array([(i+1)*15,255,255]) ]
    for i in range(12)
]


colors_by_hue = [
    ('_red1', 0, 2),
    # ('_red2', , ),
    ('orange', 2, 4),
    ('yellow', 4, 7),
    ('lime', 7, 9),
    ('green', 9, 12),
]


def filter_hue_range(hsv, hue, saturation=[120, 255], value=[70, 255]):
    lower = np.array([hue[0], saturation[0], value[0]])
    upper = np.array([hue[1], saturation[1], value[1]])
    mask = cv2.inRange(hsv, lower, upper)
    return cv2.bitwise_and(hsv, hsv, mask=mask)


def scan_hue(hsv, n_steps=12, **kwargs):
    results = []
    ranges = []
    s = 180 / n_steps
    for i in range(n_steps):
        ranges.append([int(i*s), int((i+1) * s)])
        results.append(filter_hue_range(hsv, ranges[-1], **kwargs))
    return results, ranges