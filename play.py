from pynput import mouse, keyboard
import mouse_clicker as mc
import time as time
import json
import sys
import win32api,win32con


actions = []

def get_mouseaction(button,dir)
    mouseaction = None
    if button=='left' and dir=='down':    
        mouseaction = win32con.MOUSEEVENTF_LEFTDOWN
    elif button=='left' and dir=='up':
        mouseaction = win32con.MOUSEEVENTF_LEFTUP
    elif button=='right' and dir=='down':
        mouseaction = win32con.MOUSEEVENTF_RIGHTDOWN
    elif button=='right' and dir=='up':
        mouseaction = win32con.MOUSEEVENTF_RIGHTUP
    return mouseaction


if __name__ == "__main__":
    if len(sys.argv)>1:
        filename = sys.argv[1]
    else:
        filename = rec.filename

    with open(filename, 'r') as f:
        actions = json.load(f)
    start_time = time.time()
    previous_time = 0
    for ac in actions:
        if previous_time>0:#skip first sleep
            time.sleep(ac['timestamp'] - previous_time)
        print(f'recent action:{ac}')
        if ac['source']=='mouse':
            x = ac['x']
            y = ac['y']
            mouseaction = get_mouseaction(ac['button'],ac['dir'])
            win32api.SetCursorPos((x,y))
            win32api.mouse_event(mouseaction,x,y,0,0)
        previous_time = ac['timestamp']
    print('Stop')