"""Command execution system for Chapter Agent."""

import os
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import aiofiles
from rich.console import Console
from ui.display import display_info, display_error, display_success, display_warning

console = Console()


class CommandExecutor:
    """Executes commands parsed from AI responses with proper sandboxing."""
    
    def __init__(self, workspace_path: str):
        """Initialize the command executor with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        self.console = Console()
        
        # Ensure workspace exists
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
    async def execute_command(self, command_type: str, args: List[str]) -> Dict[str, Any]:
        """Execute a command and return the result."""
        try:
            display_info(f"Executing {command_type} command...")
            
            if command_type == "LIST_FILES":
                return await self._list_files()
            elif command_type == "READ_FILE":
                return await self._read_file(args[0] if args else "")
            elif command_type == "WRITE_FILE":
                return await self._write_file(args[0] if args else "", args[1] if len(args) > 1 else "")
            elif command_type == "TERMINAL_COMMAND":
                return await self._terminal_command(args[0] if args else "")
            elif command_type == "FINISH":
                return await self._finish()
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
    
    async def _list_files(self) -> Dict[str, Any]:
        """List all files and directories in the workspace."""
        try:
            file_tree = []
            
            def build_tree(path: Path, prefix: str = "", is_last: bool = True):
                """Recursively build file tree representation."""
                if not path.exists():
                    return
                
                # Skip hidden files and common ignore patterns
                skip_patterns = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
                if path.name.startswith('.') and path.name not in {'.env', '.gitignore', '.dockerignore'}:
                    return
                if path.name in skip_patterns:
                    return
                
                connector = "└── " if is_last else "├── "
                relative_path = path.relative_to(self.workspace_path)
                
                if path.is_file():
                    file_tree.append(f"{prefix}{connector}{path.name}")
                elif path.is_dir():
                    file_tree.append(f"{prefix}{connector}{path.name}/")
                    
                    # Get directory contents
                    try:
                        children = sorted([p for p in path.iterdir() if not self._should_skip(p)])
                        for i, child in enumerate(children):
                            is_last_child = i == len(children) - 1
                            next_prefix = prefix + ("    " if is_last else "│   ")
                            build_tree(child, next_prefix, is_last_child)
                    except PermissionError:
                        file_tree.append(f"{prefix}    [Permission Denied]")
            
            # Start building tree from workspace root
            display_info(f"Scanning workspace: {self.workspace_path}")
            build_tree(self.workspace_path)
            
            if not file_tree:
                output = f"Workspace is empty: {self.workspace_path}"
            else:
                output = f"File structure of {self.workspace_path}:\n" + "\n".join(file_tree)
            
            display_success(f"Listed {len(file_tree)} items")
            
            return {
                "success": True,
                "output": output,
                "file_count": len(file_tree)
            }
            
        except Exception as e:
            error_msg = f"Failed to list files: {e}"
            display_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "output": ""
            }
    
    def _should_skip(self, path: Path) -> bool:
        """Check if a path should be skipped during directory scanning."""
        skip_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', '.DS_Store', 'Thumbs.db'
        }
        
        # Skip hidden files except common config files
        if path.name.startswith('.') and path.name not in {'.env', '.gitignore', '.dockerignore', '.editorconfig'}:
            return True
            
        return path.name in skip_patterns
    
    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Read the contents of a file."""
        try:
            if not file_path:
                return {
                    "success": False,
                    "error": "No file path provided",
                    "output": ""
                }
            
            # Resolve path relative to workspace
            full_path = self._resolve_path(file_path)
            
            if not full_path.exists():
                error_msg = f"File does not exist: {file_path}"
                display_error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "output": ""
                }
            
            if not full_path.is_file():
                error_msg = f"Path is not a file: {file_path}"
                display_error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "output": ""
                }
            
            async with aiofiles.open(full_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
            
            display_success(f"Read file: {file_path} ({len(content)} characters)")
            
            return {
                "success": True,
                "output": content,
                "file_path": str(full_path),
                "size": len(content)
            }
            
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            display_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "output": ""
            }
    
    async def _write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            if not file_path:
                return {
                    "success": False,
                    "error": "No file path provided",
                    "output": ""
                }
            
            # Resolve path relative to workspace
            full_path = self._resolve_path(file_path)
            
            # Process content to handle escaped newlines and other escape sequences
            processed_content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(full_path, mode='w', encoding='utf-8') as f:
                await f.write(processed_content)
            
            display_success(f"Wrote file: {file_path} ({len(processed_content)} characters)")
            
            return {
                "success": True,
                "output": f"Successfully wrote {len(processed_content)} characters to {file_path}",
                "file_path": str(full_path),
                "size": len(processed_content)
            }
            
        except Exception as e:
            error_msg = f"Failed to write file {file_path}: {e}"
            display_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "output": ""
            }
    
    async def _terminal_command(self, command: str) -> Dict[str, Any]:
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
    
    async def _finish(self) -> Dict[str, Any]:
        """Handle the FINISH command."""
        display_success("Task completed - FINISH command received")
        return {
            "success": True,
            "output": "Task completed successfully",
            "finished": True
        }
    
    def _resolve_path(self, file_path: str) -> Path:
        """Resolve a file path relative to the workspace with security checks."""
        # Convert to Path object
        path = Path(file_path)
        
        # If it's absolute, make it relative to workspace
        if path.is_absolute():
            # Check if it's within workspace
            try:
                path = path.relative_to(self.workspace_path)
            except ValueError:
                # Path is outside workspace, use just the filename
                path = Path(path.name)
        
        # Resolve relative to workspace
        full_path = (self.workspace_path / path).resolve()
        
        # Security check: ensure resolved path is within workspace
        try:
            full_path.relative_to(self.workspace_path)
        except ValueError:
            # Path tries to escape workspace, use just the filename
            full_path = self.workspace_path / path.name
        
        return full_path
