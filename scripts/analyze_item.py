import cv2
import sys
import urcv

import Template
from Video import Video

def main(youtube_id):
    Template.init()
    video = Video(youtube_id)
    _i = 0
    for frame_number in video.data['item_frames']:
        assigned_name = video.get_item_name(frame_number)
        if assigned_name:
            frame_name = video.get_item_content(frame_number)
            Template.create(youtube_id, frame_number, assigned_name, frame_name)
    while True:
        _i = _i % len(video.data['item_frames'])
        frame_number = video.data['item_frames'][_i]
        frame = video.get_game_content(frame_number)
        frame_name = video.get_item_content(frame_number)
        cv2.imshow('frame', frame)
        cv2.imshow('name', frame_name)
        assigned_name = video.get_item_name(frame_number)
        print(f"\n@{frame_number}: {assigned_name}")
        matches = Template.match_all(frame_name)
        for val, loc, item_name, template in matches:
            print(f'matched: {val}@{item_name}')
        if matches:
            cv2.imshow('best match', matches[-1][3])
        cv2.waitKey(100)
        pressed = input("What do?")
        if len(pressed) > 1:
            pressed = pressed.lower().replace(" ", "-")
            video.set_item_name(frame_number, pressed)
            print(f"Set frame {frame_number} to {video.get_item_name(frame_number)}")
            Template.create(youtube_id, frame_number, pressed, frame_name)
        elif pressed == 'q':
            break
        elif pressed == 'x':
            video.set_item_name(frame_number, None)
        elif pressed == '0':
            _i = 0
        elif not pressed or pressed == 'f':
            _i += 1
        elif pressed == 'b':
            _i -= 1

if __name__ == "__main__":
    main(sys.argv[1])