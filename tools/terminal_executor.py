"""Terminal command execution tool for Chapter Agent."""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any
from ui.display import display_info, display_success, display_warning, display_error


class TerminalExecutor:
    """Tool for executing terminal commands in the workspace."""
    
    def __init__(self, workspace_path: str):
        """Initialize the terminal executor with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a terminal command in the workspace."""
        try:
            if not command:
                return {
                    "success": False,
                    "error": "No command provided",
                    "output": ""
                }
            
            display_info(f"Executing: {command}")
            
            # Execute command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=str(self.workspace_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')
                
                output = ""
                if stdout_text:
                    output += f"STDOUT:\n{stdout_text}\n"
                if stderr_text:
                    output += f"STDERR:\n{stderr_text}\n"
                
                success = process.returncode == 0
                
                if success:
                    display_success(f"Command completed with exit code {process.returncode}")
                else:
                    display_warning(f"Command completed with exit code {process.returncode}")
                
                return {
                    "success": success,
                    "output": output.strip() if output else f"Command completed with exit code {process.returncode}",
                    "exit_code": process.returncode
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                error_msg = "Command timed out after 30 seconds"
                display_error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "output": ""
                }
                
        except Exception as e:
            error_msg = f"Failed to execute command '{command}': {e}"
            display_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "output": ""
            }
