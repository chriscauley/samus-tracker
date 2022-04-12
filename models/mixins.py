import numpy as np
import time

import urcv


class WaitKeyMixin:
    def __init__(self, *args, **kwargs):
        self._index = 0
        self.goto = None
        self._last_tick = time.time()

    # TODO make this getter/setter property on goto
    def increase_goto_by(self, amount):
        self.goto_sign = np.sign(amount)
        self.goto = self._index + amount
        self.goto = self.goto % self.get_max_index()
        print(f'going to {self.goto} (delta={amount})')

    @property
    def busy(self):
        return self.goto != None

    def wait_key(self):
        if self.goto is not None:
            delta = self.goto - self._index
            if abs(delta) > 10 and self._index % 100 == 99:
                print('goto... ', self._index + 1, int(1000*(time.time()-self._last_tick)))
                self._last_tick = time.time()
            self._index += self.goto_sign
            if self.goto == self._index:
                self.goto = None
            self._index = self._index % self.get_max_index()
            return
        key = urcv.wait_key()
        if key == 'right':
            self._index += 1
        elif key == 'left':
            self._index -= 1
        elif key == 'down':
            self.increase_goto_by(-10)
        elif key == 'up':
            self.increase_goto_by(10)
        elif key == ',':
            self.increase_goto_by(-100)
        elif key == '.':
            self.increase_goto_by(100)
        elif key == '<':
            self.increase_goto_by(-1000)
        elif key == '>':
            self.increase_goto_by(1000)
        elif key == '0':
            self._index = 0
        elif key == '/':
            self.increase_goto_by(self.get_max_index() - self._index - 1)
            print("Goint to end:", self.goto)
        elif key == 'g':
            while True:
                s = input("Go to what index?")
                if s.isdigit():
                    self.increase_goto_by(int(s) - self._index)
                    break
        else:
            return key
        self._index = self._index % self.get_max_index()


    def get_max_index(self):
        raise NotImplementedError()
