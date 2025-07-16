#!/usr/bin/env python3
"""
Финальный тест всех возможностей scenario_creator.py
"""

from scenario_creator import ScenarioCreator

def test_all_scenario_types():
    """Тестирует все типы создания сценариев"""
    
    try:
        creator = ScenarioCreator('open_notepad')
        
        print("=== Тест 1: Фиксированная задержка ===")
        creator.create_complex_scenario('test_fixed_delay', delay=2.5)
        info = creator.get_scenario_info('test_fixed_delay')
        print(f"Создан сценарий с фиксированной задержкой: {info['total_actions']} действий")
        
        print("\n=== Тест 2: Динамическая задержка ===")
        creator.create_complex_scenario('test_dynamic_delay', delay='dynamic')
        info = creator.get_scenario_info('test_dynamic_delay')
        print(f"Создан сценарий с динамической задержкой: {info['total_actions']} действий")
        
        print("\n=== Тест 3: Обычный сценарий (без модификаций) ===")
        creator.create_complex_scenario('test_normal')
        info = creator.get_scenario_info('test_normal')
        print(f"Создан обычный сценарий: {info['total_actions']} действий")
        
        print("\nВсе тесты прошли успешно!")
        print("\nСозданные сценарии:")
        for scenario_name in ['test_fixed_delay', 'test_dynamic_delay', 'test_normal']:
            info = creator.get_scenario_info(scenario_name)
            print(f"  {scenario_name}: {info['file']}")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

if __name__ == "__main__":
    test_all_scenario_types()
