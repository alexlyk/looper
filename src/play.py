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
from config import get_config
import mouse_clicker as mc

# Попытка импорта PIL для скриншотов
try:
    from PIL import ImageGrab,Image,ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    print("Внимание: PIL (Pillow) не установлен. Скриншоты будут отключены.")
    print("Для установки выполните: pip install pillow")
    PIL_AVAILABLE = False
    

# Глобальная переменная для отслеживания прерывания
stop_playback = False

def on_key_press(key):
    """Обработчик нажатий клавиш для прерывания воспроизведения"""
    global stop_playback
    if key == keyboard.Key.esc:
        print("\nПолучен сигнал прерывания (ESC). Останавливаем воспроизведение...")
        stop_playback = True
        return False  # Останавливаем слушатель


def execute_mouse_click(action, dynamic=False, action_dir=None):
    """Выполняет клик мышью"""
    x = action.get('x', 0)
    y = action.get('y', 0)
    button = action.get('button', 'left')
    
    if dynamic and 'screen' in action and action_dir:
        # Динамический режим - ищем координаты по референсному прямоугольнику
        screen_file = action.get('screen', '')
        rr_file = screen_file.replace('.png', '_rr.png')
        rr_path = action_dir / rr_file
        
        if not rr_path.exists():
            # Создаем референсный прямоугольник если его нет
            bounds = mc.get_virtual_screen_bounds()
            _x = x - bounds['min_x']
            _y = y - bounds['min_y'] 
            create_reference_rectangle(action_dir / screen_file, rr_path, _x, _y)
        
        # Ищем референсный прямоугольник на экране
        found_coords = find_reference_rectangle_on_screen(rr_path)
        if found_coords:
            _x, _y = found_coords
            x = _x + bounds['min_x']
            y = _y + bounds['min_y']
            print(f"Динамический режим: найден референсный прямоугольник в ({x}, {y})")
        else:
            print(f"Динамический режим: референсный прямоугольник {rr_path} не найден. Останавливаем исполнение сценария.")# используем исходные координаты ({x}, {y})")
            return False
    


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

    return True


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


def create_reference_rectangle(source_image_path, output_path, center_x, center_y, size=50):
    """Создает референсный прямоугольник размером 50x50 с центром в указанных координатах"""
    if not PIL_AVAILABLE:
        print("Внимание: PIL не доступен, референсный прямоугольник не может быть создан")
        return False
    
    try:
        if not source_image_path.exists():
            print(f"Исходное изображение не найдено: {source_image_path}")
            return False
        
        # Загружаем исходное изображение
        image = Image.open(source_image_path)
        
        # Вычисляем координаты прямоугольника
        half_size = size // 2
        left = max(0, center_x - half_size)
        top = max(0, center_y - half_size)
        right = min(image.width, center_x + half_size)
        bottom = min(image.height, center_y + half_size)
        
        # Вырезаем прямоугольник
        reference_rect = image.crop((left, top, right, bottom))
        
        # Сохраняем
        reference_rect.save(output_path)
        print(f"Создан референсный прямоугольник: {output_path}")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании referencer rectangle: {e}")
        return False


def find_reference_rectangle_on_screen(rr_path, timeout=15, threshold=0.9):
    """Ищет референсный прямоугольник на экране"""
    if not rr_path.exists():
        print(f"Файл референсного прямоугольника не найден: {rr_path}")
        return None
    
    template = cv2.imread(str(rr_path), cv2.IMREAD_COLOR)
    if template is None:
        print(f"Не удалось загрузить референсный прямоугольник: {rr_path}")
        return None
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Получаем скриншот экрана
        screenshot = take_screenshot()
        if screenshot is None:
            time.sleep(0.1)
            continue
        
        # Ищем шаблон на скриншоте
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCORR_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # Возвращаем центр найденного прямоугольника
            template_h, template_w = template.shape[:2]
            center_x = max_loc[0] + template_w // 2
            center_y = max_loc[1] + template_h // 2
            print(f"Референсный прямоугольник {rr_path} найден в центре ({center_x}, {center_y}) с совпадением {max_val:.3f}")

            # check other location

            # Create a draw object for the screenshot
            draw = ImageDraw.Draw(screenshot)

            # Get the coordinates from max_loc
            top_left_x, top_left_y = max_loc
            bottom_right_x = top_left_x + template_w
            bottom_right_y = top_left_y + template_h

            # Draw rectangle at the max_loc position
            draw.rectangle(
                [
                    (top_left_x, top_left_y),
                    (bottom_right_x, bottom_right_y)
                ],
                outline="red", width=3,fill="yellow"
            )
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            result2 = cv2.matchTemplate(screen, template, cv2.TM_CCORR_NORMED)
            _, max_val2, _, max_loc2 = cv2.minMaxLoc(result2)
            if max_val2>= threshold and max_val - max_val2<0.0001:
                print(f'Внимание! Найдено несколько референсных прямоугольников для {rr_path}.')
                print(f'max_val = {max_val}, max_val2 = {max_val2}')

            return (center_x, center_y)
        
        # Ждем 100ms как указано в концепции
        time.sleep(0.1)
    
    print(f"Референсный прямоугольник не найден в течение {timeout} секунд")
    return None


