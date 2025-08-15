# Looper - User Action Automation

A program for recording, decomposing, and replaying user actions (mouse and keyboard).

System requirements: Windows, without screen scaling.

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

After installation, the `looper` command will be available globally from any folder.

Alternative way to run (without installation):
```bash
python main.py --help
```

## Configuration

The program uses the `looper.config` configuration file to set up paths and parameters.

By default, all actions are saved to the `./data` folder.

## Usage

### Recording Actions
```bash
# After package installation (recommended):
looper --record open_notepad
# or short form:
looper -r open_notepad

# Alternatively (without installation):
python main.py --record open_notepad
```

### Playing Actions
```bash
# Basic playback
looper --play open_notepad
# or short form:
looper -p open_notepad

# Playback with fixed delay
looper -p open_notepad --delay 2.5

# Playback with parameters from CSV file
looper -p open_notepad --typing-params typing_parameters.csv

# Dynamic mode (search by reference rectangles)
looper -p open_notepad --dynamic

# Combined modes
looper -p open_notepad --dynamic --delay 2.5
looper -p open_notepad --dynamic --delay 2.5 --typing-params xxx.csv
```

## Command Line Parameters

### Main modes:
- `--record, -r <action_name>` - Record user actions
- `--play, -p <action_name>` - Play actions
- `--help, -h` - Show help
- `--version, -v` - Show version

### Parameters for playback and scenario creation:

- `--dynamic` - Dynamic playback mode (search by reference rectangles)
- `--delay <seconds>` - Fixed delay after click, enter, space (in seconds)
- `--typing-params <csv_file>` - CSV file with parameters for typing actions
- `--sleep <seconds>` - Wait time between scenarios in seconds (default: 3)


## CSV File Format for Typing Parameters

The `typing_parameters.csv` file allows you to set different values for typing actions:

```csv
id,notepad,hello world,C:\Projects\looper\data\open_notepad,2
1,notepad,hello world,C:\Projects\looper\data\open_notepad,2
2,calculator,goodbye world,D:\MyPath,5
```

- The first row contains column headers corresponding to the text of typing actions
- Each subsequent row represents one execution scenario
- The program will execute the scenario for each row with the corresponding parameters
- Between scenario executions, the program waits for the specified time (`--sleep` parameter, default 3 seconds)

## Features

- **Recording**: Captures all mouse and keyboard actions until ESC is pressed. Supports only: English layout, space, enter keys.
- **Playback**: 
  - Executes recorded actions
  - Supports dynamic mode (search by reference rectangles)
  - Creating scenarios with fixed delay
  - Using parameters from CSV files for typing actions
- **Interruption**: Pressing ESC stops recording or playback

## Usage Examples

### Complete workflow:
```bash
# 1. Record actions
looper -r open_notepad

# 2. Play back normally
looper -p open_notepad

# 3. Play back with dynamic mode
looper -p open_notepad --dynamic

# 4. Play back with fixed delay of 2.5 seconds
looper -p open_notepad --delay 2.5

# 5. Play back with parameters from CSV file
looper -p open_notepad --typing-params typing_parameters_base.csv

# 6. Combined mode
looper -p open_notepad --dynamic --delay 2.5 --typing-params typing_parameters_base.csv

# 7. Cut action
## Step 1: create scenario. Press F1 to stop where you need to cut:
looper -sc open_notepad -o test_cut --cut
## Step 2: play scenario.
looper -p open_notepad -f test_cut 

```

## Author

**Lykov Alexander**

## License

This project is distributed under the MIT license. See the [LICENSE](LICENSE) file for details.
