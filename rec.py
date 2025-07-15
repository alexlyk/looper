from pynput import mouse, keyboard
import mouse_clicker as mc
import time as time
import ctypes
import json
import sys
import string
import os
import shutil
from pathlib import Path
from config import get_config

# Попытка импорта PIL для скриншотов
try:
    from PIL import ImageGrab,Image,ImageDraw
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

def take_screenshot(action_dir, screen_counter):
    """Создает скриншот и возвращает имя файла"""
    if not PIL_AVAILABLE:
        return None
    
    screenshot_name = f"{screen_counter}.png"
    screenshot_path = action_dir / screenshot_name
    
    try:
        # Делаем скриншот всего экрана (всех мониторов)
        screenshot = ImageGrab.grab(all_screens=True)
        screenshot.save(screenshot_path)
        x, y = mc.get_cursor_coordinates()
        # draw cursor 
        draw = ImageDraw.Draw(screenshot)
        cursor_radius = 5  # радиус кружка-курсора
        draw.ellipse(
            [
                (x - cursor_radius, y - cursor_radius),
                (x + cursor_radius, y + cursor_radius)
            ],
            outline="red", width=2, fill="red"
        )
        screenshot_name_c = f"{screen_counter}_c.png"
        screenshot_path_c = action_dir / screenshot_name_c
        screenshot.save(screenshot_path_c)

        return screenshot_name
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return None

def clear_action_directory(directory_path):
    """
    Очищает директорию с действием перед началом записи.
    Удаляет все файлы и поддиректории внутри указанной папки.
    
    Args:
        directory_path (Path): Путь к директории для очистки
    """
    if directory_path.exists():
        print(f"Очистка существующей директории: {directory_path}")
        
        # Удаляем все содержимое директории
        for item in directory_path.iterdir():
            try:
                if item.is_file():
                    item.unlink()  # Удаляем файл
                    print(f"Удален файл: {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item)  # Удаляем директорию рекурсивно
                    print(f"Удалена папка: {item.name}")
            except Exception as e:
                print(f"Не удалось удалить {item.name}: {e}")
        
        print("Директория очищена.")

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
            screenshot_name = take_screenshot(action_directory, screen_counter)
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
        screenshot_name = take_screenshot(action_directory, screen_counter)
        
        toAdd = {
            'source': 'keyboard',
            'key': '\n',
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
        screenshot_name = take_screenshot(action_directory, screen_counter)
        
        toAdd = {
            'source': 'keyboard',
            'key': ' ',
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


def record_user_actions(action_name):
    """
    Основная функция для записи действий пользователя.
    Вызывается из looper.py
    
    Args:
        action_name (str): Имя действия (например, 'open_notepad')
    """
    global actions, filename, start_time, action_directory, screen_counter
    
    # Получаем конфигурацию
    cfg = get_config()
    
    # Определяем пути через конфигурацию
    action_directory = cfg.get_action_path(action_name)
    log_file_path = cfg.get_log_file_path(action_name)
    
    # Инициализация
    actions = []
    filename = str(log_file_path)
    start_time = time.time()
    screen_counter = 0
    
    print(f"Запись действия '{action_name}'")
    print(f"Директория действий: {action_directory}")
    print(f"Файл лога: {log_file_path}")
    
    # Очищаем директорию если она уже существует
    clear_action_directory(action_directory)
    
    # Создаем директорию заново
    action_directory.mkdir(parents=True, exist_ok=True)
    
    print("Запись действий начата. Нажмите ESC для завершения записи.")
    print("Активные действия (клики мыши, enter, space) будут сопровождаться скриншотами.")
    
    if not PIL_AVAILABLE:
        print("Внимание: Скриншоты отключены - PIL (Pillow) не установлен.")
    
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
    
    test_action_name = 'test_action'
    if len(sys.argv) > 1:
        test_action_name = sys.argv[1]
    
    record_user_actions(test_action_name)
    print('Запись завершена')