def execute_wait(action):
    """Выполняет ожидание"""
    global stop_playback
    
    # Упрощенная структура wait согласно новой концепции
    if 'time' in action:
        # Новый формат: прямо указано время
        wait_time = action.get('time', 1.0)
        print(f"Ожидание {wait_time} секунд")
        
        # Разбиваем длительное ожидание на короткие интервалы для возможности прерывания
        elapsed = 0
        interval = 0.1  # Проверяем каждые 100ms
        while elapsed < wait_time and not stop_playback:
            sleep_time = min(interval, wait_time - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time
            
    elif 'event' in action:
        # Старый формат для совместимости
        event = action.get('event', {})
        event_name = event.get('name', 'timer')
        
        if event_name == 'timer':
            wait_time = event.get('time', 1.0)
            print(f"Ожидание {wait_time} секунд")
            
            # Разбиваем длительное ожидание на короткие интервалы для возможности прерывания
            elapsed = 0
            interval = 0.1  # Проверяем каждые 100ms
            while elapsed < wait_time and not stop_playback:
                sleep_time = min(interval, wait_time - elapsed)
                time.sleep(sleep_time)
                elapsed += sleep_time
                
        elif event_name == 'picOnScreen':
            pic_file = event.get('file', '')
            print(f"Ожидание появления изображения: {pic_file}")
            wait_for_image_on_screen(pic_file)
        else:
            print(f"Неизвестный тип события: {event_name}")
    else:
        print("Действие wait без указания времени или события")


def wait_for_image_on_screen(image_file, timeout=30, threshold=0.8):
    """Ждет появления изображения на экране"""
    global stop_playback
    
    if not Path(image_file).exists():
        print(f"Файл изображения не найден: {image_file}")
        return False
    
    template = cv2.imread(image_file, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Не удалось загрузить изображение: {image_file}")
        return False
    
    start_time = time.time()
    
    while time.time() - start_time < timeout and not stop_playback:
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
    
    if stop_playback:
        print("Ожидание изображения прервано")
        return False
    
    print(f"Изображение не найдено в течение {timeout} секунд")
    return False


def take_screenshot():
    """Делает скриншот экрана"""
    try:
        import pyautogui
        screenshot = ImageGrab.grab(all_screens=True)
        return screenshot
    except ImportError:
        print("Для работы с изображениями требуется установить pyautogui: pip install pyautogui")
        return None
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return None


def create_actions_base_if_needed(action_name, actions_file=None):
    """Создает actions_base.json из log.json если его нет"""
    cfg = get_config()
    
    # Если actions_file не указан, используем стандартный путь
    if actions_file is None:
        actions_file = cfg.get_actions_base_file_path(action_name)
    else:
        actions_file = Path(actions_file)
        # Если путь не абсолютный, делаем его относительно папки действия
        if not actions_file.is_absolute():
            action_dir = cfg.get_action_path(action_name)
            actions_file = action_dir / actions_file
    
    # Если файл уже существует, ничего не делаем
    if actions_file.exists():
        return True
    
    # Проверяем, что это файл actions_base.json - только для стандартного файла создаем автоматически
    if actions_file.name != 'actions_base.json':
        return False
    
    # Получаем путь к log.json через конфигурацию
    log_file = cfg.get_log_file_path(action_name)
    
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


def play_actions(action_name, actions_file=None, dynamic=False):
    """Основная функция воспроизведения действий"""
    global stop_playback
    
    # Сбрасываем флаг прерывания
    stop_playback = False
    
    # Получаем конфигурацию
    cfg = get_config()
    action_dir = cfg.get_action_path(action_name)
    
    # Если actions_file не указан, используем стандартный путь
    if actions_file is None:
        actions_file = cfg.get_actions_base_file_path(action_name)
    else:
        actions_file = Path(actions_file+'.json')
        # Если путь не абсолютный, делаем его относительно папки действия
        if not actions_file.is_absolute():
            actions_file = action_dir / actions_file
    
    print(f"Воспроизведение действия '{action_name}'")
    print(f"Файл действий: {actions_file}")
    if dynamic:
        print("Динамический режим: будет использоваться поиск по референсным прямоугольникам")
    
    # Пробуем создать actions_base.json если его нет
    if not actions_file.exists():
        if not create_actions_base_if_needed(action_name, actions_file):
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
    print("Нажмите ESC для прерывания воспроизведения")
    
    # Запускаем слушатель клавиатуры в отдельном потоке
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()
    
    time.sleep(3)
    
    for i, action in enumerate(actions):
        # Проверяем флаг прерывания перед каждым действием
        if stop_playback:
            print("Воспроизведение прервано пользователем")
            break
            
        action_name = action.get('name', 'unknown')
        print(f"[{i+1}/{len(actions)}] Выполняем действие: {action_name}")
        
        try:
            if action_name in ['click left', 'click right']:
                if not execute_mouse_click(action, dynamic, action_dir):
                    break
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
    
    # Останавливаем слушатель клавиатуры
    listener.stop()
    
    if stop_playback:
        print("Воспроизведение было прервано")
    else:
        print("Воспроизведение завершено")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        action_name = sys.argv[1]
    else:
        print("Использование: python play.py <имя_действия>")
        print("Например: python play.py open_notepad")
        sys.exit(1)
    
    success = play_actions(action_name)
    if not success:
        sys.exit(1)