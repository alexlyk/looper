import json
import sys
from typing import List, Dict, Any, Optional

class BaseActionDecomposer:
    def __init__(self, max_click_delay: float = 0.3):
        self.max_click_delay = max_click_delay
        self.base_actions = []
    
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
        
        # Collect consecutive keyboard character inputs
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
        
        if (action.get('source') == 'keyboard' and action.get('key') == ' '):
            return {
                'name': 'space',
                'type': 'keyboard_space',
                'timestamp': action.get('timestamp'),
                'layout': action.get('layout'),
                'consumed_indices': [start_index]
            }
        
        return None
    
    def decompose_actions(self, actions: List[Dict]):
        """Decompose actions into base actions"""
        self.base_actions = []
        consumed_indices = set()
        
        i = 0
        while i < len(actions):
            if i in consumed_indices:
                i += 1
                continue
            
            # Try to find base actions in order of priority
            base_action = None
            
            # Try mouse click
            base_action = self.find_mouse_clicks(actions, i)
            if base_action:
                for idx in base_action['consumed_indices']:
                    consumed_indices.add(idx)
                self.base_actions.append(base_action)
                i += 1
                continue
            
            # Try space
            base_action = self.find_space_action(actions, i)
            if base_action:
                consumed_indices.add(i)
                self.base_actions.append(base_action)
                i += 1
                continue
            
            # Try typing sequence
            base_action = self.find_typing_sequence(actions, i)
            if base_action:
                for idx in base_action['consumed_indices']:
                    consumed_indices.add(idx)
                self.base_actions.append(base_action)
                i = max(base_action['consumed_indices']) + 1
                continue
            
            # Try enter
            base_action = self.find_enter_action(actions, i)
            if base_action:
                consumed_indices.add(i)
                self.base_actions.append(base_action)
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
        print("Usage: python bactor.py <input_actions.json> [output_base_actions.json]")
        print("Example: python bactor.py actions.json base_actions.json")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "base_actions.json"
    
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

if __name__ == "__main__":
    main()