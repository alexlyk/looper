# Установка Looper CLI

## Установка пакета

Для установки пакета в режиме разработки выполните следующие команды в корневой директории проекта:

```bash
# Перейдите в директорию проекта
cd c:\Projects\looper

# Установите пакет в режиме разработки
pip install -e .
```

После установки команда `looper` будет доступна глобально в вашей системе.

## Проверка установки

Проверьте, что установка прошла успешно:

```bash
looper --help
looper --version
```

## Использование

После установки вы можете использовать команды без `python looper.py`:

```bash
# Вместо: python looper.py -r open_notepad
looper -r open_notepad

# Вместо: python looper.py -p open_notepad
looper -p open_notepad

# Вместо: python looper.py -d open_notepad
looper -d open_notepad

# Вместо: python looper.py -sc open_notepad -o scenario_name
looper -sc open_notepad -o scenario_name
```

## Удаление

Для удаления пакета:

```bash
pip uninstall looper
```
