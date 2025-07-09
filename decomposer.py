import json
import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from config import get_config

class BaseActionDecomposer:
    def __init__(self, max_click_delay: float = 0.5):
        self.max_click_delay = max_click_delay
        self.base_actions = []
        self.action_id_counter = 1
    
    def load_actions(self, filename: str) -> List[Dict]:
        """Load actions from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filename}: {e}")
            return []
    
    def save_base_actions(self, filename: str):
        """Save base actions to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.base_actions, f, ensure_ascii=False, indent=4)
            print(f"Base actions saved to {filename}")
        except Exception as e:
            print(f"Error saving to {filename}: {e}")
    
    def find_mouse_clicks(self, actions: List[Dict], start_index: int) -> Optional[Dict]:
        """Find and create mouse click base action starting from given index"""
        if start_index >= len(actions):
            return None
            
        action = actions[start_index]
        
        # Check if this is a mouse down event
        if (action.get('source') != 'mouse' or 
            action.get('dir') != 'down' or
            action.get('button') not in ['left', 'right']):
            return None
        
        # Look for corresponding up event
        button = action.get('button')
        x, y = action.get('x'), action.get('y')
        down_timestamp = action.get('timestamp')
        
        for i in range(start_index + 1, len(actions)):
            next_action = actions[i]
            
            # Check if this is the matching up event
            if (next_action.get('source') == 'mouse' and
                next_action.get('dir') == 'up' and
                next_action.get('button') == button and
                abs(next_action.get('x') - x)<10 and
                abs(next_action.get('y') - y)<10):
                
                up_timestamp = next_action.get('timestamp')
                delay = up_timestamp - down_timestamp
               
                # Check if within max delay
                if delay <= self.max_click_delay:
                    return {
                        'id': self.action_id_counter,
                        'name': f'click {button}',
                        'type': 'mouse_click',
                        'button': button,
                        'x': x,
                        'y': y,
                        'start_timestamp': down_timestamp,
                        'end_timestamp': up_timestamp,
                        'delay': delay,
                        'consumed_indices': [start_index, i]
                    }
                break
        
        return None
    
    def find_typing_sequence(self, actions: List[Dict], start_index: int) -> Optional[Dict]:
        """Find and create typing sequence base action starting from given index"""
        if start_index >= len(actions):
            return None
            
        action = actions[start_index]
        
        # Check if this is a keyboard character input (not enter or space)
        if (action.get('source') != 'keyboard' or 
            action.get('key') in ['\n', ' '] or
            not action.get('key', '').isprintable()):
            return None
        
        # Collect consecutive keyboard character inputs (including space)
        typing_sequence = ""
        consumed_indices = []
        start_timestamp = action.get('timestamp')
        end_timestamp = start_timestamp
        
        for i in range(start_index, len(actions)):
            curr_action = actions[i]
            
            # Check if this is a keyboard character input
            if (curr_action.get('source') == 'keyboard' and
                curr_action.get('key') not in ['\n'] and
                curr_action.get('key', '').isprintable()):
                
                typing_sequence += curr_action.get('key', '')
                consumed_indices.append(i)
                end_timestamp = curr_action.get('timestamp')
            else:
                # Stop at first non-character input
                break
        
        if typing_sequence:
            return {
                'name': 'typing',
                'type': 'keyboard_typing',
                'text': typing_sequence,
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'consumed_indices': consumed_indices
            }
        
        return None
    
    def find_enter_action(self, actions: List[Dict], start_index: int) -> Optional[Dict]:
        """Find and create enter key base action"""
        if start_index >= len(actions):
            return None
            
        action = actions[start_index]
        
        if (action.get('source') == 'keyboard' and action.get('key') == '\n'):
            return {
                'id': self.action_id_counter,
                'name': 'enter',
                'type': 'keyboard_enter',
                'timestamp': action.get('timestamp'),
                'layout': action.get('layout'),
                'consumed_indices': [start_index]
            }
        
        return None
    
    def find_space_action(self, actions: List[Dict], start_index: int) -> Optional[Dict]:
        """Find and create space key base action (standalone, not part of typing)"""
        if start_index >= len(actions):
            return None
            
        action = actions[start_index]
        
        # Space is now handled within typing sequences, so this method is kept for compatibility
        # but will not be used in the main decomposition logic
        if (action.get('source') == 'keyboard' and action.get('key') == ' '):
            return {
                'id': self.action_id_counter,
                'name': 'space',
                'type': 'keyboard_space',
                'timestamp': action.get('timestamp'),
                'layout': action.get('layout'),
                'consumed_indices': [start_index]
            }
        
        return None
    
    def create_wait_action(self, time_seconds: float) -> Dict:
        """Create a wait action with timer event"""
        wait_action = {
            'id': self.action_id_counter,
            'name': 'wait',
            'event': {
                'name': 'timer',
                'time': time_seconds
            }
        }
        self.action_id_counter += 1
        return wait_action

    def decompose_actions(self, actions: List[Dict]):
        """Decompose actions into base actions"""
        self.base_actions = []
        self.action_id_counter = 1
        consumed_indices = set()
        
        i = 0
        last_action_timestamp = 0
        
        while i < len(actions):
            if i in consumed_indices:
                i += 1
                continue
            
            # Try to find base actions in order of priority
            base_action = None
            
            # Try mouse click
            base_action = self.find_mouse_clicks(actions, i)
            if base_action:
                # Add wait action if there's a delay from previous action
                if last_action_timestamp > 0:
                    delay = base_action['start_timestamp'] - last_action_timestamp
                    if delay > 0.1:  # Only add wait if delay is significant
                        wait_action = self.create_wait_action(delay)
                        self.base_actions.append(wait_action)
                
                base_action['id'] = self.action_id_counter
                self.action_id_counter += 1
                
                for idx in base_action['consumed_indices']:
                    consumed_indices.add(idx)
                self.base_actions.append(base_action)
                last_action_timestamp = base_action['end_timestamp']
                i += 1
                continue

            # Try space
            base_action = self.find_space_action(actions, i)
            if base_action:
                # Add wait action if there's a delay from previous action
                if last_action_timestamp > 0:
                    delay = base_action['timestamp'] - last_action_timestamp
                    if delay > 0.1:  # Only add wait if delay is significant
                        wait_action = self.create_wait_action(delay)
                        self.base_actions.append(wait_action)
                
                base_action['id'] = self.action_id_counter
                self.action_id_counter += 1
                
                consumed_indices.add(i)
                self.base_actions.append(base_action)
                last_action_timestamp = base_action['timestamp']
                i += 1
                continue
            
            # Try typing sequence (space is now included in typing)
            base_action = self.find_typing_sequence(actions, i)
            if base_action:
                # Add wait action if there's a delay from previous action
                if last_action_timestamp > 0:
                    delay = base_action['start_timestamp'] - last_action_timestamp
                    if delay > 0.1:  # Only add wait if delay is significant
                        wait_action = self.create_wait_action(delay)
                        self.base_actions.append(wait_action)
                
                base_action['id'] = self.action_id_counter
                self.action_id_counter += 1
                
                for idx in base_action['consumed_indices']:
                    consumed_indices.add(idx)
                self.base_actions.append(base_action)
                last_action_timestamp = base_action['end_timestamp']
                i = max(base_action['consumed_indices']) + 1
                continue
            
            # Try enter
            base_action = self.find_enter_action(actions, i)
            if base_action:
                # Add wait action if there's a delay from previous action
                if last_action_timestamp > 0:
                    delay = base_action['timestamp'] - last_action_timestamp
                    if delay > 0.1:  # Only add wait if delay is significant
                        wait_action = self.create_wait_action(delay)
                        self.base_actions.append(wait_action)
                
                base_action['id'] = self.action_id_counter
                self.action_id_counter += 1
                
                consumed_indices.add(i)
                self.base_actions.append(base_action)
                last_action_timestamp = base_action['timestamp']
                i += 1
                continue
            
            # If no base action found, skip this action
            print(f"Warning: Could not decompose action at index {i}: {actions[i]}")
            i += 1
    
    def print_summary(self):
        """Print summary of decomposed actions"""
        print(f"\nDecomposition Summary:")
        print(f"Total base actions: {len(self.base_actions)}")
        
        action_counts = {}
        for action in self.base_actions:
            action_type = action['name']
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        for action_type, count in action_counts.items():
            print(f"  {action_type}: {count}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python decomposer.py <action_name>")
        print("Example: python decomposer.py open_notepad")
        return
    
    action_name = sys.argv[1]
    
    # Construct file paths according to concept.md
    action_dir = os.path.join(".", action_name)
    input_file = os.path.join(action_dir, "log.json")
    output_file = os.path.join(action_dir, "actions_base.json")
    
    # Check if action directory and log file exist
    if not os.path.exists(action_dir):
        print(f"Error: Action directory '{action_dir}' not found")
        return
    
    if not os.path.exists(input_file):
        print(f"Error: Log file '{input_file}' not found")
        return
    
    decomposer = BaseActionDecomposer()
    
    # Load actions
    actions = decomposer.load_actions(input_file)
    if not actions:
        return
    
    print(f"Loaded {len(actions)} actions from {input_file}")
    
    # Decompose actions
    decomposer.decompose_actions(actions)
    
    # Print summary
    decomposer.print_summary()
    
    # Save base actions
    decomposer.save_base_actions(output_file)

