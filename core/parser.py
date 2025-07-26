"""Thought extraction and parsing utilities for Chapter Agent."""

import re
from typing import List, Dict, Any, Tuple, Optional

from rich.console import Console
from ui.display import display_error, display_info

console = Console()


class ThoughtExtractor:
    """Extracts and parses AI thoughts and actions from responses."""
    
    def __init__(self):
        """Initialize the thought extractor."""
        # Regex patterns for parsing responses
        self.narration_pattern = r'<narration>(.*?)</narration>'
        self.command_pattern = r'<command>(.*?)</command>'
        self.output_pattern = r'<output>(.*?)</output>'
        self.finish_pattern = r'\[CMD:FINISH\]'
        
        # Command patterns
        self.cmd_read_file = r'\[CMD:READ_FILE\("([^"]+)"\)\]'
        self.cmd_write_file = r'\[CMD:WRITE_FILE\("([^"]+)",\s*"(.*?)"\)\]'
        self.cmd_list_files = r'\[CMD:LIST_FILES\]'
        self.cmd_terminal = r'\[CMD:TERMINAL_COMMAND\("([^"]+)"\)\]'
        self.cmd_finish = r'\[CMD:FINISH\]'
    
    def extract_thoughts_and_actions(self, response_text: str) -> Dict[str, Any]:
        """Extract thoughts and parse actions from AI response."""
        try:
            # Look for explicit thinking sections (if model supports it)
            thoughts = self._extract_explicit_thoughts(response_text)
            
            # Parse actions from the response
            actions = self._parse_actions(response_text)
            
            # Check for finish command and output
            has_finish = bool(re.search(self.finish_pattern, response_text))
            final_output = None
            
            if has_finish:
                output_matches = re.findall(self.output_pattern, response_text, re.DOTALL)
                if output_matches:
                    final_output = output_matches[-1].strip()
            
            return {
                'thoughts': thoughts,
                'actions': actions,
                'has_finish': has_finish,
                'final_output': final_output,
                'raw_response': response_text
            }
            
        except Exception as e:
            display_error(f"Error extracting thoughts and actions: {e}")
            return {
                'thoughts': f"Error parsing response: {e}",
                'actions': [],
                'has_finish': False,
                'final_output': None,
                'raw_response': response_text
            }
    
    def _extract_explicit_thoughts(self, text: str) -> str:
        """Extract explicit thinking sections if present."""
        # This would be populated by the Gemini client if thinking is enabled
        # For now, we'll look for any reasoning patterns in the text
        
        # Look for common thinking patterns
        thinking_indicators = [
            r'(?i)(?:i think|i need to|let me|first,|the user wants|to accomplish)',
            r'(?i)(?:my plan|my approach|i should|i will|the task is)'
        ]
        
        thoughts = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(re.search(pattern, line) for pattern in thinking_indicators):
                thoughts.append(line)
        
        if thoughts:
            return '\n'.join(thoughts)
        
        return "No explicit thoughts detected in response."
    
    def _parse_actions(self, text: str) -> List[Dict[str, Any]]:
        """Parse action sequences from the response text."""
        actions = []
        
        # Find all narration/command pairs
        narrations = re.findall(self.narration_pattern, text, re.DOTALL)
        commands = re.findall(self.command_pattern, text, re.DOTALL)
        
        # Match narrations with commands
        for i in range(max(len(narrations), len(commands))):
            narration = narrations[i].strip() if i < len(narrations) else ""
            command = commands[i].strip() if i < len(commands) else ""
            
            if command:
                action = self._parse_single_command(command, narration)
                if action:
                    actions.append(action)
        
        return actions
    
    def _parse_single_command(self, command: str, narration: str = "") -> Optional[Dict[str, Any]]:
        """Parse a single command string into an action dictionary."""
        try:
            # READ_FILE command
            match = re.search(self.cmd_read_file, command)
            if match:
                return {
                    'type': 'READ_FILE',
                    'narration': narration,
                    'command': command,
                    'params': {'file_path': match.group(1)}
                }
            
            # WRITE_FILE command
            match = re.search(self.cmd_write_file, command, re.DOTALL)
            if match:
                return {
                    'type': 'WRITE_FILE',
                    'narration': narration,
                    'command': command,
                    'params': {
                        'file_path': match.group(1),
                        'content': match.group(2)
                    }
                }
            
            # LIST_FILES command
            if re.search(self.cmd_list_files, command):
                return {
                    'type': 'LIST_FILES',
                    'narration': narration,
                    'command': command,
                    'params': {}
                }
            
            # TERMINAL_COMMAND
            match = re.search(self.cmd_terminal, command)
            if match:
                return {
                    'type': 'TERMINAL_COMMAND',
                    'narration': narration,
                    'command': command,
                    'params': {'terminal_command': match.group(1)}
                }
            
            # FINISH command
            if re.search(self.cmd_finish, command):
                return {
                    'type': 'FINISH',
                    'narration': narration,
                    'command': command,
                    'params': {}
                }
            
            # Unknown command
            display_error(f"Unknown command format: {command}")
            return {
                'type': 'UNKNOWN',
                'narration': narration,
                'command': command,
                'params': {},
                'error': 'Unknown command format'
            }
            
        except Exception as e:
            display_error(f"Error parsing command '{command}': {e}")
            return {
                'type': 'ERROR',
                'narration': narration,
                'command': command,
                'params': {},
                'error': str(e)
            }
    
    def validate_action_sequence(self, actions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate that an action sequence is well-formed."""
        if not actions:
            return True, "No actions to validate"
        
        # Check for FINISH command
        finish_actions = [a for a in actions if a['type'] == 'FINISH']
        
        if len(finish_actions) > 1:
            return False, "Multiple FINISH commands found"
        
        if finish_actions and actions[-1]['type'] != 'FINISH':
            return False, "FINISH command must be the last action"
        
        # Check for invalid command types
        valid_types = {'READ_FILE', 'WRITE_FILE', 'LIST_FILES', 'TERMINAL_COMMAND', 'FINISH'}
        invalid_actions = [a for a in actions if a['type'] not in valid_types]
        
        if invalid_actions:
            invalid_types = [a['type'] for a in invalid_actions]
            return False, f"Invalid action types found: {invalid_types}"
        
        return True, "Action sequence is valid"
