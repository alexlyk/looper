"""
Модуль для работы с конфигурационными файлами looper
"""

import configparser
from pathlib import Path
import os


class LooperConfig:
    """Класс для работы с конфигурацией looper"""
    
    def __init__(self, config_file="looper.config"):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
        if not self.config_file.exists():
            self.create_default_config()
        
        try:
            # Для простого формата KEY = VALUE без секций
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Если файл не содержит секций, добавляем секцию по умолчанию
            if not content.strip().startswith('['):
                content = '[DEFAULT]\n' + content
            
            self.config.read_string(content)
            
        except Exception as e:
            print(f"Ошибка при чтении конфигурации: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Создает конфигурацию по умолчанию"""
        self.config['DEFAULT'] = {
            'ACTION_FOLDER': './actions'
        }
        self.save_config()
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                # Записываем только значения без секции DEFAULT
                for key, value in self.config['DEFAULT'].items():
                    f.write(f"{key} = {value}\n")
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")
    
    def get_action_folder(self):
        """Возвращает путь к папке с действиями"""
        action_folder = self.config.get('DEFAULT', 'ACTION_FOLDER', fallback='./actions')
        return Path(action_folder).resolve()
    
    def get_action_path(self, action_name):
        """Возвращает полный путь к папке конкретного действия"""
        return self.get_action_folder() / action_name
    
    def get_log_file_path(self, action_name):
        """Возвращает путь к файлу лога для действия"""
        return self.get_action_path(action_name) / "log.json"
    
    def get_actions_base_file_path(self, action_name):
        """Возвращает путь к файлу базовых действий для действия"""
        return self.get_action_path(action_name) / "actions_base.json"
    
    def get_scenario_file_path(self, action_name, scenario_name):
        """Возвращает путь к файлу сценария"""
        return self.get_action_path(action_name) / f"{scenario_name}.json"
    
    def get_get_typing_parameters_file_path(self, action_name, typing_parameters):
        """Возвращает путь к файлу параметров typing для действия"""
        return self.get_action_path(action_name) / f"{typing_parameters}.csv"

    def get_typing_parameters_base_file_path(self, action_name):
        """Возвращает путь к файлу базовых параметров typing для действия"""
        return self.get_get_typing_parameters_file_path(action_name,'typing_parameters_base')
    



# Глобальный экземпляр конфигурации
config = LooperConfig()


def get_config():
    """Возвращает глобальный экземпляр конфигурации"""
    return config


if __name__ == "__main__":
    # Тестирование модуля
    cfg = LooperConfig()
    print(f"ACTION_FOLDER: {cfg.get_action_folder()}")
    print(f"Path for 'open_notepad': {cfg.get_action_path('open_notepad')}")
    print(f"Log file for 'open_notepad': {cfg.get_log_file_path('open_notepad')}")
    print(f"Actions base file for 'open_notepad': {cfg.get_actions_base_file_path('open_notepad')}")
    print(f"Typing parameters base file for 'open_notepad': {cfg.get_typing_parameters_base_file_path('open_notepad')}")
