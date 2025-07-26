"""File listing tool for Agent Code."""

from pathlib import Path
from typing import Dict, Any
from ui.display import display_info, display_success, display_error


class FileLister:
    """Tool for listing files and directories in the workspace."""
    
    def __init__(self, workspace_path: str):
        """Initialize the file lister with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        
    async def list_files(self) -> Dict[str, Any]:
        """List all files and directories in the workspace."""
        try:
            file_tree = []
            
            def build_tree(path: Path, prefix: str = "", is_last: bool = True):
                """Recursively build file tree representation."""
                if not path.exists():
                    return
                
                # Skip hidden files and common ignore patterns
                if self._should_skip(path):
                    return
                
                connector = "└── " if is_last else "├── "
                
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
