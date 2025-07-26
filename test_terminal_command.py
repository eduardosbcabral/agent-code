#!/usr/bin/env python3
"""
Test script to validate TERMINAL_COMMAND implementation
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/eduardo/dev/personal/chapter-agent')

from core.command_executor import CommandExecutor
from core.command_parser import CommandParser

async def test_terminal_command():
    """Test the TERMINAL_COMMAND implementation."""
    
    # Create test workspace
    workspace_path = "/home/eduardo/dev/personal/chapter-agent/workspace"
    
    # Initialize components
    executor = CommandExecutor(workspace_path)
    parser = CommandParser()
    
    print("🧪 Testing TERMINAL_COMMAND Implementation")
    print("=" * 50)
    
    # Test 1: Simple directory listing command
    print("1. Testing simple command parsing and execution...")
    test_response_1 = """<narration>I'll list the current directory contents to see what files are available.</narration>
<command>[CMD:TERMINAL_COMMAND("ls -la")]</command>"""
    
    parsed_1 = parser.parse_response(test_response_1)
    print(f"   Parsed commands: {len(parsed_1['commands'])}")
    
    if parsed_1['commands']:
        cmd_1 = parsed_1['commands'][0]
        print(f"   Command type: {cmd_1['type']}")
        print(f"   Command: {cmd_1['args'][0] if cmd_1['args'] else 'N/A'}")
        
        result_1 = await executor.execute_command(cmd_1['type'], cmd_1['args'])
        print(f"   Success: {result_1['success']}")
        print(f"   Exit code: {result_1.get('exit_code', 'N/A')}")
        if result_1['success']:
            output_preview = result_1['output'][:200] + "..." if len(result_1['output']) > 200 else result_1['output']
            print(f"   Output preview: {output_preview}")
        else:
            print(f"   Error: {result_1.get('error', 'Unknown error')}")
    
    # Test 2: Python script execution
    print("\n2. Testing Python script execution...")
    test_response_2 = """<narration>I'll run the greeting.py script to see its output.</narration>
<command>[CMD:TERMINAL_COMMAND("python3 greeting.py")]</command>"""
    
    parsed_2 = parser.parse_response(test_response_2)
    if parsed_2['commands']:
        cmd_2 = parsed_2['commands'][0]
        result_2 = await executor.execute_command(cmd_2['type'], cmd_2['args'])
        print(f"   Python execution success: {result_2['success']}")
        print(f"   Exit code: {result_2.get('exit_code', 'N/A')}")
        if result_2['success']:
            print(f"   Python output: {result_2['output'].strip()}")
        else:
            print(f"   Error: {result_2.get('error', 'Unknown error')}")
    
    # Test 3: File operations via terminal
    print("\n3. Testing file operations via terminal...")
    test_response_3 = """<narration>I'll create a simple text file using echo command.</narration>
<command>[CMD:TERMINAL_COMMAND("echo 'Hello from terminal command!' > terminal_test.txt")]</command>"""
    
    parsed_3 = parser.parse_response(test_response_3)
    if parsed_3['commands']:
        cmd_3 = parsed_3['commands'][0]
        result_3 = await executor.execute_command(cmd_3['type'], cmd_3['args'])
        print(f"   File creation success: {result_3['success']}")
        print(f"   Exit code: {result_3.get('exit_code', 'N/A')}")
        
        # Verify the file was created
        if result_3['success']:
            verify_response = """<command>[CMD:TERMINAL_COMMAND("cat terminal_test.txt")]</command>"""
            parsed_verify = parser.parse_response(verify_response)
            if parsed_verify['commands']:
                cmd_verify = parsed_verify['commands'][0]
                result_verify = await executor.execute_command(cmd_verify['type'], cmd_verify['args'])
                if result_verify['success']:
                    print(f"   ✅ File content: {result_verify['output'].strip()}")
                else:
                    print(f"   ❌ Verification failed: {result_verify.get('error', 'Unknown')}")
    
    # Test 4: Command with error (non-existent command)
    print("\n4. Testing error handling...")
    test_response_4 = """<narration>Testing error handling with invalid command.</narration>
<command>[CMD:TERMINAL_COMMAND("nonexistentcommand12345")]</command>"""
    
    parsed_4 = parser.parse_response(test_response_4)
    if parsed_4['commands']:
        cmd_4 = parsed_4['commands'][0]
        result_4 = await executor.execute_command(cmd_4['type'], cmd_4['args'])
        print(f"   Expected failure success: {not result_4['success']}")  # Should fail
        print(f"   Exit code: {result_4.get('exit_code', 'N/A')}")
        if not result_4['success']:
            print(f"   ✅ Error properly handled: {result_4.get('error', 'No error message')}")
        else:
            print(f"   ❌ Command unexpectedly succeeded")
    
    # Test 5: Multi-line command with pipes
    print("\n5. Testing complex command with pipes...")
    test_response_5 = """<narration>Using pipes to count files in directory.</narration>
<command>[CMD:TERMINAL_COMMAND("ls -1 | wc -l")]</command>"""
    
    parsed_5 = parser.parse_response(test_response_5)
    if parsed_5['commands']:
        cmd_5 = parsed_5['commands'][0]
        result_5 = await executor.execute_command(cmd_5['type'], cmd_5['args'])
        print(f"   Pipe command success: {result_5['success']}")
        print(f"   Exit code: {result_5.get('exit_code', 'N/A')}")
        if result_5['success']:
            file_count = result_5['output'].strip()
            print(f"   ✅ File count: {file_count}")
        else:
            print(f"   Error: {result_5.get('error', 'Unknown error')}")
    
    print("\n✅ TERMINAL_COMMAND test completed!")

if __name__ == "__main__":
    asyncio.run(test_terminal_command())
