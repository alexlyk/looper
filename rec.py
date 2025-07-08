from pynput import mouse, keyboard
import mouse_clicker as mc
import time as time
import ctypes
import json
import sys
import string
import os
from pathlib import Path

# Попытка импорта PIL для скриншотов
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    print("Внимание: PIL (Pillow) не установлен. Скриншоты будут отключены.")
    print("Для установки выполните: pip install pillow")
    PIL_AVAILABLE = False


def get_layout():
    """Возвращает идентификатор текущей раскладки клавиатуры"""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    pid = ctypes.c_ulong()
    tid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    hkl = ctypes.windll.user32.GetKeyboardLayout(tid)
    lid = hkl & 0xffff
    return format(lid, '04x')

def get_monitor_info():
    """Получает информацию о всех мониторах"""
    try:
        from win32api import GetSystemMetrics
        from win32con import SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN
        
        # Получаем границы виртуального экрана (все мониторы)
        x = GetSystemMetrics(SM_XVIRTUALSCREEN)
        y = GetSystemMetrics(SM_YVIRTUALSCREEN)
        width = GetSystemMetrics(SM_CXVIRTUALSCREEN)
        height = GetSystemMetrics(SM_CYVIRTUALSCREEN)
        
        return (x, y, width, height)
    except ImportError:
        # Если win32api недоступен, используем только основной монитор
        return None

def get_monitor_from_cursor(cursor_x, cursor_y):
    """Определяет монитор, на котором находится курсор"""
    try:
        import win32api
        import win32gui
        
        # Получаем список всех мониторов
        monitors = []
        
        def monitor_enum_proc(hmon, hdc, rect, data):
            monitors.append(rect)
            return True
        
        win32api.EnumDisplayMonitors(None, None, monitor_enum_proc, None)
        
        # Находим монитор, содержащий курсор
        for i, (left, top, right, bottom) in enumerate(monitors):
            if left <= cursor_x < right and top <= cursor_y < bottom:
                return (left, top, right - left, bottom - top), i
        
        # Если не найден, возвращаем первый монитор
        if monitors:
            left, top, right, bottom = monitors[0]
            return (left, top, right - left, bottom - top), 0
            
    except ImportError:
        pass
    
    return None, 0

def take_screenshot(action_dir, screen_counter, cursor_x=None, cursor_y=None):
    """Создает скриншот и возвращает имя файла"""
    if not PIL_AVAILABLE:
        return None
    
    screenshot_name = f"{screen_counter}.png"
    screenshot_path = action_dir / screenshot_name
    
    try:
        # Получаем позицию курсора, если не передана
        if cursor_x is None or cursor_y is None:
            cursor_x, cursor_y = mc.get_cursor_coordinates()
        
        # Пытаемся определить монитор с курсором
        monitor_info, monitor_index = get_monitor_from_cursor(cursor_x, cursor_y)
        
        if monitor_info:
            # Делаем скриншот конкретного монитора
            x, y, width, height = monitor_info
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            print(f"Скриншот монитора {monitor_index + 1} ({width}x{height})")
        else:
            # Получаем информацию о виртуальном экране (все мониторы)
            virtual_screen = get_monitor_info()
            
            if virtual_screen:
                # Делаем скриншот всех мониторов
                x, y, width, height = virtual_screen
                screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                print(f"Скриншот всех мониторов ({width}x{height})")
            else:
                # Fallback: скриншот по умолчанию
                screenshot = ImageGrab.grab()
                print("Скриншот основного монитора")
        
        screenshot.save(screenshot_path)
        return screenshot_name
        
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        try:
            # Fallback: простой скриншот всего экрана
            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_path)
            print("Использован fallback скриншот")
            return screenshot_name
        except Exception as e2:
            print(f"Ошибка fallback скриншота: {e2}")
            return None

# Глобальные переменные для записи
actions = []
filename = 'actions.json'
start_time = None
action_directory = None
screen_counter = 0

