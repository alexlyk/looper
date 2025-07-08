# Модуль play.py - Воспроизведение действий

## Описание
Модуль `play.py` предназначен для воспроизведения базовых действий пользователя, полученных на этапе декомпозиции.

## ✨ Автоматическое создание actions_base.json
**Новая функция:** Если файл `actions_base.json` не существует, модуль автоматически создаст его, вызвав функцию декомпозиции из модуля `decomposer.py`.

### Условия автоматического создания:
- Запрашиваемый файл называется `actions_base.json`
- В той же директории существует файл `log.json`
- Модуль `decomposer.py` доступен для импорта

### Пример работы:
```bash
# Если open_notepad/actions_base.json не существует, но есть open_notepad/log.json
python looper.py -p open_notepad

# Вывод:
# Файл open_notepad\actions_base.json не найден.
# Найден файл лога: open_notepad\log.json
# Выполняем декомпозицию для создания базовых действий...
# Декомпозиция завершена. Файл open_notepad\actions_base.json создан.
# Загружено 13 действий из open_notepad\actions_base.json
# ...
```

## Поддерживаемые действия

### 1. Клики мышью
```json
{
    "name": "click left",  // или "click right"
    "type": "mouse_click",
    "button": "left",      // или "right"
    "x": 775,
    "y": 1058
}
```

### 2. Ввод текста
```json
{
    "name": "typing",
    "type": "keyboard_typing", 
    "text": "Hello World!"
}
```

### 3. Нажатие клавиш
```json
{
    "name": "enter"  // или "space"
}
```

### 4. Ожидание
```json
{
    "name": "wait",
    "event": {
        "name": "timer",
        "time": 2.5
    }
}
```

### 5. Ожидание изображения на экране
```json
{
    "name": "wait",
    "event": {
        "name": "picOnScreen",
        "file": "reference_image.png"
    }
}
```

## Использование

### Из командной строки:
```bash
python play.py path/to/actions_base.json
```

### Из другого Python модуля:
```python
from play import play_actions

success = play_actions("path/to/actions_base.json")
if success:
    print("Воспроизведение успешно завершено")
```

## Зависимости
Для работы модуля требуются следующие библиотеки:
- `pynput` - для ввода с клавиатуры
- `opencv-python` - для работы с изображениями
- `pyautogui` - для создания скриншотов
- `pywin32` - для работы с Windows API
- `numpy` - для обработки массивов

Установка зависимостей:
```bash
pip install -r requirements.txt
```

## Примечания
- Модуль работает только на Windows (использует win32api)
- Для функции ожидания изображения требуется OpenCV
- Воспроизведение начинается через 3 секунды после запуска
- В случае ошибки выполнения действия, модуль продолжает работу с следующим действием
