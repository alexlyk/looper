#!/usr/bin/env python3
"""
Пример использования автоматического создания actions_base.json
"""

import tempfile
import json
import os
from pathlib import Path

def create_example_log():
    """Создает пример файла log.json для демонстрации"""
    example_log = [
        {
            "source": "mouse",
            "button": "left",
            "dir": "down",
            "x": 100,
            "y": 100,
            "timestamp": 1.0,
            "screen": "1.png"
        },
        {
            "source": "mouse",
            "button": "left",
            "dir": "up",
            "x": 100,
            "y": 100,
            "timestamp": 1.1
        },
        {
            "source": "keyboard",
            "key": "h",
            "timestamp": 2.0,
            "layout": "0409"
        },
        {
            "source": "keyboard",
            "key": "i",
            "timestamp": 2.1,
            "layout": "0409"
        },
        {
            "source": "keyboard",
            "key": "\n",
            "timestamp": 3.0,
            "layout": "0409",
            "screen": "2.png"
        }
    ]
    
    return example_log

def demo_auto_creation():
    """Демонстрация автоматического создания actions_base.json"""
    
    # Создаем временную директорию
    test_dir = Path("example_action")
    test_dir.mkdir(exist_ok=True)
    
    # Создаем log.json
    log_file = test_dir / "log.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(create_example_log(), f, ensure_ascii=False, indent=2)
    
    print(f"Создан пример log.json в {log_file}")
    
    # Убеждаемся, что actions_base.json не существует
    actions_file = test_dir / "actions_base.json"
    if actions_file.exists():
        actions_file.unlink()
    
    print(f"actions_base.json отсутствует: {not actions_file.exists()}")
    
    # Теперь вызовем play.py - должно автоматически создать actions_base.json
    from play import play_actions
    
    print("\n--- Демонстрация автоматического создания ---")
    result = play_actions(str(actions_file))
    
    print(f"\nДекомпозиция успешна: {result}")
    print(f"actions_base.json создан: {actions_file.exists()}")
    
    # Покажем содержимое созданного файла
    if actions_file.exists():
        with open(actions_file, 'r', encoding='utf-8') as f:
            actions = json.load(f)
        print(f"\nСоздано {len(actions)} базовых действий:")
        for action in actions:
            print(f"  - {action.get('name', 'unknown')}")
    
    # Очистка
    print(f"\nОчистка: удаляем {test_dir}")
    import shutil
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    print("=== Демонстрация автоматического создания actions_base.json ===\n")
    demo_auto_creation()
    print("\n=== Демонстрация завершена ===")
