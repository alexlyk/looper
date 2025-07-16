#!/usr/bin/env python3
"""
Тестовый скрипт для проверки создания сценариев с динамической задержкой
"""

from scenario_creator import ScenarioCreator

def test_dynamic_delay():
    """Тестирует создание сценария с динамической задержкой"""
    
    try:
        creator = ScenarioCreator('open_notepad')
        
        # Создаем сценарий с динамической задержкой
        print("Создание сценария с динамической задержкой...")
        creator.create_complex_scenario('test_dynamic_scenario', delay='dynamic')
        
        # Показываем информацию о сценарии
        info = creator.get_scenario_info('test_dynamic_scenario')
        if info:
            print(f"\nИнформация о динамическом сценарии:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        print("\nТест завершен успешно!")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

if __name__ == "__main__":
    test_dynamic_delay()
