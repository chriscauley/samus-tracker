from inputs import get_gamepad, UnknownEventCode
import time
# import keyboard
import pyautogui


KEY_TO_CODE = {
    'R': 'BTN_TR',
    'Y': 'BTN_WEST',
    'X': 'BTN_NORTH',
    'A': 'BTN_SOUTH',
    'B': 'BTN_EAST',
}
CODE_TO_KEY = {}

for a,b in KEY_TO_CODE.items():
    CODE_TO_KEY[b] = a

def press(key, text='pressed'):
    print(f'{key} {text}...', end="", flush=True)
    pyautogui.keyDown(key)
    time.sleep(0.1)
    print('done!', key)
    pyautogui.keyUp(key)


def split(key):
    # TODO get LiveSplitOne working locally so we can use https://pypi.org/project/livesplit/
    pyautogui.hotkey('alt', 'tab')
    pyautogui.press(key)
    pyautogui.hotkey('alt', 'tab')


def main():
    """Just print out some event infomation when the gamepad is used."""
    last_tap = 0
    r_down = False
    r_lock = False
    need_clear = False
    while 1:
        try:
            events = get_gamepad()
        except UnknownEventCode:
            continue
        for event in events:
            key = CODE_TO_KEY.get(event.code)
            if not key:
                # TODO add all to key map
                print('unknown code', event.code)
                continue
            if key == 'R':
                r_lock = False
                if event.state:
                    r_down = time.time()
                else:
                    duration = time.time() - r_down
                    if duration < 0.5:
                        if time.time() - last_tap < 0.5:
                            press('f2', 'saving')
                        else:
                            print('tappy...')
                            last_tap = time.time()
                    elif duration < 2:
                        press('f4', 'loading')
                    r_down = False

                continue

            # Every key after this is triggered when pressed
            if not event.state:
                continue

            if r_down and not r_lock:
                # Player must be holding r and press one of these
                r_lock = True
                if key == 'A':
                    press(' ')
                elif key == 'B':
                    press('m')


if __name__ == "__main__":
    main()