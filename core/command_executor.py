"""Command execution system for Chapter Agent."""

from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console

from tools import FileLister, FileReader, FileWriter, TerminalExecutor, TaskFinisher
from ui.display import display_info, display_error

console = Console()


class CommandExecutor:
    """Executes commands parsed from AI responses with proper sandboxing."""
    
    def __init__(self, workspace_path: str):
        """Initialize the command executor with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        self.console = Console()
        
        # Ensure workspace exists
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize tools
        self.file_lister = FileLister(str(self.workspace_path))
        self.file_reader = FileReader(str(self.workspace_path))
        self.file_writer = FileWriter(str(self.workspace_path))
        self.terminal_executor = TerminalExecutor(str(self.workspace_path))
        self.task_finisher = TaskFinisher()
        
    async def execute_command(self, command_type: str, args: List[str]) -> Dict[str, Any]:
        """Execute a command and return the result."""
        try:
            display_info(f"Executing {command_type} command...")
            
            if command_type == "LIST_FILES":
                return await self.file_lister.list_files()
            elif command_type == "READ_FILE":
                return await self.file_reader.read_file(args[0] if args else "")
            elif command_type == "WRITE_FILE":
                return await self.file_writer.write_file(
                    args[0] if args else "", 
                    args[1] if len(args) > 1 else ""
                )
            elif command_type == "TERMINAL_COMMAND":
                return await self.terminal_executor.execute_command(args[0] if args else "")
            elif command_type == "FINISH":
                return await self.task_finisher.finish_task()
            else:
                return {
                    "success": False,
                    "error": f"Unknown command type: {command_type}",
                    "output": ""
                }
                
        except Exception as e:
            display_error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }
