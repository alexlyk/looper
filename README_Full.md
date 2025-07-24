# Looper - Автоматизация действий пользователя

Программа для записи, декомпозиции и воспроизведения действий пользователя (мышь и клавиатура).

## Структура проекта

```
looper/
├── src/                    # Исходный код приложения
│   ├── __init__.py
│   ├── looper.py          # Главный модуль
│   ├── config.py          # Конфигурация
│   ├── rec.py             # Модуль записи
│   ├── play.py            # Модуль воспроизведения
│   ├── decomposer.py      # Модуль декомпозиции
│   ├── mouse_clicker.py   # Утилиты для работы с мышью
│   ├── scenario_creator.py # Создание сценариев
│   └── scenario_viewer.py  # Просмотр сценариев
├── main.py                # Точка входа приложения
├── setup.py               # Установочный скрипт
├── requirements.txt       # Зависимости
├── actions/               # Папка с записанными действиями
├── data/                  # Тестовые данные
└── looper.config          # Конфигурационный файл
```

## Установка

```bash
pip install -r requirements.txt
pip install -e .
```

После установки команда `looper` будет доступна глобально из любой папки.

Альтернативный способ запуска (без установки):
```bash
python main.py --help
```

## Конфигурация

Программа использует конфигурационный файл `looper.config` для настройки путей и параметров.

По умолчанию все действия сохраняются в папку `./data`.

## Использование

### Запись действий
```bash
# После установки пакета (рекомендуется):
looper --record open_notepad
# или короткая форма:
looper -r open_notepad

# Альтернативно (без установки):
python main.py --record open_notepad
```

### Воспроизведение действий
```bash
# Базовое воспроизведение
looper --play open_notepad
# или короткая форма:
looper -p open_notepad

# Воспроизведение с фиксированной задержкой
looper -p open_notepad --delay 2.5

# Воспроизведение с параметрами из CSV файла
looper -p open_notepad --typing-params typing_parameters.csv


# Динамический режим (поиск по референсным прямоугольникам)
looper -p open_notepad --dynamic

# Комбинированные режимы
looper -p open_notepad --dynamic --delay 2.5
looper -p open_notepad --dynamic --delay 2.5 --typing-params xxx.csv



# Воспроизведение с указанием файла действий
looper -p open_notepad -f custom_actions.json

looper -p open_notepad -f custom_actions.json --dynamic

# Альтернативно (без установки):
python main.py --play open_notepad
```

### Декомпозиция на базовые действия
```bash
# После установки пакета:
looper --decompose open_notepad
# или короткая форма:
looper -d open_notepad

# Альтернативно (без установки):
python main.py --decompose open_notepad
```

### Создание сценариев
```bash
# Создание базового сценария
looper --scenario open_notepad --output my_scenario
# или короткая форма:
looper -sc open_notepad -o my_scenario

# Сценарий с фиксированной задержкой
looper -sc open_notepad -o my_scenario --delay 1.5

# Сценарий с параметрами из CSV файла
looper -sc open_notepad -o my_scenario --typing-params typing_parameters.csv

# Сценарий с настройкой времени ожидания между повторениями
looper -sc open_notepad -o my_scenario --sleep 5

# Альтернативно (без установки):
python main.py --scenario open_notepad --output my_scenario
```

## Параметры командной строки

### Основные режимы:
- `--record, -r <action_name>` - Запись действий пользователя
- `--play, -p <action_name>` - Воспроизведение действий
- `--decompose, -d <action_name>` - Декомпозиция на базовые действия  
- `--scenario, -sc <action_name>` - Создание сценариев
- `--help, -h` - Показать справку
- `--version, -v` - Показать версию

