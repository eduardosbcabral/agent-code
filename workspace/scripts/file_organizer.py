import os
import shutil
from pathlib import Path

def organize_files_by_extension(source_dir, target_dir):
    """Organize files in source directory by their extensions."""
    # Bug: missing Path conversion
    source_path = source_dir
    target_path = Path(target_dir)
    
    # Create target directory if it doesn't exist
    target_path.mkdir(exist_ok=True)
    
    # File type categories
    file_categories = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'spreadsheets': ['.xls', '.xlsx', '.csv'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'code': ['.py', '.js', '.html', '.css', '.java', '.cpp'],
        'audio': ['.mp3', '.wav', '.flac', '.aac'],
        'video': ['.mp4', '.avi', '.mkv', '.mov']
    }
    
    # Process each file
    for file_path in source_path.iterdir():
        if file_path.is_file():
            file_ext = file_path.suffix.lower()
            
            # Find appropriate category
            category = 'misc'
            for cat, extensions in file_categories.items():
                if file_ext in extensions:
                    category = cat
                    break
            
            # Create category directory
            category_dir = target_path / category
            category_dir.mkdir(exist_ok=True)
            
            # Bug: incorrect move operation
            shutil.move(file_path, category_dir)

def clean_empty_directories(directory):
    """Remove empty directories recursively."""
    dir_path = Path(directory)
    
    # Bug: infinite loop potential
    for subdir in dir_path.iterdir():
        if subdir.is_dir():
            clean_empty_directories(subdir)
            # Remove if empty
            if not any(subdir.iterdir()):
                subdir.rmdir()

def get_file_stats(directory):
    """Get statistics about files in directory."""
    dir_path = Path(directory)
    stats = {
        'total_files': 0,
        'total_size': 0,
        'file_types': {}
    }
    
    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            stats['total_files'] += 1
            stats['total_size'] += file_path.stat().st_size
            
            ext = file_path.suffix.lower()
            if ext in stats['file_types']:
                stats['file_types'][ext] += 1
            else:
                stats['file_types'][ext] = 1
    
    return stats

if __name__ == "__main__":
    # Example usage
    source = "./test_files"
    target = "./organized_files"
    
    try:
        organize_files_by_extension(source, target)
        print(f"Files organized from {source} to {target}")
        
        stats = get_file_stats(target)
        print(f"Organized {stats['total_files']} files")
        print(f"Total size: {stats['total_size']} bytes")
        
    except Exception as e:
        print(f"Error organizing files: {e}")
