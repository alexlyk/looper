from pynput import mouse, keyboard
import mouse_clicker as mc
import time as time
import ctypes

def get_layout():
    # return current keyboard layout identifier (hex) of active window
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    pid = ctypes.c_ulong()
    tid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    hkl = ctypes.windll.user32.GetKeyboardLayout(tid)
    lid = hkl & 0xffff
    return format(lid, '04x')
    
import json
import sys
import string

actions = []
filename = 'actions.json'
start_time = time.time()

# Обработчик события нажатия мыши
def on_click(x, y, button, pressed):
    if (button == mouse.Button.left or button == mouse.Button.right):
        x, y = mc.get_cursor_coordinates()
        toAdd = {
            'source':'mouse',
            'button':'left' if button == mouse.Button.left else 'right',
            'dir': 'down' if pressed else 'up',
            'x':x,
            'y':y,
            'timestamp':time.time() - start_time
        }
        actions.append(toAdd)
        print(toAdd)



# Обработчик события нажатия клавиши
def on_press(key):
    # always allow ESC to stop
    if key == keyboard.Key.esc:
        with open(filename,'w') as f:
            json.dump(actions, f, ensure_ascii=False, indent=4)
        print(f'Write to filename:{filename}')
        return False

    # record Enter explicitly
    if key == keyboard.Key.enter:
        toAdd = {
            'source':   'keyboard',
            'key':      '\n',
            'timestamp': time.time() - start_time,
            'layout':    get_layout()
        }
        actions.append(toAdd)
        print(toAdd)
        return

    # record space explicitly
    if key == keyboard.Key.space:
        toAdd = {
            'source':   'keyboard',
            'key':      ' ',
            'timestamp': time.time() - start_time,
            'layout':    get_layout()
        }
        actions.append(toAdd)
        print(toAdd)
        return

    # ignore other special Keys without .char
    try:
        char = key.char
    except AttributeError:
        return

    # record all printable characters (letters, digits, punctuation, symbols…)
    if char.isprintable():
        toAdd = {
            'source':   'keyboard',
            'key':      char,
            'timestamp': time.time() - start_time,
            'layout':    get_layout()
        }
        actions.append(toAdd)
        print(toAdd)

if __name__ == "__main__":
    # switch to English layout via Alt+Shift using pynput
    # controller = keyboard.Controller()
    # controller.press(keyboard.Key.ctrl_l)
    # controller.press(keyboard.Key.shift)
    # controller.release(keyboard.Key.shift)
    # controller.release(keyboard.Key.ctrl_l)
    print('Включи английскую раскладку!')
    if len(sys.argv)>1:
        filename = sys.argv[1]

    
    # Запуск слушателей
    with mouse.Listener(on_click=on_click) as mouse_listener, keyboard.Listener(on_press=on_press) as keyboard_listener:
        keyboard_listener.join()
    
    print('Stop')