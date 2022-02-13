import cv2
import numpy as np
import sys

from Video import Video
from unrest.utils import JsonCache
import urcv


def main(youtube_id):
    video = Video(youtube_id)
    current_title = None
    _i = 0
    while True:
        _i = _i % len(video.frames)
        _i = _i
        if not 'timer_bounds' in video.config:
            frame = video.get_frame(_i)
            video.config['timer_bounds'] = urcv.get_scaled_roi(frame, 4)
        if not 'game_bounds' in video.config:
            frame = video.get_frame(_i)
            video.config['game_bounds'] = urcv.get_scaled_roi(frame, 3)

        frame = video.get_game_content(_i)
        result = frame.copy()
        if 'item_bounds' in video.config and _i in video.data['item_frames']:
            x, y, w, h = video.config['item_bounds']
            cv2.rectangle(result, (x,y),(x+w,y+h),(255, 0, 0),2)

        frame_h, frame_w = frame.shape[:-1]
        item_count = len([i for i in video.data["item_frames"] if i <= _i])
        text = f'{_i} - {item_count}'
        cv2.putText(result, text, (5, frame_h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

        cv2.imshow('result', result)
        key = urcv.wait_key()
        if key == 'q':
            break
        elif key == '[':
            video.config['item_bounds'] = urcv.get_scaled_roi(result, 4)
        elif key == 'f':
            _i += 1
        elif key == 'b':
            _i -= 1
        elif key == 'n':
            _i += 5
        elif key == 'p':
            _i -= 5
        elif key == '0':
            _i = 0
        elif key == 'i':
            for i in video.data['item_frames']:
                if i > _i:
                    _i = i
                    break
        elif key == 'j':
            for i in video.data['item_frames'][::-1]:
                if i < _i:
                    _i = i
                    break
        elif key == '\r':
            if _i in video.data['item_frames']:
                video.data['item_frames'].remove(_i)
                video.data._save()
            else:
                video.data['item_frames'].append(_i)
                video.data['item_frames'] = sorted(video.data['item_frames'])
        else:
            print('unknown key', repr(key))
if __name__ == "__main__":
    main(sys.argv[1])
