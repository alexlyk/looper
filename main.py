#!/usr/bin/env python3
"""
Точка входа для приложения Looper
"""

import sys
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Импортируем и запускаем главную функцию
from looper import main

if __name__ == "__main__":
    main()
