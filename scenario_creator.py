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
                               click_params_file=None, sleep_time=3):
        """Создает комплексный сценарий с несколькими типами модификаций"""
        print(f"Создание комплексного сценария '{output_name}'...")
        
        # Загружаем параметры typing если указаны
        typing_data = None
        if typing_params_file:
            typing_data = self._load_typing_params(typing_params_file)
        
        # Загружаем параметры клика если указаны
        click_data = None
        if click_params_file:
            click_data = self._load_click_params(click_params_file)
        
        # Если есть typing_data, создаем несколько сценариев
        scenarios_count = len(typing_data) if typing_data else 1
        
        modified_actions = []
        
        for scenario_idx in range(scenarios_count):
            scenario_actions = []
            i = 0
            
            for action in self.base_actions:
                new_action = copy.deepcopy(action)
                
                # Модифицируем typing действия
                if action.get('name') == 'typing' and typing_data:
                    typing_row = typing_data[scenario_idx]
                    action_id = action.get('id')
                    if str(action_id) in typing_row:
                        new_action['text'] = typing_row[str(action_id)]
                    else:
                        # Если нет соответствующего ID, берем первое не-id значение
                        for key, value in typing_row.items():
                            if key != 'id':
                                new_action['text'] = value
                                break
                
                # Обрабатываем фиксированную задержку для определенных действий
                if action.get('name') == 'wait' and delay:
                    # Добавляем новое wait действие с фиксированной задержкой
                    wait_action = {
                        "id": self.next_id,
                        "name": "wait",
                        "event": {
                            "name": "timer",
                            "time": delay
                        }
                    }
                    self.next_id += 1
                    scenario_actions.append(wait_action)
                else:
                    scenario_actions.append(new_action)
                
            
            # Модифицируем click параметры
            if click_data:
                for action in scenario_actions:
                    if action.get('name') in ['click left', 'click right']:
                        action_id = action.get('id')
                        for click_param in click_data:
                            if click_param.get('id') == action_id:
                                # Изменяем предыдущее wait событие на picOnScreen
                                prev_action_idx = scenario_actions.index(action) - 1
                                if (prev_action_idx >= 0 and 
                                    scenario_actions[prev_action_idx].get('name') == 'wait'):
                                    scenario_actions[prev_action_idx]['event'] = {
                                        "name": "picOnScreen",
                                        "file": click_param.get('fn')
                                    }
            
            modified_actions.extend(scenario_actions)
            
            # Добавляем паузу между сценариями (кроме последнего)
            if scenario_idx < scenarios_count - 1:
                sleep_action = {
                    "id": self.next_id,
                    "name": "wait",
                    "event": {
                        "name": "timer", 
                        "time": sleep_time
                    }
                }
                self.next_id += 1
                modified_actions.append(sleep_action)
        
        self._save_scenario(modified_actions, output_name)
        return modified_actions
    
    def _load_typing_params(self, typing_params_file):
        """Загружает параметры ввода из CSV файла"""
        try:
            with open(typing_params_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла параметров ввода: {e}")
    
    def _load_click_params(self, click_params_file):
        """Загружает параметры клика из JSON файла"""
        try:
            with open(click_params_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла параметров клика: {e}")
    
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
