from setup import get_video_from_argv
import Video

def main(video):
    actions = []
    down = {}
    for _i in range(len(video.frames)):
        pressed = video.get_buttons_pressed(_i)
        for button in pressed:
            if not button in down:
                down[button] = _i
        for button in list(down.keys()):
            if not button in pressed:
                actions.append({
                    'button': button,
                    'start': down[button],
                    'end': _i,
                })
                down.pop(button)
    for action in sorted(actions, key=lambda a: a['start']):
        a = [action[key] for key in ('button', 'start', 'end')]
        print(f'{repr(a)},')


if __name__ == "__main__":
    main(get_video_from_argv())