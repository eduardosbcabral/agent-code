"""Path utilities for Agent Code tools."""

from pathlib import Path


class PathResolver:
    """Utility for resolving and validating file paths within workspace."""
    
    def __init__(self, workspace_path: str):
        """Initialize the path resolver with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        
    def resolve_path(self, file_path: str) -> Path:
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
    
    def is_path_safe(self, file_path: str) -> bool:
        """Check if a path is safe (within workspace bounds)."""
        try:
            resolved = self.resolve_path(file_path)
            resolved.relative_to(self.workspace_path)
            return True
        except ValueError:
            return False
