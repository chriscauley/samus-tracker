import cv2
from pathlib import Path
from unrest.utils import JsonCache
import urcv

class Video():
    def __init__(self, external_id):
        self._current_frame_number = None
        self._current_frame = None
        self.external_id = external_id
        self.video_dir = Path(f'.cache/youtube/{external_id}')
        if not (self.video_dir / f'{external_id}.mp4').exists():
            raise ValueError(f"No video exists for external_id: {external_id}")
        self.frame_dir = self.video_dir / 'frames'
        self.frame_dir.mkdir(exist_ok=True)
        files = list(self.frame_dir.iterdir())
        self.frames = sorted([i for i in files if i.suffix == '.png'])


        self.config = JsonCache(str(self.video_dir / 'config.json'), {
            'external_id': 'Syygh_qwaTU',
            'i_frame': 0,
        })
        self.data = JsonCache(str(self.video_dir / 'data.json'), {
            'item_frames': [],
            'names_by_frame': {}
        })
        if not 'fps' in self.config:
            self.config['fps'] = int(input('What is the fps?'))

    def get_item_name(self, frame_number):
        return self.data['names_by_frame'].get(str(frame_number))

    def set_item_name(self, frame_number, name):
        print('s', frame_number, name)
        self.data['names_by_frame'][str(frame_number)] = name
        self.data._save()

    def get_frame(self, frame_number):
        frame_path = self.frames[frame_number]
        return cv2.imread(str(frame_path))

    def get_game_content(self, frame_number):
        if self._current_frame_number == frame_number:
            return self._current_frame
        if not 'game_bounds' in self.config:
            e = "Cannot extract item name without setting video.config['game_bounds']"
            raise ValueError(e)
        frame = self.get_frame(frame_number)
        self._current_frame_number = frame_number
        self._current_frame = urcv.transform.crop(frame, self.config['game_bounds'])
        return self._current_frame

    def get_item_content(self, frame_number):
        if not 'item_bounds' in self.config:
            e = "Cannot extract item name without setting video.config['item_bounds']"
            raise ValueError(e)
        frame = self.get_game_content(frame_number)
        return urcv.transform.crop(frame, self.config['item_bounds'])
