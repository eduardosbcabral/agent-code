#!/usr/bin/env python3
"""
Test script to validate WRITE_FILE command implementation
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/eduardo/dev/personal/chapter-agent')

from core.command_executor import CommandExecutor
from core.command_parser import CommandParser

async def test_write_file_command():
    """Test the WRITE_FILE command implementation."""
    
    # Create test workspace
    workspace_path = "/home/eduardo/dev/personal/chapter-agent/workspace"
    
    # Initialize components
    executor = CommandExecutor(workspace_path)
    parser = CommandParser()
    
    print("🧪 Testing WRITE_FILE Command Implementation")
    print("=" * 50)
    
    # Test 1: Parse a WRITE_FILE command
    test_content = """# New Python script
import datetime

def greet():
    print(f"Hello! Current time: {datetime.datetime.now()}")
    
if __name__ == "__main__":
    greet()"""
    
    test_response = f"""<narration>I will create a new Python file with a greeting function.</narration>
<command>[CMD:WRITE_FILE("greeting.py", "{test_content}")]</command>"""
    
    print("1. Testing command parsing...")
    parsed = parser.parse_response(test_response)
    print(f"   Parsed commands: {len(parsed['commands'])}")
    
    if parsed['commands']:
        cmd = parsed['commands'][0]
        print(f"   Command type: {cmd['type']}")
        print(f"   File path: {cmd['args'][0] if cmd['args'] else 'N/A'}")
        print(f"   Content length: {len(cmd['args'][1]) if len(cmd['args']) > 1 else 0} characters")
        
        # Test 2: Execute the WRITE_FILE command
        print("\n2. Testing command execution...")
        result = await executor.execute_command(cmd['type'], cmd['args'])
        
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Written to: {result.get('file_path', 'N/A')}")
            print(f"   Bytes written: {result.get('size', 0)}")
            print(f"   Result message: {result['output']}")
            
            # Test 3: Verify the file was actually created
            print("\n3. Verifying file creation...")
            try:
                written_file_path = result.get('file_path')
                if written_file_path and os.path.exists(written_file_path):
                    with open(written_file_path, 'r') as f:
                        actual_content = f.read()
                    print(f"   ✅ File exists: {written_file_path}")
                    print(f"   ✅ Content matches: {actual_content == test_content}")
                    print(f"   ✅ File size: {len(actual_content)} characters")
                    print(f"   Content preview: {actual_content[:100]}{'...' if len(actual_content) > 100 else ''}")
                else:
                    print(f"   ❌ File not found at: {written_file_path}")
            except Exception as e:
                print(f"   ❌ Verification error: {e}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Test 4: Test writing to a subdirectory
    print("\n4. Testing subdirectory creation...")
    subdir_response = """<narration>Creating a config file in a new subdirectory.</narration>
<command>[CMD:WRITE_FILE("config/settings.json", "{\\"debug\\": true, \\"version\\": \\"1.0\\"}")]</command>"""
    
    parsed_subdir = parser.parse_response(subdir_response)
    if parsed_subdir['commands']:
        cmd_subdir = parsed_subdir['commands'][0]
        result_subdir = await executor.execute_command(cmd_subdir['type'], cmd_subdir['args'])
        print(f"   Subdirectory write success: {result_subdir['success']}")
        if result_subdir['success']:
            print(f"   Created: {result_subdir.get('file_path', 'N/A')}")
        else:
            print(f"   Error: {result_subdir.get('error', 'Unknown error')}")
    
    print("\n✅ WRITE_FILE command test completed!")

if __name__ == "__main__":
    asyncio.run(test_write_file_command())
