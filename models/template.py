import cv2
import numpy as np
from pathlib import Path
import urcv

class Template:
    def __init__(self, world ):
        self.dirs = { 'root': Path('.cache/templates/'+world) }
        self.scale_ratio = 1
        self._raw = {}
        self._scaled = {}
        for category in ['item']:
            self.dirs[category] = self.dirs['root'] / 'item'
            self.dirs[category].mkdir(exist_ok=True, parents=True)
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
        if self.scale_ratio == 1:
            self._scaled[category][name] = self._raw[category][name]
        else:
            self._scaled[category][name] = urcv.transform.scale(
                self._raw[category][name],
                self.scale_ratio,
                interpolation=cv2.INTER_LINEAR,
            )

    def save_from_frame(self, frame):
        h, w = frame.shape[:2]
        scale = 2 if w < 600 else 1
        x, y, w, h = urcv.input.get_scaled_roi(frame, scale)
        name = input("what is this? ")
        self.save('item', name, frame[y:y+h,x:x+w])
