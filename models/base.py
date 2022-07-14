from collections import defaultdict
import cv2
import json
import numpy as np
from pathlib import Path
import urcv

from maptroid.icons import get_icons

from .mixins import WaitKeyMixin
from .template import Template

ITEM_HOLE_BOUNDS = [
    [114, 225, 32, 28],
    [431, 223, 32, 42],
    [229, 251, 204, 14],
]
MOD_FRAMES = {
    'ypx': 1,
    'super_metroid': 1, # actually for varia
}


class BasePlaythrough(WaitKeyMixin):
    """ Defines the common API for Video and Playthrough models """
    root_dir = None
    def __init__(self, id, world):
        super().__init__()
        self.icons = get_icons('items')
        self.gray_icons = get_icons('items', _cvt=cv2.COLOR_BGR2GRAY)
        self.id = id
        self.data = {
            'item_names': [],
            'item_frames': [],
            'item_duplicates': [],
            'fps': 4,
            'world': world,
        }
        self.path = Path(f'{self.root_dir}/{id}/')
        self.path.mkdir(parents=True, exist_ok=True)
        self.item_path = Path(f'{self.root_dir}/{id}/items/')
        self.item_path.mkdir(parents=True, exist_ok=True)
        self._data_json = self.path / 'data.json'
        if self._data_json.exists():
            self.data = json.loads(self._data_json.read_text())
        if not self.data['world']:
            raise ValueError("Playthrough must have world set")
        self._current = self._last = None
        self._frozen = False
        self.template = Template(self.data['world'])
        self._item_hole_bounds = ITEM_HOLE_BOUNDS

    def freeze(self):
        self._frozen = True
        self._frozen_data = self.data
        self.data = {
            **self._frozen_data,
            'item_names': [],
            'item_frames': [],
            'item_duplicates': [],
        }

    def does_frozen_match_live(self):
        live = self.data['item_names']
        frozen = self._frozen_data['item_names']
        for i, live_item in enumerate(live):
            if i > len(frozen) - 1:
                print(f"Frozen items stop after {i}")
                return
            if live_item != frozen[i]:
                print(f'Item mismatch live:{live_item} != frozen:{frozen[i]} @{i}')
                print('Items in live', live)
                print('mismatch frame number:', self.data['item_frames'][i])
                return
        print(f'frozen and live match up to {len(live)}/{len(frozen)}')
        return True

    def touch(self, item_name):
        if item_name and self._current != item_name:
            fname = f'{len(self.data["item_names"]):03}.png'
            self.data['item_names'].append(item_name)
            self.data['item_frames'].append(int(self._index))
            self._last = item_name
            self.save()
            frame = self.get_frame().copy()
            urcv.text.write(frame, f'{self._index}-{item_name}')
            cv2.imwrite(str(self.item_path / fname), frame)
        self._current = item_name

    def save(self):
        if not self._frozen:
            # with numpy this is a uint64 which is not serializeable
            self.data['item_frames'] = [int(i) for i in self.data['item_frames']]
            self._data_json.write_text(json.dumps(self.data))

    def list_items(self, names=None):
        if names == None:
            names = list(dict.fromkeys(self.data['item_names']))
        items = defaultdict(int)
        for item_name in self.data['item_names']:
            items[item_name] += 1
        return [(name, items.get(name)) for name in names]

    def get_max_index(self):
        raise NotImplementedError()

    def get_frame(self):
        raise NotImplementedError()

    # TODO this should be on an inventory class
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

    # TODO this should be on an inventory class
    def get_stats(self, extra={}):
        return {
            # 'fps': round(len(frames) / (time.time() - frame_times[0]), 2),
            'last': self._last,
            'saved_frames': self.frame_count,
            'duplicated': self.is_last_duplicate(),
            **extra
        }

    # TODO item detection functions could be on their own class
    def sum_item_box(self, frame):
        frame = urcv.transform.threshold(frame, value=10)
        item_sum = 0
        for x, y, w, h in self._item_hole_bounds:
            item_sum += np.sum(frame[y:y+h,x:x+w])
        return item_sum

    # TODO item detection functions could be on their own class
    def check_item(self):
        world = self.data['world']

        # We can ignore most frames since the item stays open for 1-7 seconds depending on the mod
        if self._index % MOD_FRAMES[world] != 0:
            return None, []

        frame = self.get_frame()
        gray_mini = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Check to see if the item box is open by testing several bounds for blackness
        item_sum = self.sum_item_box(gray_mini)
        if item_sum > 1e4:
            return None, []

        item, item_bounds = self.template.search(gray_mini, 'item')
        self.touch(item)
        return item, item_bounds

    # TODO item detection functions could be on their own class
    def get_game_time(self):
        x, y, w, h = (92, 0, 152, 14)