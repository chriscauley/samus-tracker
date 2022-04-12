import setup
import cv2
from models import Playthrough, Template, MotionDetector
import numpy as np
import sys

import urcv
from unrest.utils import time_it

stop_at = None
playthrough = Playthrough(sys.argv[1])
if '--stop-at' in sys.argv:
    stop_at = sys.argv[sys.argv.index('--stop-at') + 1]
    if stop_at == 'end':
        stop_at = playthrough.get_max_index()-1
    stop_at = int(stop_at)
    playthrough.increase_goto_by(stop_at)

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
    if stop_at and playthrough._index == stop_at:
        break
    frame = playthrough.get_frame(playthrough._index)
    if frame is None:
        raise ValueError("missing frame:", playthrough._index)
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
        if item_sum:
            bounds = 431, 223, 32, 42
    # elif item_sum < 1e2:
    #     sums_miss.append(item_sum)
    if not playthrough.goto:
        inventory = playthrough.get_inventory_image()
        cv2.imshow('inventory', inventory)

        h, w = copy.shape[:2]
        urcv.text.write(copy, playthrough._index, pos=(w, h), align="bottom right")
        urcv.text.write(copy, item_sum, pos=(0, h), align="bottom")
        cv2.imshow('copy', copy)
        playthrough.does_frozen_match_live()

    pressed = playthrough.wait_key()
    if pressed == 'b':
        x, y, w, h = urcv.get_scaled_roi(copy, 1)
        cropped = urcv.transform.crop(copy, (x, y, w, h))
        cv2.imshow('cropped', cropped)
        print('bounds is', (x, y, w, h))
    elif pressed == 's':
        print('unfreezing and saving', end=" ")
        playthrough._frozen = False
        playthrough.save()
        print('...done')
        exit()
    elif pressed == 'i':
        template.save_from_frame('item', frame)
    elif pressed == 'q':
        break
