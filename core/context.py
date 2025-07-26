"""Project context builder for Chapter Agent."""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import aiofiles

from rich.console import Console
from ui.display import display_error, display_info

console = Console()


class ProjectContextBuilder:
    """Builds comprehensive project context from a directory."""
    
    def __init__(self, root_directory: Path):
        """Initialize with the root directory to scan."""
        self.root_directory = Path(root_directory).resolve()
        self.max_file_size = 1024 * 1024  # 1MB max file size
        self.excluded_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', '.env', 'dist', 'build', '.next',
            '.docker', 'coverage', '.nyc_output', 'target'
        }
        self.excluded_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.pdf',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.exe', '.bin'
        }
    
    async def build_context(self) -> str:
        """Build the complete project context string."""
        try:
            display_info(f"Scanning project directory: {self.root_directory}")
            
            # Get file structure
            structure = await self._get_directory_structure()
            
            # Get file contents
            file_contents = await self._get_file_contents()
            
            # Build the context string
            context = self._format_context(structure, file_contents)
            
            display_info(f"Project context built: {len(file_contents)} files processed")
            return context
            
        except Exception as e:
            display_error(f"Failed to build project context: {e}")
            return f"Error building project context: {e}"
    
    async def _get_directory_structure(self) -> str:
        """Get the directory structure as a tree."""
        structure_lines = []
        
        def add_directory(path: Path, prefix: str = ""):
            """Recursively add directory structure."""
            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                
                for i, item in enumerate(items):
                    if item.name.startswith('.') and item.name not in {'.env.example', '.gitignore'}:
                        continue
                    
                    if item.is_dir() and item.name in self.excluded_dirs:
                        continue
                    
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    structure_lines.append(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir():
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        add_directory(item, next_prefix)
                        
            except PermissionError:
                structure_lines.append(f"{prefix}└── [Permission Denied]")
        
        structure_lines.append(f"{self.root_directory.name}/")
        add_directory(self.root_directory)
        
        return "\n".join(structure_lines)
    
    async def _get_file_contents(self) -> List[Dict[str, Any]]:
        """Get contents of all readable files."""
        file_contents = []
        
        for file_path in self._get_text_files():
            try:
                # Check file size
                if file_path.stat().st_size > self.max_file_size:
                    file_contents.append({
                        'path': str(file_path.relative_to(self.root_directory)),
                        'content': f"[File too large: {file_path.stat().st_size} bytes]",
                        'type': 'large_file'
                    })
                    continue
                
                # Read file content
                async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = await f.read()
                
                file_contents.append({
                    'path': str(file_path.relative_to(self.root_directory)),
                    'content': content,
                    'type': 'text_file'
                })
                
            except Exception as e:
                file_contents.append({
                    'path': str(file_path.relative_to(self.root_directory)),
                    'content': f"[Error reading file: {e}]",
                    'type': 'error'
                })
        
        return file_contents
    
    def _get_text_files(self):
        """Generator for all text files in the project."""
        for root, dirs, files in os.walk(self.root_directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip excluded extensions
                if file_path.suffix.lower() in self.excluded_extensions:
                    continue
                
                # Skip hidden files (except specific ones)
                if file.startswith('.') and file not in {'.env.example', '.gitignore'}:
                    continue
                
                yield file_path
    
    def _format_context(self, structure: str, file_contents: List[Dict[str, Any]]) -> str:
        """Format the complete context string."""
        context_parts = []
        
        # Add header
        context_parts.append("=== PROJECT CONTEXT ===")
        context_parts.append(f"Working Directory: {self.root_directory}")
        context_parts.append(f"Total Files: {len(file_contents)}")
        context_parts.append("")
        
        # Add directory structure
        context_parts.append("=== DIRECTORY STRUCTURE ===")
        context_parts.append(structure)
        context_parts.append("")
        
        # Add file contents
        context_parts.append("=== FILE CONTENTS ===")
        
        for file_info in file_contents:
            context_parts.append(f"--- File: {file_info['path']} ---")
            context_parts.append(file_info['content'])
            context_parts.append("")
        
        return "\n".join(context_parts)
