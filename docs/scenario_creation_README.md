# Создание сценариев в Looper

Модуль создания сценариев позволяет модифицировать базовые действия, полученные после декомпозиции, для создания настраиваемых сценариев воспроизведения.

## Быстрый старт

### Создание сценария с фиксированной задержкой

```bash
python looper.py -sc open_notepad -o my_scenario --delay 2.5
```

Это создаст сценарий, где после каждого клика мышью, нажатия Enter или Space будет добавлена задержка в 2.5 секунды.

### Просмотр всех доступных действий

```bash
python scenario_viewer.py actions
```

### Просмотр сценариев для конкретного действия

```bash
python scenario_viewer.py scenarios open_notepad
```

### Просмотр деталей сценария

```bash
python scenario_viewer.py details open_notepad my_scenario
```

## Подробное описание

### 1. Фиксированная задержка

Добавляет заданную задержку после действий типа: клик мышью, Enter, Space.

**Синтаксис:**
```bash
python looper.py -sc <action_name> -o <scenario_name> --delay <seconds>
```

**Пример:**
```bash
python looper.py -sc open_notepad -o with_delay --delay 1.5
```

### 2. Параметризация текста ввода

Позволяет создать несколько сценариев с разными текстами ввода, используя CSV файл с параметрами.

**Формат CSV файла:**
```csv
id,text1,text2
1,calculator,calc
2,paint,mspaint  
3,notepad,code
```

**Синтаксис:**
```bash
python looper.py -sc <action_name> -o <scenario_name> --typing-params <csv_file>
```

**Пример:**
```bash
python looper.py -sc open_notepad -o multi_apps --typing-params typing_params.csv
```

### 3. Комбинированные сценарии

Можно комбинировать несколько типов модификаций:

```bash
python looper.py -sc open_notepad -o complex_scenario --delay 1.0 --typing-params params.csv --sleep 5
```

Параметры:
- `--delay` - фиксированная задержка в секундах
- `--typing-params` - CSV файл с параметрами ввода
- `--sleep` - пауза между сценариями в секундах (по умолчанию 3)

## Структура файлов

После создания сценариев в папке действия появляются файлы:

```
actions/
└── open_notepad/
    ├── log.json                    # Исходные записанные действия
    ├── actions_base.json           # Базовые действия после декомпозиции
    ├── my_scenario.json            # Созданный сценарий
    └── typing_parameters_base.csv  # Базовые параметры ввода
```

## Модули

### scenario_creator.py

Основной модуль для создания сценариев. Предоставляет класс `ScenarioCreator` с методами:

- `create_scenario_with_delay()` - создание с фиксированной задержкой
- `create_scenario_with_typing_params()` - создание с параметрами ввода
- `create_complex_scenario()` - создание комплексного сценария
- `get_scenario_info()` - получение информации о сценарии

### scenario_viewer.py

Утилита для просмотра и анализа сценариев:

```bash
# Показать все действия
python scenario_viewer.py actions

# Показать сценарии для действия
python scenario_viewer.py scenarios <action_name>

# Показать детали сценария
python scenario_viewer.py details <action_name> <scenario_name>
```

## Примеры использования

### Создание простого сценария с задержкой

```bash
# Запись действий
python looper.py -r open_calculator

# Декомпозиция
python looper.py -d open_calculator

# Создание сценария с задержкой 2 секунды
python looper.py -sc open_calculator -o slow_version --delay 2.0

# Просмотр созданного сценария
python scenario_viewer.py details open_calculator slow_version
```

### Создание сценария с параметрами

1. Создайте CSV файл `apps.csv`:
```csv
id,app_name
1,calculator
2,notepad
3,mspaint
```

2. Создайте сценарий:
```bash
python looper.py -sc open_app -o multiple_apps --typing-params apps.csv --delay 1.0 --sleep 5
```

Это создаст сценарий, который:
- Откроет calculator, подождет 5 секунд
- Откроет notepad, подождет 5 секунд  
- Откроет mspaint
- Между каждым действием будет задержка 1 секунда

## Структура JSON сценария

Пример структуры созданного сценария:

```json
[
  {
    "id": 1,
    "name": "click left",
    "type": "mouse_click",
    "button": "left",
    "x": 775,
    "y": 1058
  },
  {
    "id": 14,
    "name": "wait",
    "event": {
      "name": "timer",
      "time": 2.0
    }
  },
  {
    "id": 3,
    "name": "typing",
    "type": "keyboard_typing",
    "text": "calculator"
  }
]
```

## Типы действий

- **click left/right** - клик мышью (левой/правой кнопкой)
- **typing** - ввод текста
- **wait** - ожидание (timer или picOnScreen)
- **enter** - нажатие Enter
- **space** - нажатие пробела

## Ошибки и решения

### Файл базовых действий не найден
```
Ошибка: файл базовых действий 'actions_base.json' не найден
```
**Решение:** Сначала выполните декомпозицию:
```bash
python looper.py -d <action_name>
```

### Ошибка чтения CSV файла
```
Ошибка при чтении файла параметров ввода
```
**Решение:** Проверьте формат CSV файла и кодировку (должна быть UTF-8).

### Сценарий не найден
```
Сценарий 'name' для действия 'action' не найден
```
**Решение:** Проверьте правильность имени сценария и действия.
