#!/usr/bin/env python3
"""
Утилита для просмотра и анализа сценариев
"""

import argparse
import sys
from pathlib import Path
from scenario_creator import ScenarioCreator
from config import get_config


def list_scenarios(action_name):
    """Показывает список всех сценариев для действия"""
    cfg = get_config()
    action_dir = cfg.get_action_path(action_name)
    
    if not action_dir.exists():
        print(f"Папка действия '{action_name}' не найдена")
        return
    
    # Ищем файлы сценариев (все .json файлы кроме специальных)
    scenario_files = []
    for file in action_dir.glob("*.json"):
        if file.name not in ["log.json", "actions_base.json"]:
            scenario_files.append(file)
    
    if not scenario_files:
        print(f"Сценарии для действия '{action_name}' не найдены")
        return
    
    print(f"Сценарии для действия '{action_name}':")
    print("-" * 50)
    
    try:
        creator = ScenarioCreator(action_name)
        
        for scenario_file in sorted(scenario_files):
            scenario_name = scenario_file.stem
            info = creator.get_scenario_info(scenario_name)
            
            if info and 'error' not in info:
                print(f"📁 {scenario_name}")
                print(f"   Всего действий: {info['total_actions']}")
                print(f"   Клики: {info['click_actions']}, Ввод: {info['typing_actions']}, Ожидания: {info['wait_actions']}")
                if info['enter_actions'] > 0 or info['space_actions'] > 0:
                    print(f"   Enter: {info['enter_actions']}, Space: {info['space_actions']}")
                print()
            else:
                print(f"❌ {scenario_name} - ошибка чтения")
                print()
    
    except Exception as e:
        print(f"Ошибка при анализе сценариев: {e}")


def show_scenario_details(action_name, scenario_name):
    """Показывает детальную информацию о сценарии"""
    try:
        creator = ScenarioCreator(action_name)
        cfg = get_config()
        scenario_file = cfg.get_scenario_file_path(action_name, scenario_name)
        
        if not scenario_file.exists():
            print(f"Сценарий '{scenario_name}' для действия '{action_name}' не найден")
            return
        
        import json
        with open(scenario_file, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        info = creator.get_scenario_info(scenario_name)
        
        print(f"Детали сценария '{scenario_name}' для действия '{action_name}'")
        print("=" * 60)
        print(f"Файл: {scenario_file}")
        print(f"Размер файла: {scenario_file.stat().st_size} байт")
        print()
        
        if info and 'error' not in info:
            print("Статистика:")
            print(f"  Всего действий: {info['total_actions']}")
            print(f"  Клики мышью: {info['click_actions']}")
            print(f"  Действия ввода: {info['typing_actions']}")
            print(f"  Ожидания: {info['wait_actions']}")
            print(f"  Нажатия Enter: {info['enter_actions']}")
            print(f"  Нажатия Space: {info['space_actions']}")
            print()
        
        print("Последовательность действий:")
        print("-" * 30)
        
        for i, action in enumerate(scenario_data[:10]):  # Показываем первые 10 действий
            action_name = action.get('name', 'unknown')
            action_id = action.get('id', '')
            
            if action_name == 'click left' or action_name == 'click right':
                x, y = action.get('x', '?'), action.get('y', '?')
                print(f"{i+1:2d}. {action_name} в точке ({x}, {y}) [ID: {action_id}]")
            elif action_name == 'typing':
                text = action.get('text', '')[:30]  # Ограничиваем длину текста
                print(f"{i+1:2d}. ввод текста: '{text}' [ID: {action_id}]")
            elif action_name == 'wait':
                event = action.get('event', {})
                if event.get('name') == 'timer':
                    time_val = event.get('time', 0)
                    print(f"{i+1:2d}. ожидание {time_val} сек [ID: {action_id}]")
                elif event.get('name') == 'picOnScreen':
                    pic_file = event.get('file', '')
                    print(f"{i+1:2d}. ожидание картинки '{pic_file}' [ID: {action_id}]")
                else:
                    print(f"{i+1:2d}. ожидание (неизвестный тип) [ID: {action_id}]")
            else:
                print(f"{i+1:2d}. {action_name} [ID: {action_id}]")
        
        if len(scenario_data) > 10:
            print(f"... и еще {len(scenario_data) - 10} действий")
        
    except Exception as e:
        print(f"Ошибка при показе деталей сценария: {e}")


def list_actions():
    """Показывает список всех доступных действий"""
    cfg = get_config()
    actions_folder = cfg.get_action_folder()
    
    if not actions_folder.exists():
        print(f"Папка действий '{actions_folder}' не найдена")
        return
    
    action_dirs = [d for d in actions_folder.iterdir() if d.is_dir()]
    
    if not action_dirs:
        print("Действия не найдены")
        return
    
    print("Доступные действия:")
    print("-" * 30)
    
    for action_dir in sorted(action_dirs):
        action_name = action_dir.name
        has_log = (action_dir / "log.json").exists()
        has_base = (action_dir / "actions_base.json").exists()
        
        status_log = "✅" if has_log else "❌"
        status_base = "✅" if has_base else "❌"
        
        print(f"📁 {action_name}")
        print(f"   Лог: {status_log}  Базовые действия: {status_base}")
        
        # Считаем количество сценариев
        scenario_files = [f for f in action_dir.glob("*.json") 
                         if f.name not in ["log.json", "actions_base.json"]]
        if scenario_files:
            print(f"   Сценариев: {len(scenario_files)}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Утилита для просмотра и анализа сценариев looper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда для списка действий
    parser_actions = subparsers.add_parser('actions', help='Показать все доступные действия')
    
    # Команда для списка сценариев
    parser_scenarios = subparsers.add_parser('scenarios', help='Показать сценарии для действия')
    parser_scenarios.add_argument('action_name', help='Имя действия')
    
    # Команда для деталей сценария
    parser_details = subparsers.add_parser('details', help='Показать детали сценария')
    parser_details.add_argument('action_name', help='Имя действия')
    parser_details.add_argument('scenario_name', help='Имя сценария')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'actions':
            list_actions()
        elif args.command == 'scenarios':
            list_scenarios(args.action_name)
        elif args.command == 'details':
            show_scenario_details(args.action_name, args.scenario_name)
    
    except KeyboardInterrupt:
        print("\nПрерывание по запросу пользователя")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
