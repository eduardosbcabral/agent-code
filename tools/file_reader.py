"""File reader tool for Agent Code."""

from pathlib import Path
from typing import Dict, Any
import aiofiles
from ui.display import display_success, display_error
from .path_resolver import PathResolver


class FileReader:
    """Tool for reading file contents."""
    
    def __init__(self, workspace_path: str):
        """Initialize the file reader with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        self.path_resolver = PathResolver(workspace_path)
        
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read the contents of a file."""
        try:
            if not file_path:
                return {
                    "success": False,
                    "error": "No file path provided",
                    "output": ""
                }
            
            # Resolve path relative to workspace
            full_path = self.path_resolver.resolve_path(file_path)
            
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
