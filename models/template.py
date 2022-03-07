import cv2
import numpy as np
from pathlib import Path
import urcv

def noop(a, *args, **kwargs):
    return a

def _thresh_pause(image):
    return urcv.transform.threshold(image, 244)

class Template:
    def __init__(self, world, processes={}):
        self.dirs = { 'root': Path('.cache/templates/'+world) }
        self.scale_ratio = 1
        self._raw = {}
        self._template = {}
        self.processes = {
            'ui': { 'pause': _thresh_pause },
            **processes,
        }
        for category in ['item', 'zone', 'ui']:
            self.dirs[category] = self.dirs['root'] / category
            self.dirs[category].mkdir(exist_ok=True, parents=True)
            self._raw[category] = {}
            self._template[category] = {}
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

    def search(self, image, category, names=[], show=False, threshold=0.9):
        names = names or self._raw[category].keys()
        for name in names:
            func = self.processes.get(category, {}).get(name) or noop
            target = func(image)
            template = self._template[category][name]
            coords = urcv.template.match(target, template, threshold=threshold)
            if show:
                cv2.imshow(name, template)
                cv2.imshow(name +" target", target)
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
            self._template[category][name] = self._raw[category][name]
        else:
            self._template[category][name] = urcv.transform.scale(
                self._raw[category][name],
                self.scale_ratio,
                interpolation=cv2.INTER_LINEAR,
            )
        self._process(category, name)

    def _process(self, category, name):
        func = self.processes.get(category, {}).get(name)
        if func:
            self._template[category][name] = func(self._template[category][name])

    def save_from_frame(self, category, frame):
        h, w = frame.shape[:2]
        scale = 2 if w < 600 else 1
        x, y, w, h = urcv.input.get_scaled_roi(frame, scale)
        name = input("what is this? ")
        self.save(category, name, frame[y:y+h,x:x+w])

    def show_all(self, category):
        for name, image in self._raw[category].items():
            _processed = self._template[category][name]
            cv2.imshow(name, image)
            cv2.imshow(name+' processed', _processed)