### Параметры для воспроизведения и создания сценариев:
- `--actions-file, -f <filename>` - Имя файла с базовыми действиями (по умолчанию: actions_base.json)
- `--dynamic` - Динамический режим воспроизведения (поиск по референсным прямоугольникам)
- `--delay <seconds>` - Фиксированная задержка после клика, enter, space (в секундах)
- `--typing-params <csv_file>` - CSV файл с параметрами для typing действий
- `--output, -o <scenario_name>` - Имя выходного файла сценария (обязательно для --scenario)
- `--sleep <seconds>` - Время ожидания между сценариями в секундах (по умолчанию: 3)

## Структура файлов

```
./data/
├── open_notepad/
│   ├── log.json                    # Записанные действия
│   ├── actions_base.json           # Базовые действия после декомпозиции
│   ├── typing_parameters_base.csv  # Параметры typing действий (создается автоматически)
│   ├── fix_delay.json              # Временный сценарий с фиксированной задержкой
│   ├── my_scenario.json            # Пользовательский сценарий
│   ├── 1.png                       # Скриншоты активных действий
│   ├── 1_c.png                     # Скриншоты с отметкой курсора
│   ├── 1_rr.png                    # Референсные прямоугольники для динамического режима
│   ├── 2.png
│   └── ...
└── другие_действия/
```

### Типы файлов изображений:
- `xxx.png` - Скрин экрана в момент совершения действия
- `xxx_c.png` - Скрин экрана с красной точкой в месте расположения курсора
- `xxx_rr.png` - Референсный прямоугольник размером 50x50 для динамического режима

## Формат CSV файла для typing параметров

Файл `typing_parameters.csv` позволяет задать различные значения для typing действий:

```csv
id,notepad,hello world,C:\Projects\looper\data\open_notepad,2
1,notepad,hello world,C:\Projects\looper\data\open_notepad,2
2,calculator,goodbye world,D:\MyPath,5
```

- Первая строка содержит заголовки колонок, соответствующие тексту typing действий
- Каждая последующая строка представляет один сценарий выполнения
- Программа выполнит сценарий для каждой строки с соответствующими параметрами
- Между выполнениями сценариев программа ждет заданное время (параметр `--sleep`, по умолчанию 3 секунды)

## Возможности

- **Запись**: Фиксирует все действия мыши и клавиатуры до нажатия ESC
- **Воспроизведение**: 
  - Выполняет записанные действия
  - Поддерживает динамический режим (поиск по референсным прямоугольникам)
  - Создание временных сценариев с фиксированной задержкой
  - Использование параметров из CSV файлов для typing действий
- **Декомпозиция**: Преобразует записанные действия в базовые команды
- **Автоматическое создание CSV**: При декомпозиции создается `typing_parameters_base.csv` с параметрами для typing действий
- **Прерывание**: Нажатие ESC останавливает запись или воспроизведение
- **Сценарии**: Создание модифицированных версий действий с возможностью:
  - Изменения параметров ввода
  - Установки фиксированных задержек
  - Настройки времени ожидания между повторениями

## Примеры использования

### Полный цикл работы:
```bash
# 1. Записать действия
looper -r open_notepad

# 2. Декомпозировать на базовые действия
looper -d open_notepad

# 3. Воспроизвести стандартно
looper -p open_notepad

# 4. Воспроизвести с динамическим режимом
looper -p open_notepad --dynamic

# 5. Воспроизвести с фиксированной задержкой 2.5 секунды
looper -p open_notepad --delay 2.5

# 6. Воспроизвести с параметрами из CSV файла
looper -p open_notepad --typing-params typing_parameters_base.csv

# 7. Комбинированный режим
looper -p open_notepad --dynamic --delay 2.5 --typing-params typing_parameters_base.csv

# 8. Создать сценарий с настройками
looper -sc open_notepad -o my_custom_scenario --delay 1.5 --typing-params my_params.csv
```


## Конфигурация

Файл `looper.config`:
```ini
ACTION_FOLDER = ./data
```

Можно изменить папку для сохранения действий, например:
```ini
ACTION_FOLDER = D:/MyActions
```

## Автор

**Lykov Alexander**

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле [LICENSE](LICENSE).
