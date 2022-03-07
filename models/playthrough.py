import cv2
from collections import defaultdict
import json
import numpy as np
from pathlib import Path
import urcv

from .mixins import WaitKeyMixin
from maptroid.icons import get_icons


class Playthrough(WaitKeyMixin):
    def __init__(self, id, world=None):
        super().__init__()
        self.icons = get_icons('items')
        self.gray_icons = get_icons('items', _cvt=cv2.COLOR_BGR2GRAY)
        self.frozen = False
        self.data = {
            'item_names': [],
            'item_frames': [],
            'item_duplicates': [],
            'fps': 4,
            'world': world,
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
        if not self.data['world']:
            raise ValueError("Playthrough must have world set")
        self.frame_count = len(list(self.frames_path.glob("*.png")))

    def freeze(self):
        self.frozen = True
        self.frozen_data = self.data
        self.data = {
            **self.frozen_data,
            'item_names': [],
            'item_frames': [],
            'item_duplicates': [],
        }

    def get_max_index(self):
        return self.frame_count - 1

    def touch(self, item_name):
        if item_name and self._current != item_name:
            self.data['item_names'].append(item_name)
            self.data['item_frames'].append(int(self._index))
            self.last = item_name
            self.save()
        self._current = item_name

    def save(self):
        if not self.frozen:
            # for some reason this is sometimes a uint64 which is not serializeable
            self.data['item_frames'] = [int(i) for i in self.data['item_frames']]
            self._data_json.write_text(json.dumps(self.data))

    def mark_duplicate(self, _id=None):
        _id = _id or len(self.data['item_names'])
        if _id in self.data['item_duplicates']:
            self.data['item_duplicates'].remove(_id)
        else:
            self.data['item_duplicates'].append(_id)
        self.save()

    def is_last_duplicate(self):
        _id = len(self.data['item_names'])
        return _id in self.data['item_duplicates']

    def save_frame(self, image, frame_no=None):
        if self.frozen:
            raise ValueError("You cannot save a frame to a frozen playthrough")
        if frame_no is None:
            frame_no = self.frame_count
            self.frame_count += 1
        cv2.imwrite(str(self.path / f'frames/{frame_no}.png'), image)

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

    def get_stats(self, extra={}):
        return {
            # 'fps': round(len(frames) / (time.time() - frame_times[0]), 2),
            'last': self.last,
            'saved_frames': self.frame_count,
            'duplicated': self.is_last_duplicate(),
            **extra
        }

    def does_frozen_match_live(self):
        live = self.data['item_names']
        frozen = self.frozen_data['item_names']
        for i, live_item in enumerate(live):
            if i > len(frozen) - 1:
                print(f"Frozen items stop after {i}")
                return
            if live_item != frozen[i]:
                print(f'Item mismatch {live_item} != {frozen[i]} @{i}')
                print('Items in live', live)
                print('mismatch frame number:', self.data['item_frames'][i])
                return
        print(f'frozen and live match up to {len(live)}/{len(frozen)}')
        return True

    def sum_item_box(self, frame):
        frame = urcv.transform.threshold(frame, value=10)
        boundses = [
            [114, 225, 32, 28],
            [431, 223, 32, 42],
            [189, 251, 244, 14],
        ]
        item_sum = 0
        for x, y, w, h in boundses:
            item_sum += np.sum(frame[y:y+h,x:x+w])
        return item_sum
