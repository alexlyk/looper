#!/usr/bin/env python3
"""
Looper - программа для записи, декомпозиции и воспроизведения действий пользователя
"""

import argparse
import sys
import os
import json
from pathlib import Path

__version__ = "1.0.0"

def create_action_directory(action_name):
    """Создает директорию для действия, если она не существует"""
    action_dir = Path(action_name)
    action_dir.mkdir(exist_ok=True)
    return action_dir

def record_action(action_name):
    """Запись действий пользователя"""
    print(f"Запись действия '{action_name}'...")
    print("Нажмите ESC для завершения записи")
    
    action_dir = create_action_directory(action_name)
    log_file = action_dir / "log.json"
    
    # TODO: Импорт и запуск модуля записи
    try:
        from rec import record_user_actions
        record_user_actions(str(log_file))
    except ImportError:
        print("Ошибка: модуль rec.py не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при записи: {e}")
        sys.exit(1)

def decompose_action(action_name):
    """Декомпозиция действий на базовые"""
    print(f"Декомпозиция действия '{action_name}'...")
    
    action_dir = Path(action_name)
    log_file = action_dir / "log.json"
    actions_file = action_dir / "actions_base.json"
    
    if not log_file.exists():
        print(f"Ошибка: файл лога '{log_file}' не найден")
        sys.exit(1)
    
    # Импорт и запуск модуля декомпозиции
    try:
        from decomposer import decompose_action as decompose_func
        success = decompose_func(action_name)
        if success:
            print(f"Результат декомпозиции сохранен в '{actions_file}'")
        else:
            print("Ошибка при декомпозиции")
            sys.exit(1)
    except ImportError:
        print("Ошибка: модуль decomposer.py не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при декомпозиции: {e}")
        sys.exit(1)

def play_action(action_name, actions_file=None):
    """Воспроизведение действий"""
    print(f"Воспроизведение действия '{action_name}'...")
    
    action_dir = Path(action_name)
    
    if actions_file is None:
        actions_file = action_dir / "actions_base.json"
    else:
        actions_file = Path(actions_file)
    
    # Импорт и запуск модуля воспроизведения
    try:
        from play import play_actions
        success = play_actions(str(actions_file))
        if success:
            print("Воспроизведение завершено")
        else:
            print("Ошибка при воспроизведении")
            sys.exit(1)
    except ImportError:
        print("Ошибка: модуль play.py не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при воспроизведении: {e}")
        sys.exit(1)

def create_scenario(action_name, output_name, delay=None, typing_params=None, 
                   click_params=None, sleep_time=3):
    """Создание сценария"""
    print(f"Создание сценария '{output_name}' для действия '{action_name}'...")
    
    action_dir = Path(action_name)
    actions_file = action_dir / "actions_base.json"
    scenario_file = action_dir / f"{output_name}.json"
    
    if not actions_file.exists():
        print(f"Ошибка: файл базовых действий '{actions_file}' не найден")
        sys.exit(1)
    
    # Загружаем базовые действия
    try:
        with open(actions_file, 'r', encoding='utf-8') as f:
            base_actions = json.load(f)
    except Exception as e:
        print(f"Ошибка при чтении файла действий: {e}")
        sys.exit(1)
    
    # Применяем модификации
    modified_actions = modify_actions(
        base_actions, delay, typing_params, click_params, sleep_time
    )
    
    # Сохраняем сценарий
    try:
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(modified_actions, f, ensure_ascii=False, indent=2)
        print(f"Сценарий сохранен в '{scenario_file}'")
    except Exception as e:
        print(f"Ошибка при сохранении сценария: {e}")
        sys.exit(1)

