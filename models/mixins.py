import urcv


class WaitKeyMixin:
    def __init__(self, *args, **kwargs):
        self._index = 0

    def wait_key(self):
        key = urcv.wait_key()
        if key == 'q':
            self._index = self.get_max_index() + 1
        elif key == 'f':
            self._index += 1
        elif key == 'b':
            self._index -= 1
        elif key == 'n':
            self._index += 5
        elif key == 'p':
            self._index -= 5
        elif key == '0':
            self._index = 0
        else:
            return key

    def get_max_index(self):
        raise NotImplementedError()