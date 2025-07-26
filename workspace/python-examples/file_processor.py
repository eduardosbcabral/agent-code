import os
import json
from pathlib import Path

def read_text_file(file_path):
    """Read content from a text file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "File not found"

def write_text_file(file_path, content):
    """Write content to a text file."""
    with open(file_path, 'w') as f:
        f.write(content)

def list_files_in_directory(directory):
    """List all files in a directory."""
    path = Path(directory)
    if path.exists():
        return [str(f) for f in path.iterdir() if f.is_file()]
    return []

def count_lines_in_file(file_path):
    """Count the number of lines in a file."""
    try:
        with open(file_path, 'r') as f:
            return len(f.readlines())
    except FileNotFoundError:
        return 0

def process_json_file(file_path):
    """Process a JSON file and return data."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

if __name__ == "__main__":
    # Example usage
    print("File Processor Demo")
    
    # Create a sample file
    sample_content = "Hello, World!\nThis is a test file.\nIt has multiple lines."
    write_text_file("sample.txt", sample_content)
    
    # Read and display
    content = read_text_file("sample.txt")
    print(f"File content:\n{content}")
    
    # Count lines
    line_count = count_lines_in_file("sample.txt")
    print(f"Line count: {line_count}")
    
    # Clean up
    os.remove("sample.txt")
