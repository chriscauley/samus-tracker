import cv2

from .mixins import WaitKeyMixin


class Video(WaitKeyMixin):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        self._frame_index = self._index - 1
        self.get_frame()

    def get_frame(self, frame_id=None):
        if frame_id == None:
            frame_id = self._index
        if frame_id == 0:
            # opencv is 1 indexed, so we'll just return the first frame
            frame_id = 1
        if self._frame_index != frame_id:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
            self._frame_index = frame_id
            ret, self._frame_image = self.cap.read()
            if not ret:
                raise NotImplementedError("Video is not loaded")
        return self._frame_image

    def get_current_time(self):
        return self.cap.get(cv2.CAP_PROP_POS_MSEC)

    def get_max_index(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

    def increase_goto_by(self, amount):
        if amount < 0:
            self._index += amount
            cap.set(cv2.CAP_PROP_POS_FRAMES, self._index)
        else:
            super().increase_goto_by(amount)
