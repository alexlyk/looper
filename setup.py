from setuptools import setup, find_packages

setup(
    name="looper",
    version="1.0.0",
    description="Automation tool for recording and replaying user actions",
    author="alexlyk",
    packages=find_packages(),
    py_modules=["looper", "config", "decomposer", "mouse_clicker", "play", "rec", "scenario_creator"],
    entry_points={
        "console_scripts": [
            "looper=looper:main",
        ],
    },
    install_requires=[
        # Добавьте зависимости из requirements.txt если есть
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
