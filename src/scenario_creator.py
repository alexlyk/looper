#!/usr/bin/env python3
"""
Модуль для создания сценариев из базовых действий
"""

import json
import csv
import copy
import sys
from pathlib import Path
from config import get_config
import mouse_clicker as mc
from pynput import keyboard
import threading
import time


class ScenarioCreator:
    """Класс для создания и модификации сценариев"""
    
    def __init__(self, action_name):
        self.action_name = action_name
        self.config = get_config()
        self.base_actions = self._load_base_actions()
        self.next_id = self._get_next_id()
    
    def _load_base_actions(self):
        """Загружает базовые действия из файла"""
        actions_file = self.config.get_actions_base_file_path(self.action_name)
        
        if not actions_file.exists():
            raise FileNotFoundError(f"Файл базовых действий '{actions_file}' не найден")
        
        try:
            with open(actions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла действий: {e}")
    
    def _get_next_id(self):
        """Возвращает следующий доступный ID"""
        return max([action.get('id', 0) for action in self.base_actions], default=0) + 1
    
    
    def create_complex_scenario(self, output_name, delay=None, typing_params_file=None, 
                               sleep_time=3):
        """Создает комплексный сценарий с несколькими типами модификаций"""
        print(f"Создание комплексного сценария '{output_name}'...")
        
        # Загружаем параметры typing если указаны
        typing_data = None
        if typing_params_file:
            typing_data = self._load_typing_params(typing_params_file)
        
        # Если есть typing_data, создаем несколько сценариев
        scenarios_count = len(typing_data) if typing_data else 1
        
        modified_actions = []
        
        for scenario_idx in range(scenarios_count):
            scenario_actions = []
            
            for action in self.base_actions:
                new_action = copy.deepcopy(action)
                
                # Модифицируем typing действия
                if action.get('name') == 'typing' and typing_data:
                    typing_row = typing_data[scenario_idx]
                    action_id = action.get('text')
                    # print(f'action_id:{action_id}')
                    # print(f'typing_row:{typing_row}')
                    if str(action_id) in typing_row:
                        new_action['text'] = typing_row[str(action_id)]
                    else:
                        # Если нет соответствующего ID, берем первое не-id значение
                        raise Exception(f"Ошибка обработке typing parameters")
                
                # Обрабатываем задержки для действий wait
                if action.get('name') == 'wait':
                    if delay is not None:
                        # Фиксированная задержка - используем новую упрощенную структуру
                        new_action['time'] = float(delay)
                        # Удаляем старую структуру event если она есть
                        if 'event' in new_action:
                            del new_action['event']
                    else:
                        # Если задержка не указана, оставляем исходную структуру
                        # Но приводим к новому формату если используется старая структура
                        if 'event' in new_action and new_action['event'].get('name') == 'timer':
                            new_action['time'] = new_action['event']['time']
                            del new_action['event']
                
                # Создаем референсные прямоугольники для кликов мыши если есть скриншоты
                # (для использования в динамическом режиме воспроизведения)
                if action.get('name') in ['click left', 'click right'] and 'screen' in action:
                    screen_file = action.get('screen')
                    if screen_file:
                        # Создаем имя файла для референсного прямоугольника
                        rr_name = screen_file.replace('.png', '_rr.png')
                        # Создаем референсный прямоугольник (если его еще нет)
                        self._create_reference_rectangle(screen_file, rr_name, action)
                
                scenario_actions.append(new_action)
            
            modified_actions.extend(scenario_actions)
            
            # Добавляем паузу между сценариями (кроме последнего)
            if scenario_idx < scenarios_count - 1:
                sleep_action = {
                    "id": self.next_id,
                    "name": "wait",
                    "time": sleep_time
                }
                self.next_id += 1
                modified_actions.append(sleep_action)
        
        self._save_scenario(modified_actions, output_name)
        return modified_actions
    
    def create_scenario_with_delay(self, delay, output_name):
        """Создает сценарий с фиксированной задержкой (для обратной совместимости)"""
        return self.create_complex_scenario(output_name, delay=delay)
    
    def _load_typing_params(self, typing_params_file):
        """Загружает параметры ввода из CSV файла"""
        import io

        try:
            with open(typing_params_file, 'r', encoding='utf-8') as f:
                # Фильтруем строки, убирая комментарии и пустые строки
                filtered_lines = []
                for line in f:
                    line = line.strip()
                    # Пропускаем пустые строки и комментарии (начинающиеся с #)
                    if line and not line.startswith('#'):
                        filtered_lines.append(line)
                
                # Создаем строковый буфер для csv.DictReader
                csv_content = '\n'.join(filtered_lines)
                csv_buffer = io.StringIO(csv_content)
                
                reader = csv.DictReader(csv_buffer)
                return list(reader)
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла параметров ввода: {e}")
    
    
    def _create_reference_rectangle(self, screen_file, pic_name, click_action):
        """Создает референсный прямоугольник 50x50 из скриншота"""
        try:
            from PIL import Image
            import os
            
            # Получаем путь к папке с действием
            action_folder = self.config.get_action_path(self.action_name)
            screen_path = action_folder / screen_file
            pic_path = action_folder / pic_name
            
            if not screen_path.exists():
                print(f"Предупреждение: файл скриншота '{screen_path}' не найден")
                return
            
            # Открываем исходное изображение
            with Image.open(screen_path) as img:
                # Получаем координаты клика
                _x = click_action.get('x', 0)
                _y = click_action.get('y', 0)
                bounds = mc.get_virtual_screen_bounds()
                x = _x - bounds['min_x']
                y = _y - bounds['min_y'] 
                
                # Вычисляем границы прямоугольника 50x50 с центром в точке клика
                left = max(0, x - 25)
                top = max(0, y - 25)
                right = min(img.width, x + 25)
                bottom = min(img.height, y + 25)
                
                # Вырезаем прямоугольник
                reference_rect = img.crop((left, top, right, bottom))
                
                # Сохраняем референсный прямоугольник
                reference_rect.save(pic_path)
                print(f"Создан референсный прямоугольник: {pic_path}")
                
        except ImportError:
            print("Предупреждение: PIL (Pillow) не установлен. Референсные прямоугольники не будут созданы.")
        except Exception as e:
            print(f"Ошибка при создании референсного прямоугольника: {e}")
    
    def _save_scenario(self, actions, output_name):
        """Сохраняет сценарий в файл"""
        scenario_file = self.config.get_scenario_file_path(self.action_name, output_name)
        
        try:
            with open(scenario_file, 'w', encoding='utf-8') as f:
                json.dump(actions, f, ensure_ascii=False, indent=2)
            print(f"Сценарий сохранен в '{scenario_file}'")
        except Exception as e:
            raise Exception(f"Ошибка при сохранении сценария: {e}")
    
    def get_scenario_info(self, output_name):
        """Возвращает информацию о сценарии"""
        scenario_file = self.config.get_scenario_file_path(self.action_name, output_name)
        
        if not scenario_file.exists():
            return None
        
        try:
            with open(scenario_file, 'r', encoding='utf-8') as f:
                scenario_data = json.load(f)
            
            info = {
                'file': str(scenario_file),
                'total_actions': len(scenario_data),
                'click_actions': len([a for a in scenario_data if a.get('name') in ['click left', 'click right']]),
                'typing_actions': len([a for a in scenario_data if a.get('name') == 'typing']),
                'wait_actions': len([a for a in scenario_data if a.get('name') == 'wait']),
                'enter_actions': len([a for a in scenario_data if a.get('name') == 'enter']),
                'space_actions': len([a for a in scenario_data if a.get('name') == 'space']),
            }
            
            return info
        except Exception as e:
            return {'error': str(e)}

    # ---------------- CUT SCENARIO FEATURE -----------------
    def create_cut_scenario(self, output_name):
        """Интерактивно обрезает базовые действия на момент нажатия F1 во время их проигрывания.

        Пользователь запускает воспроизведение всех базовых действий и в нужный момент нажимает F1.
        Сценарий до текущего выполненного действия (включительно) сохраняется.
        ESC отменяет создание.
        """
        print("Интерактивный режим обрезки (F1 = обрезать, ESC = отмена).")
        print("Используется play.play_actions в режиме cut_mode.")
        try:
            from play import play_actions
        except ImportError:
            print("Не удалось импортировать play_actions для cut_mode")
            return []

        # Воспроизводим base_actions напрямую через временный файл
        temp_name = "__cut_temp_base__"
        temp_path = self.config.get_scenario_file_path(self.action_name, temp_name)
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.base_actions, f, ensure_ascii=False, indent=2)
            result = play_actions(self.action_name, actions_file=temp_name, dynamic=False, cut_mode=True)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

        if isinstance(result, dict) and result.get('cut') and result.get('last_index', -1) >= 0:
            cut_idx = result['last_index']
            cut_actions = self.base_actions[:cut_idx+1]
            self._save_scenario(cut_actions, output_name)
            print(f"Создан обрезанный сценарий '{output_name}' с {len(cut_actions)} действиями.")
            return cut_actions
        elif isinstance(result, dict) and not result.get('cut'):
            print("Обрезка не выполнена (ESC или завершение без F1). Сценарий не создан.")
            return []
        else:
            print("Не удалось корректно выполнить cut_mode.")
            return []


def main():
    """Функция для тестирования модуля"""
    if len(sys.argv) < 2:
        print("Использование: python scenario_creator.py <action_name>")
        sys.exit(1)
    
    action_name = sys.argv[1]
    
    try:
        creator = ScenarioCreator(action_name)
        
        # Создаем тестовый сценарий с задержкой
        creator.create_scenario_with_delay(1.0, "test_delay_scenario")
        
        # Показываем информацию о сценарии
        info = creator.get_scenario_info("test_delay_scenario")
        if info:
            print(f"Информация о сценарии:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
