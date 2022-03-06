import cv2
import numpy as np
import urcv
from unrest.utils import time_it

class MotionDetector:
    def __init__(self):
        self._last = None
    @time_it
    def check(self, image, show=False):
        image = urcv.transform.scale(image, 1/2)
        b = g = r = total = 0

        if self._last is not None:
            old_shape = self._last.shape
            if self._last.shape != image.shape:
                # crop _last shape if bigger
                (h,w) = image.shape[:2]
                self._last = self._last[:h,:w]
            if self._last.shape != image.shape:
                # now expand _last if it's still not the same shape
                h, w = self._last.shape[:2]
                _new_last = np.zeros(image.shape, dtype=image.dtype)
                _new_last[:h,:w] = self._last
                self._last = _new_last
            if old_shape != self._last.shape:
                w = "WARNING: Motion dectetor reshaped image from {} to {}"
                print(w.format(old_shape, self._last.shape))
            diff = cv2.absdiff(image, self._last)
            if show:
                cv2.imshow('md diff', diff)
            b, g, r = [int(np.sum(c) / c.size) for c in cv2.split(diff)]
            total = b + g + r
        self._last = image
        return b, g, r, total