#!/usr/bin/env python3
"""
Looper - программа для записи, декомпозиции и воспроизведения действий пользователя
"""

import argparse
import sys
import os
import json
from pathlib import Path
from config import get_config

__version__ = "1.0.0"

def create_action_directory(action_name):
    """Создает директорию для действия, если она не существует"""
    cfg = get_config()
    action_dir = cfg.get_action_path(action_name)
    action_dir.mkdir(parents=True, exist_ok=True)
    return action_dir

def record_action(action_name):
    """Запись действий пользователя"""
    print(f"Запись действия '{action_name}'...")
    print("Нажмите ESC для завершения записи")
    
    # Импорт и запуск модуля записи
    try:
        from rec import record_user_actions
        record_user_actions(action_name)
    except ImportError:
        print("Ошибка: модуль rec.py не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при записи: {e}")
        sys.exit(1)

def decompose_action(action_name):
    """Декомпозиция действий на базовые"""
    print(f"Декомпозиция действия '{action_name}'...")
    
    cfg = get_config()
    log_file = cfg.get_log_file_path(action_name)
    actions_file = cfg.get_actions_base_file_path(action_name)
    
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

def play_action(action_name, actions_file=None, dynamic=False, delay=None, typing_params=None):
    """Воспроизведение действий"""
    print(f"Воспроизведение действия '{action_name}'...")
    if dynamic:
        print("Динамический режим включен")
    
    # Проверяем, существует ли файл базовых действий
    cfg = get_config()
    actions_base_file = cfg.get_actions_base_file_path(action_name)
    
    if not actions_base_file.exists():
        # Проверяем, есть ли файл лога для декомпозиции
        log_file = cfg.get_log_file_path(action_name)
        if log_file.exists():
            print(f"Файл базовых действий не найден. Выполняем декомпозицию...")
            decompose_action(action_name)
        else:
            print(f"Ошибка: файл лога '{log_file}' не найден. Необходимо сначала записать действия.")
            sys.exit(1)
    
    # Проверяем, нужно ли создать сценарий перед воспроизведением
    if delay is not None or typing_params is not None:
        # Создаем имя сценария
        scenario_parts = []
        if delay is not None:
            scenario_parts.append("fix_delay")
        if typing_params is not None:
            # Используем имя файла без расширения
            typing_name = Path(typing_params).stem
            scenario_parts.append(typing_name)
        
        scenario_name = "_".join(scenario_parts)
        print(f"Создание временного сценария '{scenario_name}' с параметрами...")
        
        # Создаем сценарий
        try:
            delay_value = float(delay) if delay is not None else None
            create_scenario(action_name, scenario_name, delay_value, typing_params, None, 3)
            # Используем созданный сценарий вместо actions_file
            actions_file = scenario_name
        except Exception as e:
            print(f"Ошибка при создании сценария: {e}")
            sys.exit(1)
    
    # Импорт и запуск модуля воспроизведения
    try:
        from play import play_actions
        success = play_actions(action_name, actions_file, dynamic)
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
                   click_params=None, sleep_time=3, cut=False):
    """Создание сценария"""
    print(f"Создание сценария '{output_name}' для действия '{action_name}'...")
    
    try:
        from scenario_creator import ScenarioCreator
        creator = ScenarioCreator(action_name)
        cfg = get_config()
        typing_params_file = cfg.get_get_typing_parameters_file_path(action_name,typing_params)
        if cut:
            if any([delay, typing_params, click_params]):
                print("Предупреждение: параметры delay/typing-params/click-params игнорируются при --cut")
            creator.create_cut_scenario(output_name)
        else:
            # Создаем комплексный сценарий со всеми возможными модификациями
            creator.create_complex_scenario(
                output_name=output_name,
                delay=delay,
                typing_params_file=typing_params_file,
                sleep_time=sleep_time
            )
        
        # Показываем информацию о созданном сценарии
        info = creator.get_scenario_info(output_name)
        if info and 'error' not in info:
            print(f"\nИнформация о сценарии:")
            print(f"  Общее количество действий: {info['total_actions']}")
            print(f"  Клики мышью: {info['click_actions']}")
            print(f"  Действия ввода: {info['typing_actions']}")
            print(f"  Ожидания: {info['wait_actions']}")
            if info['enter_actions'] > 0:
                print(f"  Нажатия Enter: {info['enter_actions']}")
            if info['space_actions'] > 0:
                print(f"  Нажатия Space: {info['space_actions']}")
        
    except ImportError:
        print("Ошибка: модуль scenario_creator.py не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при создании сценария: {e}")
        sys.exit(1)

def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description="Looper - программа для записи и воспроизведения действий пользователя",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  looper -r open_notepad
  looper -p open_notepad --dynamic
  looper -p open_notepad --dynamic --delay 2.5 
  looper -p open_notepad --dynamic --delay 2.5 --typing-params xxx.csv
  Для разработчиков:
  looper -d open_notepad 
  looper -p open_notepad -f custom_actions.json
  looper -p open_notepad -f custom_actions.json --dynamic
  looper -sc open_notepad -o my_scenario --delay 1.5
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
    parser.add_argument(
        '--dynamic',
        action='store_true',
        help='Динамический режим воспроизведения (поиск по референсным прямоугольникам)'
    )
    
    # Параметры для создания сценариев
    parser.add_argument(
        '--output', '-o',
        metavar='SCENARIO_NAME',
        help='Имя выходного файла сценария (обязательно для --scenario)'
    )
    parser.add_argument(
        '--delay',
        #type=float,
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
    parser.add_argument(
        '--cut',
        action='store_true',
    help='Обрезать сценарий на момент нажатия F1 во время воспроизведения'
    )
    
    args = parser.parse_args()
    
    try:
        if args.record:
            record_action(args.record)
        elif args.decompose:
            decompose_action(args.decompose)
        elif args.play:
            play_action(args.play, args.actions_file, args.dynamic, args.delay, args.typing_params)
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
                args.sleep,
                args.cut
            )
    except KeyboardInterrupt:
        print("\nПрерывание по запросу пользователя")
        sys.exit(0)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()