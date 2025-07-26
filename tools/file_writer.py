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
            
            # Process content with intelligent escape sequence handling
            processed_content = self._process_content(content)
            
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
    
    def _process_content(self, content: str) -> str:
        """
        Intelligently process content to handle escape sequences.
        
        This function uses a more sophisticated approach to determine when
        escape sequences should be processed vs. preserved.
        """
        if not content:
            return content
            
        # Try to detect if this looks like code/text that has been over-escaped
        # Common patterns that indicate over-escaping:
        
        # 1. Check for Python string patterns with escaped quotes
        import re
        
        # Pattern for Python strings with escaped quotes that should be unescaped
        # e.g., "Hello \"world\"" should become "Hello "world""
        python_string_pattern = r'(\w+\s*=\s*|return\s+|print\s*\()\s*\\"([^"]*)\\"'
        if re.search(python_string_pattern, content):
            # This looks like Python code with over-escaped quotes
            content = self._unescape_python_strings(content)
        
        # 2. Handle other common escape sequences
        # Only process these if they appear to be literal escape sequences
        if self._should_process_escapes(content):
            content = content.replace('\\n', '\n')
            content = content.replace('\\t', '\t')
            content = content.replace('\\r', '\r')
            # Handle double backslashes last
            content = content.replace('\\\\', '\\')
        
        return content
    
    def _unescape_python_strings(self, content: str) -> str:
        """Unescape Python string literals that have been over-escaped."""
        import re
        
        # Replace escaped quotes in common Python contexts
        # Handle return statements with escaped quotes
        content = re.sub(r'(return\s+)\\"([^"]*)\\"', r'\1"\2"', content)
        
        # Handle print statements with escaped quotes
        content = re.sub(r'(print\s*\(\s*)\\"([^"]*)\\"', r'\1"\2"', content)
        
        # Handle variable assignments with escaped quotes
        content = re.sub(r'(\w+\s*=\s*)\\"([^"]*)\\"', r'\1"\2"', content)
        
        # Handle function calls with escaped quotes
        content = re.sub(r'(\w+\s*\(\s*)\\"([^"]*)\\"', r'\1"\2"', content)
        
        # Handle if statements and comparisons
        content = re.sub(r'(==\s*)\\"([^"]*)\\"', r'\1"\2"', content)
        
        # Handle escaped single quotes in similar contexts
        content = re.sub(r"(return\s+)\\'([^']*)\\'", r'''\1'\2' ''', content)
        content = re.sub(r"(print\s*\(\s*)\\'([^']*)\\'", r'''\1'\2' ''', content)
        
        return content
    
    def _should_process_escapes(self, content: str) -> bool:
        """
        Determine if escape sequences should be processed.
        
        Returns True if the content appears to contain literal escape sequences
        that should be converted to their actual characters.
        """
        # Don't process if content already has actual newlines/tabs
        # (indicates it's already properly formatted)
        if '\n' in content or '\t' in content:
            return False
            
        # Process if we see literal escape sequences
        if '\\n' in content or '\\t' in content or '\\r' in content:
            return True
            
        return False
