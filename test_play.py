#!/usr/bin/env python3
"""
Тестовый скрипт для проверки модуля play.py
"""

import json
from pathlib import Path

def create_test_actions():
    """Создает тестовый файл действий"""
    test_actions = [
        {
            "id": 1,
            "name": "wait",
            "event": {
                "name": "timer",
                "time": 1.0
            }
        },
        {
            "id": 2,
            "name": "typing",
            "type": "keyboard_typing",
            "text": "Hello World!"
        },
        {
            "id": 3,
            "name": "wait",
            "event": {
                "name": "timer",
                "time": 0.5
            }
        },
        {
            "id": 4,
            "name": "enter"
        }
    ]
    
    test_file = Path("test_actions.json")
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_actions, f, ensure_ascii=False, indent=2)
    
    print(f"Создан тестовый файл: {test_file}")
    return str(test_file)

if __name__ == "__main__":
    from play import play_actions
    
    # Создаем тестовый файл
    test_file = create_test_actions()
    
    # Запускаем воспроизведение
    print("Запуск тестового воспроизведения...")
    play_actions(test_file)
    
    # Удаляем тестовый файл
    Path(test_file).unlink()
    print("Тестовый файл удален")
