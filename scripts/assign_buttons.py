import cv2
import numpy as np
from Video import Video
from unrest.utils import JsonCache
import urcv


def main(video_id):
    video = Video(video_id)
    frames = video.frames
    _i = 0
    while True:
        _i = _i % len(frames)
        frame = video.get_game_content(_i).copy()
        buttons = video.get_buttons_pressed(_i)
        urcv.text.write(frame, '+'.join(buttons))
        cv2.imshow('frame', frame)
        pressed = urcv.wait_key()
        if pressed == 'f':
            _i += 1
        elif pressed == 'b':
            _i -= 1
        elif pressed == 'n':
            _i += 10
        elif pressed == 'p':
            _i -= 10
        elif pressed == 'u':
            bounds = urcv.get_scaled_roi(frame, 3)
            name = input("What is th name for this region?")
            video.config['bounds'][name] = bounds
            video.config._save()
        elif pressed == 'q':
            break

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
