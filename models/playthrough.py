import cv2
import numpy as np
import urcv

from .base import BasePlaythrough


class Playthrough(BasePlaythrough):
    """
    Playthroughs are a series of frames captured live via the mss package
    """
    def __init__(self, id, world=None):
        self.root_dir = '.cache/playthroughs'
        super().__init__(id, world)
        self.frames_path = self.path / 'frames'
        self.frames_path.mkdir(parents=True, exist_ok=True)
        self.frame_count = len(list(self.frames_path.glob("*.png")))

    def get_max_index(self):
        return self.frame_count - 1

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
        if self._frozen:
            raise ValueError("You cannot save a frame to a frozen playthrough")
        if frame_no is None:
            frame_no = self.frame_count
            self.frame_count += 1
        cv2.imwrite(str(self.path / f'frames/{frame_no}.png'), image)

    def get_frame(self, frame_id=None):
        if frame_id == None:
            frame_id = self._index
        return cv2.imread(f'{self.frames_path}/{frame_id}.png')

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
