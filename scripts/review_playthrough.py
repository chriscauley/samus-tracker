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


all_items = None

item, item_bounds = None, []

while True:
    if stop_at and playthrough._index == stop_at:
        break

    item, item_bounds = playthrough.check_item()
    if item_bounds:
        x, y, _, _ = item_bounds[0]
        if all_items is None:
            all_items = playthrough.get_frame().copy()
        else:
            all_items = cv2.add(all_items, playthrough.get_frame())
        all_items_copy = cv2.multiply(all_items, (100, 100, 100, 1))
        cv2.imshow('all_items', all_items_copy)
    if not playthrough.goto:
        copy = playthrough.get_frame()
        urcv.text.write(copy, playthrough._current)
        inventory = playthrough.get_inventory_image()
        cv2.imshow('inventory', inventory)

        h, w = copy.shape[:2]
        urcv.text.write(copy, playthrough._index, pos=(w, h), align="bottom right")
        cv2.imshow('copy', copy)
        playthrough.does_frozen_match_live()

    pressed = playthrough.wait_key()
    if pressed == 'b':
        copy = playthrough.get_frame().copy()
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
        template.save_from_frame('item', playthrough.get_frame())
    elif pressed == 'q':
        break
