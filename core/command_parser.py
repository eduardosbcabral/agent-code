"""Command parser for extracting commands from AI responses."""

import re
from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console
from ui.display import display_info, display_error, display_warning

console = Console()


class CommandParser:
    """Parses commands from AI responses using regex patterns."""
    
    def __init__(self):
        """Initialize the command parser with regex patterns."""
        # Regex patterns for different command types
        self.patterns = {
            'LIST_FILES': re.compile(r'<command>\[CMD:LIST_FILES\]</command>', re.IGNORECASE),
            'READ_FILE': re.compile(r'<command>\[CMD:READ_FILE\("([^"]+)"\)\]</command>', re.IGNORECASE),
            'WRITE_FILE': re.compile(r'<command>\[CMD:WRITE_FILE\("([^"]+)",\s*"(.*?)"\)\]</command>', re.IGNORECASE | re.DOTALL),
            'TERMINAL_COMMAND': re.compile(r'<command>\[CMD:TERMINAL_COMMAND\("([^"]+)"\)\]</command>', re.IGNORECASE),
            'FINISH': re.compile(r'<command>\[CMD:FINISH\]</command>', re.IGNORECASE)
        }
        
        # Pattern for extracting narration
        self.narration_pattern = re.compile(r'<narration>(.*?)</narration>', re.IGNORECASE | re.DOTALL)
        
        # Pattern for extracting final output
        self.final_output_pattern = re.compile(r'<o>(.*?)</o>', re.IGNORECASE | re.DOTALL)
    
    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract commands, narrations, and final output."""
        try:
            commands = []
            narrations = []
            final_output = None
            
            # Extract narrations
            narration_matches = self.narration_pattern.findall(response_text)
            narrations = [match.strip() for match in narration_matches]
            
            # Extract final output
            final_output_match = self.final_output_pattern.search(response_text)
            if final_output_match:
                final_output = final_output_match.group(1).strip()
            
            # Extract commands
            for command_type, pattern in self.patterns.items():
                matches = pattern.finditer(response_text)
                
                for match in matches:
                    if command_type == 'LIST_FILES' or command_type == 'FINISH':
                        commands.append({
                            'type': command_type,
                            'args': [],
                            'position': match.start()
                        })
                    elif command_type == 'READ_FILE':
                        commands.append({
                            'type': command_type,
                            'args': [match.group(1)],
                            'position': match.start()
                        })
                    elif command_type == 'WRITE_FILE':
                        commands.append({
                            'type': command_type,
                            'args': [match.group(1), match.group(2)],
                            'position': match.start()
                        })
                    elif command_type == 'TERMINAL_COMMAND':
                        commands.append({
                            'type': command_type,
                            'args': [match.group(1)],
                            'position': match.start()
                        })
            
            # Sort commands by position in text
            commands.sort(key=lambda x: x['position'])
            
            # Remove position info as it's no longer needed
            for cmd in commands:
                del cmd['position']
            
            display_info(f"Parsed {len(commands)} commands and {len(narrations)} narrations")
            
            return {
                'commands': commands,
                'narrations': narrations,
                'final_output': final_output,
                'has_finish': any(cmd['type'] == 'FINISH' for cmd in commands)
            }
            
        except Exception as e:
            display_error(f"Error parsing response: {e}")
            return {
                'commands': [],
                'narrations': [],
                'final_output': None,
                'has_finish': False,
                'error': str(e)
            }
    
    def validate_commands(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate parsed commands for common issues."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check for FINISH command placement
            finish_commands = [i for i, cmd in enumerate(commands) if cmd['type'] == 'FINISH']
            if len(finish_commands) > 1:
                validation_results['errors'].append("Multiple FINISH commands found")
                validation_results['valid'] = False
            elif len(finish_commands) == 1 and finish_commands[0] != len(commands) - 1:
                validation_results['warnings'].append("FINISH command should be the last command")
            
            # Check for empty file paths
            for i, cmd in enumerate(commands):
                if cmd['type'] in ['READ_FILE', 'WRITE_FILE']:
                    if not cmd['args'] or not cmd['args'][0].strip():
                        validation_results['errors'].append(f"Command {i+1}: Empty file path")
                        validation_results['valid'] = False
                
                # Check for empty write content
                if cmd['type'] == 'WRITE_FILE':
                    if len(cmd['args']) < 2:
                        validation_results['errors'].append(f"Command {i+1}: Missing content for WRITE_FILE")
                        validation_results['valid'] = False
                
                # Check for empty terminal command
                if cmd['type'] == 'TERMINAL_COMMAND':
                    if not cmd['args'] or not cmd['args'][0].strip():
                        validation_results['errors'].append(f"Command {i+1}: Empty terminal command")
                        validation_results['valid'] = False
            
            # Display validation results
            if validation_results['errors']:
                for error in validation_results['errors']:
                    display_error(f"Validation error: {error}")
            
            if validation_results['warnings']:
                for warning in validation_results['warnings']:
                    display_warning(f"Validation warning: {warning}")
            
            return validation_results
            
        except Exception as e:
            display_error(f"Error during command validation: {e}")
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    def format_command_summary(self, commands: List[Dict[str, Any]]) -> str:
        """Create a human-readable summary of parsed commands."""
        if not commands:
            return "No commands found in response"
        
        summary_lines = [f"Found {len(commands)} commands:"]
        
        for i, cmd in enumerate(commands, 1):
            cmd_type = cmd['type']
            args = cmd.get('args', [])
            
            if cmd_type == 'LIST_FILES':
                summary_lines.append(f"  {i}. List all files in workspace")
            elif cmd_type == 'READ_FILE':
                file_path = args[0] if args else "[missing path]"
                summary_lines.append(f"  {i}. Read file: {file_path}")
            elif cmd_type == 'WRITE_FILE':
                file_path = args[0] if args else "[missing path]"
                content_preview = args[1][:50] + "..." if len(args) > 1 and len(args[1]) > 50 else args[1] if len(args) > 1 else "[missing content]"
                summary_lines.append(f"  {i}. Write file: {file_path} ({len(args[1]) if len(args) > 1 else 0} chars)")
            elif cmd_type == 'TERMINAL_COMMAND':
                command = args[0] if args else "[missing command]"
                summary_lines.append(f"  {i}. Execute: {command}")
            elif cmd_type == 'FINISH':
                summary_lines.append(f"  {i}. Finish task")
        
        return "\n".join(summary_lines)
