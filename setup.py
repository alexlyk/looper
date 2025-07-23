from setuptools import setup, find_packages

setup(
    name="looper",
    version="1.0.0",
    description="Automation tool for recording and replaying user actions",
    author="alexlyk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "looper=looper:main",
        ],
    },
    install_requires=[
        "pynput>=1.7.6",
        "opencv-python>=4.5.0",
        "pyautogui>=0.9.54",
        "pywin32>=306",
        "numpy>=1.21.0",
        "Pillow>=8.0.0",
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
