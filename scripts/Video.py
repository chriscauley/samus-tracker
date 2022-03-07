import cv2
import numpy as np
from pathlib import Path
from unrest.utils import JsonCache
import urcv

BUTTONS = [
    'left',
    'right',
    'up',
    'down',
    'dash', # a
    'jump', # b
    'item-select', # x
    'shot', # y
    'aim-up', # r
    'aim-down', # l
]


class Video():
    def __init__(self, external_id):
        self._current_frame_number = None
        self._current_frame = None
        self._i = 0
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
            'bounds': {},
        })
        self.data = JsonCache(str(self.video_dir / 'data.json'), {
            'item_frames': [],
            'names_by_frame': {},
            'coords_by_frame': {},
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

    def get_buttons_pressed(self, frame_number):
        pressed = []
        frame = self.get_game_content(frame_number)
        for button, bounds in self.config['bounds'].items():
            if not button in BUTTONS:
                continue
            x, y, w, h = bounds
            image = urcv.transform.crop(frame,bounds)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = urcv.transform.threshold(image)
            if np.sum(thresh) / thresh.size > 0.2:
                # print(button, np.sum(thresh), thresh.size)
                pressed.append(button)
        return pressed

    def get_item_template(self, frame_number):
        item_name = self.data['names_by_frame'][str(frame_number)]
        key = f'{self.external_id}__{frame_number}__{item_name}'
        path = f'templates/{key}.png'
        if not str(frame_number) in self.data['coords_by_frame']:
            item_content = self.get_item_content(frame_number)
            bounds = urcv.input.get_scaled_roi(item_content, 3)
            cv2.imwrite(path, urcv.transform.crop(item_content, bounds))
            self.data['coords_by_frame'][str(frame_number)] = bounds
            self.data._save()
        return cv2.imread(path)

    def wait_key(self):
        key = urcv.wait_key()
        if key == 'q':
            self._i = self.frames.length + 1
        elif key == 'f':
            self._i += 1
        elif key == 'b':
            self._i -= 1
        elif key == 'n':
            self._i += 5
        elif key == 'p':
            self._i -= 5
        elif key == '0':
            self._i = 0
        else:
            return key
