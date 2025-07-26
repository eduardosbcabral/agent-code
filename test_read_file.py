#!/usr/bin/env python3
"""
Quick test script to validate READ_FILE command implementation
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/eduardo/dev/personal/chapter-agent')

from core.command_executor import CommandExecutor
from core.command_parser import CommandParser

async def test_read_file_command():
    """Test the READ_FILE command implementation."""
    
    # Create test workspace
    workspace_path = "/home/eduardo/dev/personal/chapter-agent/workspace"
    
    # Initialize components
    executor = CommandExecutor(workspace_path)
    parser = CommandParser()
    
    print("🧪 Testing READ_FILE Command Implementation")
    print("=" * 50)
    
    # Test 1: Parse a READ_FILE command
    test_response = """<narration>I need to read the test.py file to see its contents.</narration>
<command>[CMD:READ_FILE("test.py")]</command>"""
    
    print("1. Testing command parsing...")
    parsed = parser.parse_response(test_response)
    print(f"   Parsed commands: {len(parsed['commands'])}")
    
    if parsed['commands']:
        cmd = parsed['commands'][0]
        print(f"   Command type: {cmd['type']}")
        print(f"   Arguments: {cmd['args']}")
        
        # Test 2: Execute the READ_FILE command
        print("\n2. Testing command execution...")
        result = await executor.execute_command(cmd['type'], cmd['args'])
        
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   File path: {result.get('file_path', 'N/A')}")
            print(f"   Content size: {result.get('size', 0)} characters")
            print(f"   Content preview: {result['output'][:100]}{'...' if len(result['output']) > 100 else ''}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n✅ READ_FILE command test completed!")

if __name__ == "__main__":
    asyncio.run(test_read_file_command())
