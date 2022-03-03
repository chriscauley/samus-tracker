import cv2
from inputs import get_gamepad, UnknownEventCode
import numpy as np
from mss import mss
from pathlib import Path
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import json
import time
import urcv
import sys

# define dimensions of screen w.r.t to given monitor to be captured
GAME_LEFT = 724 # min width of chrome window!
SCREEN_WIDTH = 1920
GAME_TOP = 64
GAME_HEIGHT = 960 - GAME_TOP # Taken from screenshot
GAME_WIDTH = SCREEN_WIDTH-GAME_LEFT
frames = []
options = {
    'left': GAME_LEFT,
    'width': GAME_WIDTH,
    'top': GAME_TOP,
    'height': GAME_HEIGHT,
}

WORLD = 'super-metroid'

class Template:
    def __init__(self, scale_ratio):
        self.dirs = { 'root': Path('.cache/templates/'+WORLD) }
        self.scale_ratio = scale_ratio
        self._raw = {}
        self._scaled = {}
        for category in ['item']:
            self.dirs[category] = self.dirs['root'] / 'item'
            self.dirs[category].mkdir(exist_ok=True)
            self._raw[category] = {}
            self._scaled[category] = {}
            for fname in self.dirs[category].iterdir():
                template_name = str(fname).split('/')[-1].split('.')[0]
                self._reload(category, template_name)


    def _reload(self, category, name):
        path = self.dirs[category] / f'{name}.png'
        gray = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2GRAY)
        self._raw[category][name] = gray
        self._scale(category, name)

    def save(self, category, name, image):
        path = self.dirs[category] / f'{name}.png'
        cv2.imwrite(str(path), image)
        self._reload(category, name)

    def search(self, image, category, names=[]):
        names = names or self._raw[category].keys()
        for name in names:
            template = self._scaled[category][name]
            coords = urcv.template.match(image, template, threshold=0.9)
            if coords:
                return name, coords
        return None, []

    def rescale(self, scale_ratio):
        self.scale_ratio = scale_ratio
        for category in self._raw:
            for name in self._raw[category]:
                self._scale(category, name)

    def _scale(self, category, name):
        self._scaled[category][name] = urcv.transform.scale(self._raw[category][name], self.scale_ratio, interpolation=cv2.INTER_LINEAR)

class Playthrough:
    def __init__(self, id):
        self.data = {
            'items': [],
            'duplicates': [],
            'frames': 0,
            'capture_rate': 250,
        }
        self.last = self._current = self._last_image = None
        self.id = id
        self.path = Path(f'.cache/playthroughs/{id}/')
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / 'items').mkdir(parents=True, exist_ok=True)
        (self.path / 'frames').mkdir(parents=True, exist_ok=True)
        self._data_json = self.path / 'data.json'
        if self._data_json.exists():
            self.data = json.loads(self._data_json.read_text())
    def touch(self, item_name, image):
        self.data['frames'] += 1
        cv2.imwrite(str(self.path / f'frames/{self.data["frames"]}.png'), image)
        if item_name and self._current != item_name:
            self.data['items'].append(item_name)
            self.last = item_name
            self._last_image = image
            self.save()
        self._current = item_name
    def save(self):
        self._data_json.write_text(json.dumps(self.data))
    def mark_duplicate(self, _id=None):
        _id = _id or len(self.data['items']) - 1
        if _id in self.data['duplicates']:
            self.data['duplicates'].remove(_id)
        else:
            self.data['duplicates'].append(_id)
        self.save()

    def is_last_duplicate(self):
        _id = len(self.data['items']) - 1
        return _id in self.data['duplicates']

with mss() as sct:
    scale = 0.5
    template = Template(1)
    playthrough = Playthrough(sys.argv[1])
    print('starting in 1 sec')
    time.sleep(1)

    while True:
        now = time.time()

        screenShot = sct.grab(options)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mini = urcv.transform.scale(frame, scale, interpolation=cv2.INTER_LINEAR)
        gray_mini = cv2.cvtColor(mini, cv2.COLOR_RGB2GRAY)

        frames.append(time.time())
        frames = [f for f in frames if f > time.time() - 5]

        item_name, coords = template.search(gray_mini, 'item')
        playthrough.touch(item_name, mini)
        for x1, y1, x2, y2 in coords:
            cv2.rectangle(mini, [x1, y1], [x2, y2], (255,0,0), 3)
            urcv.text.write(mini, item_name)
        if not coords:
            text = f'last: {playthrough.last}'
            if playthrough.is_last_duplicate():
                text += ' DUPLICATED'
            else:
                text += f' {len(playthrough.data["items"])}'
            urcv.text.write(mini, text)

        cv2.imshow('mini', mini)
        # cv2.imshow('gray_mini', gray_mini)
        capture_rate = playthrough.data['capture_rate']
        delay = int(capture_rate - (time.time() * 1000) % capture_rate)
        pressed = urcv.wait_key(max_time=1, delay=delay)
        if pressed == 'q':
            break
        if pressed == 'i':
            x, y, w, h = urcv.input.get_scaled_roi(mini, 2)
            result = mini[y:y+h,x:x+w]
            name = input("what is this? ")
            template.save('item', name, result)
        if pressed == 'd':
            playthrough.mark_duplicate()
