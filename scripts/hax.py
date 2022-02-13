from inputs import get_gamepad, UnknownEventCode
import time
# import keyboard
from pynput.keyboard import Key, Controller
import pyautogui


KEY_TO_CODE = {
    'R': 'BTN_TR',
    'Y': 'BTN_WEST',
    'X': 'BTN_NORTH',
    'A': 'BTN_SOUTH',
    'B': 'BTN_EAST',
}
controller = Controller()
def press(key):
    print('pressing', key)
    pyautogui.keyDown(key)
    time.sleep(0.1)
    print('releasing', key)
    pyautogui.keyUp(key)

CODE_TO_KEY = {}

for a,b in KEY_TO_CODE.items():
    CODE_TO_KEY[b] = a


def main():
    """Just print out some event infomation when the gamepad is used."""
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
                continue
            if key == 'R':
                r_down = bool(event.state)
                r_lock = False
                if event.state:
                    r_down = True
                else:
                    r_down = False
                continue
            if r_lock or not r_down:
                continue
            if event.state:
                r_lock = True
                if key == 'A':
                    press(' ')
                if key == 'B':
                    press('m')
                if key == 'X':
                    press('f2')
                if key == 'Y':
                    press('f4')


if __name__ == "__main__":
    main()