from setup import get_video_from_argv
import cv2
import numpy as np
import sys

from Video import Video
from unrest.utils import JsonCache
import urcv


def main(video):
    current_title = None
    while video._i < len(video.frames):
        if not 'timer_bounds' in video.config:
            frame = video.get_frame(video._i)
            video.config['timer_bounds'] = urcv.get_scaled_roi(frame, 4)
        if not 'game_bounds' in video.config:
            frame = video.get_frame(video._i)
            video.config['game_bounds'] = urcv.get_scaled_roi(frame, 3)

        frame = video.get_game_content(video._i)
        result = frame.copy()
        if 'item_bounds' in video.config and video._i in video.data['item_frames']:
            x, y, w, h = video.config['item_bounds']
            cv2.rectangle(result, (x,y),(x+w,y+h),(255, 0, 0),2)

        frame_h, frame_w = frame.shape[:-1]
        item_count = len([i for i in video.data["item_frames"] if i <= video._i])
        text = f'{video._i} - {item_count}'
        cv2.putText(result, text, (5, frame_h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

        cv2.imshow('result', result)
        key = video.wait_key()
        if key == '[':
            video.config['item_bounds'] = urcv.get_scaled_roi(result, 4)
        elif key == 'i':
            for i in video.data['item_frames']:
                if i > video._i:
                    video._i = i
                    break
        elif key == 'j':
            for i in video.data['item_frames'][::-1]:
                if i < video._i:
                    video._i = i
                    break
        elif key == '\r':
            if video._i in video.data['item_frames']:
                video.data['item_frames'].remove(video._i)
                video.data._save()
            else:
                video.data['item_frames'].append(video._i)
                video.data['item_frames'] = sorted(video.data['item_frames'])
if __name__ == "__main__":
    main(get_video_from_argv())
