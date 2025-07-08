#!/usr/bin/env python3
"""
Модуль воспроизведения базовых действий
"""

import json
import time
import sys
import cv2
import numpy as np
from pathlib import Path
import win32api
import win32con
import win32gui
from pynput import keyboard


def execute_mouse_click(action):
    """Выполняет клик мышью"""
    x = action.get('x', 0)
    y = action.get('y', 0)
    button = action.get('button', 'left')
    
    print(f"Клик {button} кнопкой мыши в точке ({x}, {y})")
    
    # Устанавливаем курсор в нужную позицию
    win32api.SetCursorPos((x, y))
    
    # Выполняем клик
    if button == 'left':
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.05)  # Небольшая задержка между нажатием и отпусканием
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    elif button == 'right':
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)


def execute_typing(action):
    """Выполняет ввод текста"""
    text = action.get('text', '')
    print(f"Ввод текста: '{text}'")
    
    # Используем pynput для ввода текста
    kb = keyboard.Controller()
    kb.type(text)


def execute_enter():
    """Выполняет нажатие Enter"""
    print("Нажатие Enter")
    kb = keyboard.Controller()
    kb.press(keyboard.Key.enter)
    kb.release(keyboard.Key.enter)


def execute_space():
    """Выполняет нажатие Space"""
    print("Нажатие Space")
    kb = keyboard.Controller()
    kb.press(keyboard.Key.space)
    kb.release(keyboard.Key.space)


def execute_wait(action):
    """Выполняет ожидание"""
    event = action.get('event', {})
    event_name = event.get('name', 'timer')
    
    if event_name == 'timer':
        wait_time = event.get('time', 1.0)
        print(f"Ожидание {wait_time} секунд")
        time.sleep(wait_time)
    elif event_name == 'picOnScreen':
        pic_file = event.get('file', '')
        print(f"Ожидание появления изображения: {pic_file}")
        wait_for_image_on_screen(pic_file)
    else:
        print(f"Неизвестный тип события: {event_name}")


def wait_for_image_on_screen(image_file, timeout=30, threshold=0.8):
    """Ждет появления изображения на экране"""
    if not Path(image_file).exists():
        print(f"Файл изображения не найден: {image_file}")
        return False
    
    template = cv2.imread(image_file, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Не удалось загрузить изображение: {image_file}")
        return False
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Получаем скриншот экрана
        screenshot = take_screenshot()
        if screenshot is None:
            time.sleep(0.5)
            continue
        
        # Ищем шаблон на скриншоте
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            print(f"Изображение найдено в позиции {max_loc} с совпадением {max_val:.3f}")
            return True
        
        time.sleep(0.5)
    
    print(f"Изображение не найдено в течение {timeout} секунд")
    return False


def take_screenshot():
    """Делает скриншот экрана"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except ImportError:
        print("Для работы с изображениями требуется установить pyautogui: pip install pyautogui")
        return None
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return None


def create_actions_base_if_needed(actions_file):
    """Создает actions_base.json из log.json если его нет"""
    actions_path = Path(actions_file)
    
    # Если файл уже существует, ничего не делаем
    if actions_path.exists():
        return True
    
    # Проверяем, что это файл actions_base.json
    if actions_path.name != 'actions_base.json':
        return False
    
    # Ищем log.json в той же директории
    log_file = actions_path.parent / 'log.json'
    
    if not log_file.exists():
        print(f"Не найден файл лога: {log_file}")
        print("Для создания actions_base.json требуется файл log.json")
        return False
    
    print(f"Файл {actions_file} не найден.")
    print(f"Найден файл лога: {log_file}")
    print("Выполняем декомпозицию для создания базовых действий...")
    
    try:
        # Импортируем и вызываем функцию декомпозиции
        from decomposer import decompose_action
        action_name = actions_path.parent.name
        
        success = decompose_action(action_name)
        if success:
            print(f"Декомпозиция завершена. Файл {actions_file} создан.")
            return True
        else:
            print("Ошибка при декомпозиции")
            return False
            
    except ImportError:
        print("Ошибка: модуль decomposer.py не найден")
        return False
    except Exception as e:
        print(f"Ошибка при выполнении декомпозиции: {e}")
        return False


def play_actions(actions_file):
    """Основная функция воспроизведения действий"""
    # Пробуем создать actions_base.json если его нет
    if not Path(actions_file).exists():
        if not create_actions_base_if_needed(actions_file):
            print(f"Файл не найден: {actions_file}")
            return False
    
    try:
        with open(actions_file, 'r', encoding='utf-8') as f:
            actions = json.load(f)
    except FileNotFoundError:
        print(f"Файл не найден: {actions_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return False
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return False
    
    print(f"Загружено {len(actions)} действий из {actions_file}")
    print("Начинаем воспроизведение через 3 секунды...")
    time.sleep(3)
    
    for i, action in enumerate(actions):
        action_name = action.get('name', 'unknown')
        print(f"[{i+1}/{len(actions)}] Выполняем действие: {action_name}")
        
        try:
            if action_name in ['click left', 'click right']:
                execute_mouse_click(action)
            elif action_name == 'typing':
                execute_typing(action)
            elif action_name == 'enter':
                execute_enter()
            elif action_name == 'space':
                execute_space()
            elif action_name == 'wait':
                execute_wait(action)
            else:
                print(f"Неизвестное действие: {action_name}")
        
        except Exception as e:
            print(f"Ошибка при выполнении действия {action_name}: {e}")
            continue
    
    print("Воспроизведение завершено")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("Использование: python play.py <путь_к_файлу_действий>")
        sys.exit(1)
    
    success = play_actions(filename)
    if not success:
        sys.exit(1)