import setup
import cv2
from models import Playthrough, Template, MotionDetector
import matplotlib.pyplot as plt
import numpy as np
import sys

import urcv
from unrest.utils import time_it

sums_hit = []
sums_miss = []


playthrough = Playthrough(sys.argv[1])
playthrough.freeze()
template = Template(playthrough.data['world'])
trex = MotionDetector()


def search_item(template, gray_mini):
    return template.search(gray_mini, 'item')


def search_zone(template, gray_mini):
    cropped = gray_mini[:40,:200]
    return template.search(cropped, 'zone')

# @time_it(True)
def search(gray_mini):
    x, y, w, h = 52, 173, 496, 161
    cropped = gray_mini[y:y+h, x:x+w]
    return template.search(cropped, 'item')

all_items = np.zeros((0))

while True:
    frame = playthrough.get_frame(playthrough._index)
    copy = frame.copy()
    gray_mini = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    item_sum = playthrough.sum_item_box(gray_mini)

    if item_sum < 1e4:
        item, item_bounds = search(gray_mini)
    else:
        item, item_bounds = None, []
    playthrough.touch(item)
    if item_bounds:
        x, y, _, _ = item_bounds[0]
        if all_items.shape != frame.shape:
            all_items = frame.copy()
        else:
            all_items = cv2.add(all_items, frame)
        cv2.imshow('all_items', cv2.multiply(all_items, (100, 100, 100, 1)))
        urcv.text.write(copy, item)
        sums_hit.append(item_sum)
        if item_sum:
            bounds = 431, 223, 32, 42
    elif item_sum < 1e2:
        sums_miss.append(item_sum)
    if not playthrough.goto:
        inventory = playthrough.get_inventory_image()
        cv2.imshow('inventory', inventory)

        h, w = copy.shape[:2]
        urcv.text.write(copy, playthrough._index, pos=(w, h), align="bottom right")
        urcv.text.write(copy, item_sum, pos=(0, h), align="bottom")
        cv2.imshow('copy', copy)
        if not playthrough.does_frozen_match_live():
            playthrough.goto = None

    pressed = playthrough.wait_key()
    if pressed == 'b':
        x, y, w, h = urcv.get_scaled_roi(copy, 1)
        cropped = urcv.transform.crop(copy, (x, y, w, h))
        cv2.imshow('cropped', cropped)
        print('bounds is', (x, y, w, h))
    elif pressed == 'p':
        fig, (ax1, ax2) = plt.subplots(2)
        fig.suptitle('Horizontally stacked subplots')

        ax1.hist(sums_hit, range=(0, 1e2))
        ax2.hist(sums_miss, range=(0, 1e2))
        fig.show()
        input('review plot and press enter')
    elif pressed == 'i':
        template.save_from_frame('item', frame)
    elif pressed == 'q':
        break