def decompose_action(action_name: str) -> bool:
    """
    Decompose action for use from looper.py
    Returns True if decomposition was successful, False otherwise
    """
    # Получаем конфигурацию
    cfg = get_config()
    
    # Определяем пути через конфигурацию
    action_dir = cfg.get_action_path(action_name)
    input_file = cfg.get_log_file_path(action_name)
    output_file = cfg.get_actions_base_file_path(action_name)
    
    print(f"Декомпозиция действия '{action_name}'")
    print(f"Директория действий: {action_dir}")
    print(f"Входной файл: {input_file}")
    print(f"Выходной файл: {output_file}")
    
    # Check if action directory and log file exist
    if not action_dir.exists():
        print(f"Error: Action directory '{action_dir}' not found")
        return False
    
    if not input_file.exists():
        print(f"Error: Log file '{input_file}' not found")
        return False
    
    decomposer = BaseActionDecomposer()
    
    # Load actions
    actions = decomposer.load_actions(str(input_file))
    if not actions:
        return False
    
    print(f"Loaded {len(actions)} actions from {input_file}")
    
    # Decompose actions
    decomposer.decompose_actions(actions)
    
    # Print summary
    decomposer.print_summary()
    
    # Save base actions
    decomposer.save_base_actions(str(output_file))
    
    return True

if __name__ == "__main__":
    main()