# Обработчик события нажатия мыши
def on_click(x, y, button, pressed):
    global screen_counter
    
    if (button == mouse.Button.left or button == mouse.Button.right):
        x, y = mc.get_cursor_coordinates()
        
        toAdd = {
            'source': 'mouse',
            'button': 'left' if button == mouse.Button.left else 'right',
            'dir': 'down' if pressed else 'up',
            'x': x,
            'y': y,
            'timestamp': time.time() - start_time
        }
        
        # Для активного действия (нажатие мыши) создаем скриншот
        if pressed:  # только при нажатии (down), не при отпускании
            screen_counter += 1
            screenshot_name = take_screenshot(action_directory, screen_counter, x, y)
            if screenshot_name:
                toAdd['screen'] = screenshot_name
        
        actions.append(toAdd)
        print(toAdd)



# Обработчик события нажатия клавиши
def on_press(key):
    global screen_counter
    
    # always allow ESC to stop
    if key == keyboard.Key.esc:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(actions, f, ensure_ascii=False, indent=4)
        print(f'Запись сохранена в файл: {filename}')
        return False

    # record Enter explicitly
    if key == keyboard.Key.enter:
        screen_counter += 1
        cursor_x, cursor_y = mc.get_cursor_coordinates()
        screenshot_name = take_screenshot(action_directory, screen_counter, cursor_x, cursor_y)
        
        toAdd = {
            'source': 'keyboard',
            'key': 'enter',
            'timestamp': time.time() - start_time,
            'layout': get_layout()
        }
        
        if screenshot_name:
            toAdd['screen'] = screenshot_name
            
        actions.append(toAdd)
        print(toAdd)
        return

    # record space explicitly
    if key == keyboard.Key.space:
        screen_counter += 1
        cursor_x, cursor_y = mc.get_cursor_coordinates()
        screenshot_name = take_screenshot(action_directory, screen_counter, cursor_x, cursor_y)
        
        toAdd = {
            'source': 'keyboard',
            'key': 'space',
            'timestamp': time.time() - start_time,
            'layout': get_layout()
        }
        
        if screenshot_name:
            toAdd['screen'] = screenshot_name
            
        actions.append(toAdd)
        print(toAdd)
        return

    # ignore other special Keys without .char
    try:
        char = key.char
    except AttributeError:
        return

    # record all printable characters (letters, digits, punctuation, symbols…)
    if char and char.isprintable():
        toAdd = {
            'source': 'keyboard',
            'key': char,
            'timestamp': time.time() - start_time,
            'layout': get_layout()
        }
        actions.append(toAdd)
        print(toAdd)


def record_user_actions(log_file_path):
    """
    Основная функция для записи действий пользователя.
    Вызывается из looper.py
    
    Args:
        log_file_path (str): Путь к файлу лога (включая имя файла)
    """
    global actions, filename, start_time, action_directory, screen_counter
    
    # Инициализация
    actions = []
    filename = log_file_path
    start_time = time.time()
    screen_counter = 0
    
    # Определяем директорию для скриншотов (та же директория, где log.json)
    action_directory = Path(log_file_path).parent
    action_directory.mkdir(exist_ok=True)
    
    print("Запись действий начата. Нажмите ESC для завершения записи.")
    print("Активные действия (клики мыши, enter, space) будут сопровождаться скриншотами.")
    print("Поддержка нескольких мониторов: скриншоты будут делаться для монитора с курсором.")
    
    # Проверим доступность библиотек для работы с мониторами
    try:
        import win32api
        print("Библиотека win32api доступна - полная поддержка мониторов.")
    except ImportError:
        print("Библиотека win32api недоступна - будут использоваться базовые скриншоты.")
    
    try:
        # Запуск слушателей
        with mouse.Listener(on_click=on_click) as mouse_listener, \
             keyboard.Listener(on_press=on_press) as keyboard_listener:
            keyboard_listener.join()
    except Exception as e:
        print(f"Ошибка при записи действий: {e}")
        raise

if __name__ == "__main__":
    # Тестовый запуск для отладки
    print('Включите английскую раскладку для лучшей совместимости!')
    
    test_filename = 'test_actions.json'
    if len(sys.argv) > 1:
        test_filename = sys.argv[1]
    
    record_user_actions(test_filename)
    print('Запись завершена')