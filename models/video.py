import cv2

from .mixins import WaitKeyMixin


class Video(WaitKeyMixin):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        self._frame_index = self._index - 1
        self.get_frame()

    def get_frame(self):
        while self._index != self._frame_index:
            ret, self._frame_image = self.cap.read()
            if not ret:
                raise NotImplementedError("Video is not loaded")
            self._frame_index += 1
        self.is_opened = self.cap.isOpened()
        return self._frame_image

    def get_max_index(self):
        return 1e12

    def increase_goto_by(self, amount):
        if amount < 0:
            self._index += amount
            cap.set(cv2.CAP_PROP_POS_FRAMES, self._index)
        else:
            super().increase_goto_by(amount)
