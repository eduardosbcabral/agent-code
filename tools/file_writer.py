"""File writer tool for Chapter Agent."""

from pathlib import Path
from typing import Dict, Any
import aiofiles
from ui.display import display_success, display_error
from .path_resolver import PathResolver


class FileWriter:
    """Tool for writing content to files."""
    
    def __init__(self, workspace_path: str):
        """Initialize the file writer with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        self.path_resolver = PathResolver(workspace_path)
        
    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            if not file_path:
                return {
                    "success": False,
                    "error": "No file path provided",
                    "output": ""
                }
            
            # Resolve path relative to workspace
            full_path = self.path_resolver.resolve_path(file_path)
            
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
