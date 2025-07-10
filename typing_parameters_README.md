# Файл typing_parameters_base.csv

Этот файл автоматически создается при декомпозиции действий командой:
```bash
python looper.py -d <action_name>
```

## Назначение

Файл содержит базовые параметры для всех `typing` действий, найденных в записанном сценарии. Он используется для создания сценариев с различными вариантами ввода текста.

## Формат файла

- Первая строка содержит заголовки колонок: `id` и названия каждого typing действия
- Каждая последующая строка представляет один сценарий выполнения
- Колонка `id` - уникальный идентификатор сценария
- Остальные колонки содержат текст для соответствующих typing действий

## Пример использования

Если у вас есть файл `typing_parameters_base.csv`:
```csv
id,notepad,hello_world
1,notepad,hello world
2,calculator,goodbye world
3,wordpad,hi there
```

Вы можете создать сценарий командой:
```bash
python looper.py -sc open_notepad -o my_scenario --typing-params typing_parameters_base.csv
```

Это создаст сценарий, который будет выполнен три раза:
1. Первый раз: введет "notepad" и "hello world"
2. Второй раз: введет "calculator" и "goodbye world"  
3. Третий раз: введет "wordpad" и "hi there"

## Редактирование

Вы можете редактировать этот файл вручную, добавляя новые строки или изменяя существующие значения. Главное - сохранить структуру заголовков и убедиться, что количество колонок в каждой строке совпадает.

## Связанные команды

- Запись действий: `python looper.py -r <action_name>`
- Декомпозиция: `python looper.py -d <action_name>`
- Создание сценария: `python looper.py -sc <action_name> -o <scenario_name> --typing-params <csv_file>`
- Воспроизведение: `python looper.py -p <action_name>`
