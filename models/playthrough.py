import cv2
from collections import defaultdict
import json
import numpy as np
from pathlib import Path
import urcv

from maptroid.icons import get_icons

class Playthrough:
    def __init__(self, id):
        self.icons = get_icons('items')
        self.gray_icons = get_icons('items', _cvt=cv2.COLOR_BGR2GRAY)
        self.data = {
            'item_names': [],
            'item_frames': [],
            'item_duplicates': [],
            'fps': 4,
        }
        self.last = self._current = None
        self.id = id
        self.path = Path(f'.cache/playthroughs/{id}/')
        self.path.mkdir(parents=True, exist_ok=True)
        self.frames_path = self.path / 'frames'
        self.frames_path.mkdir(parents=True, exist_ok=True)
        self._data_json = self.path / 'data.json'
        if self._data_json.exists():
            self.data = json.loads(self._data_json.read_text())
        self.frame_count = len(list(self.frames_path.glob("*.png")))

    def touch(self, item_name):
        if item_name and self._current != item_name:
            self.data['item_names'].append(item_name)
            self.last = item_name
            self.save()
        self._current = item_name

    def save(self):
        self._data_json.write_text(json.dumps(self.data))

    def mark_duplicate(self, _id=None):
        _id = _id or len(self.data['item_names']) - 1
        if _id in self.data['item_duplicates']:
            self.data['item_duplicates'].remove(_id)
        else:
            self.data['item_duplicates'].append(_id)
        self.save()

    def is_last_duplicate(self):
        _id = len(self.data['item_names']) - 1
        return _id in self.data['item_duplicates']

    def save_frame(self, image):
        self.frame_count += 1
        cv2.imwrite(str(self.path / f'frames/{self.frame_count}.png'), image)

    def get_frame(self, frame_id):
        return cv2.imread(f'{self.frames_path}/{frame_id}.png')

    def list_items(self, names=None):
        if names == None:
            names = list(dict.fromkeys(self.data['item_names']))
        items = defaultdict(int)
        for item_name in self.data['item_names']:
            items[item_name] += 1
        return [(name, items.get(name)) for name in names]

    def get_inventory_image(self, item_counts=None):
        if item_counts is None:
            item_counts = self.list_items()
        scale = 4
        cols = 12
        rows = 2
        per_icon = 16
        _buffer = 1
        W = (per_icon + _buffer) * cols - _buffer
        H = (per_icon + _buffer) * rows - _buffer
        image = np.zeros((H, W, 4), dtype=np.uint8)
        image[:,:,3] = 255
        counts = []

        for index, (item, count) in enumerate(item_counts):
            x = (index % cols) * (per_icon + _buffer)
            y = (index // cols) * (per_icon + _buffer)
            _icons = self.icons if count else self.gray_icons
            urcv.draw.paste(image, self.icons[item], x, y)
            if count > 1:
                counts.append([x, y, count])
        image = urcv.transform.scale(image, scale)

        for x, y, count in counts:
            x = (x + per_icon) * scale
            y = (y + per_icon) * scale
            w, h = urcv.text.write(
                image,
                count,
                pos=(x, y),
                align="bottom right",
                bg_color=(0,0,0),
            )

        return image