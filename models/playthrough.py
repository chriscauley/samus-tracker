from pathlib import Path
import json
import cv2


class Playthrough:
    def __init__(self, id):
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