def modify_actions(base_actions, delay, typing_params, click_params, sleep_time):
    """Модифицирует базовые действия согласно параметрам сценария"""
    modified_actions = []
    
    # Загружаем параметры typing если указаны
    typing_data = None
    if typing_params:
        try:
            import csv
            with open(typing_params, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                typing_data = list(reader)
        except Exception as e:
            print(f"Ошибка при чтении файла параметров ввода: {e}")
            sys.exit(1)
    
    # Загружаем параметры клика если указаны
    click_data = None
    if click_params:
        try:
            with open(click_params, 'r', encoding='utf-8') as f:
                click_data = json.load(f)
        except Exception as e:
            print(f"Ошибка при чтении файла параметров клика: {e}")
            sys.exit(1)
    
    # Если есть typing_data, создаем несколько сценариев
    scenarios_count = len(typing_data) if typing_data else 1
    
    for scenario_idx in range(scenarios_count):
        scenario_actions = []
        
        for action in base_actions:
            new_action = action.copy()
            
            # Модифицируем typing действия
            if action.get('name') == 'typing' and typing_data:
                typing_row = typing_data[scenario_idx]
                # Находим соответствующий параметр для этого typing
                action_id = action.get('id')
                for key, value in typing_row.items():
                    if key != 'id':
                        new_action['text'] = value
                        break
            
            # Добавляем фиксированную задержку после определенных действий
            if delay and action.get('name') in ['click left', 'click right', 'enter', 'space']:
                scenario_actions.append(new_action)
                # Добавляем wait действие
                wait_action = {
                    "name": "wait",
                    "event": {
                        "name": "timer",
                        "time": delay
                    }
                }
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
                "name": "wait",
                "event": {
                    "name": "timer", 
                    "time": sleep_time
                }
            }
            modified_actions.append(sleep_action)
    
    return modified_actions

def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description="Looper - программа для записи и воспроизведения действий пользователя",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python looper.py -r open_notepad
  python looper.py -d open_notepad  
  python looper.py -p open_notepad -f custom_actions.json
  python looper.py -sc open_notepad -o my_scenario --delay 1.5
        """
    )
    
    # Основные команды (взаимоисключающие)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--record', '-r', 
        metavar='ACTION_NAME',
        help='Запись действий пользователя'
    )
    mode_group.add_argument(
        '--decompose', '-d',
        metavar='ACTION_NAME', 
        help='Декомпозиция на базовые действия'
    )
    mode_group.add_argument(
        '--play', '-p',
        metavar='ACTION_NAME',
        help='Воспроизведение действий'
    )
    mode_group.add_argument(
        '--scenario', '-sc',
        metavar='ACTION_NAME',
        help='Создание сценариев'
    )
    mode_group.add_argument(
        '--version', '-v',
        action='version',
        version=f'looper {__version__}'
    )
    
    # Параметры для воспроизведения
    parser.add_argument(
        '--actions-file', '-f',
        metavar='FILENAME',
        help='Имя файла с базовыми действиями (по умолчанию: actions_base.json)'
    )
    
    # Параметры для создания сценариев
    parser.add_argument(
        '--output', '-o',
        metavar='SCENARIO_NAME',
        help='Имя выходного файла сценария (обязательно для --scenario)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        metavar='SECONDS',
        help='Фиксированная задержка после клика, enter, space (в секундах)'
    )
    parser.add_argument(
        '--typing-params',
        metavar='CSV_FILE',
        help='CSV файл с параметрами для typing действий'
    )
    parser.add_argument(
        '--click-params',
        metavar='JSON_FILE',
        help='JSON файл с параметрами для click действий'
    )
    parser.add_argument(
        '--sleep',
        type=float,
        default=3,
        metavar='SECONDS',
        help='Время ожидания между сценариями в секундах (по умолчанию: 3)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.record:
            record_action(args.record)
        elif args.decompose:
            decompose_action(args.decompose)
        elif args.play:
            play_action(args.play, args.actions_file)
        elif args.scenario:
            if not args.output:
                print("Ошибка: для режима --scenario необходимо указать --output")
                sys.exit(1)
            create_scenario(
                args.scenario, 
                args.output, 
                args.delay, 
                args.typing_params, 
                args.click_params, 
                args.sleep
            )
    except KeyboardInterrupt:
        print("\nПрерывание по запросу пользователя")
        sys.exit(0)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()