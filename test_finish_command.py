#!/usr/bin/env python3
"""
Test script to validate FINISH command and command limit implementation
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/eduardo/dev/personal/chapter-agent')

from core.command_executor import CommandExecutor
from core.command_parser import CommandParser

async def test_finish_command():
    """Test the FINISH command and command limits."""
    
    # Create test workspace
    workspace_path = "/home/eduardo/dev/personal/chapter-agent/workspace"
    
    # Initialize components
    executor = CommandExecutor(workspace_path)
    parser = CommandParser()
    
    print("🧪 Testing FINISH Command & Command Limits")
    print("=" * 50)
    
    # Test 1: Basic FINISH command
    print("1. Testing basic FINISH command...")
    test_response_1 = """<narration>I'll list files and then finish the operation.</narration>
<command>[CMD:LIST_FILES]</command>
<command>[CMD:FINISH]</command>
<o>Successfully listed all files in the workspace.</o>"""
    
    parsed_1 = parser.parse_response(test_response_1)
    print(f"   Parsed commands: {len(parsed_1['commands'])}")
    print(f"   Has FINISH: {parsed_1['has_finish']}")
    print(f"   Final output: {parsed_1['final_output']}")
    
    # Simulate command execution
    task_completed = False
    for i, command in enumerate(parsed_1['commands']):
        print(f"   Executing command {i+1}: {command['type']}")
        
        result = await executor.execute_command(command['type'], command['args'])
        print(f"   Result: {result['success']}")
        
        if command['type'] == 'FINISH':
            task_completed = True
            print(f"   ✅ FINISH command executed - task completion signaled")
            break
    
    print(f"   Task completed: {task_completed}")
    
    # Test 2: FINISH with final output extraction
    print("\n2. Testing FINISH with final output...")
    test_response_2 = """<narration>Creating a summary file and finishing.</narration>
<command>[CMD:WRITE_FILE("summary.txt", "Operation completed successfully")]</command>
<command>[CMD:FINISH]</command>
<o>I have created a summary file with the operation results. The task is now complete.</o>"""
    
    parsed_2 = parser.parse_response(test_response_2)
    print(f"   Commands: {len(parsed_2['commands'])}")
    print(f"   Final output present: {bool(parsed_2['final_output'])}")
    if parsed_2['final_output']:
        print(f"   Final output: {parsed_2['final_output'][:100]}...")
    
    # Test 3: Multiple commands without FINISH (warning case)
    print("\n3. Testing commands without FINISH...")
    test_response_3 = """<narration>I'll do several operations.</narration>
<command>[CMD:LIST_FILES]</command>
<command>[CMD:READ_FILE("test.py")]</command>
<command>[CMD:TERMINAL_COMMAND("echo 'No finish command'")]</command>"""
    
    parsed_3 = parser.parse_response(test_response_3)
    print(f"   Commands without FINISH: {len(parsed_3['commands'])}")
    print(f"   Has FINISH: {parsed_3['has_finish']}")
    print(f"   Warning: Commands executed without proper termination")
    
    # Test 4: Command limit test (simulate 25 commands)
    print("\n4. Testing command limit (max 20)...")
    
    # Generate a response with 25 commands
    many_commands = []
    for i in range(25):
        many_commands.append(f'<command>[CMD:TERMINAL_COMMAND("echo Command {i+1}")]</command>')
    many_commands.append('<command>[CMD:FINISH]</command>')
    
    test_response_4 = f"""<narration>Executing many commands to test limits.</narration>
{''.join(many_commands)}
<o>Completed all operations.</o>"""
    
    parsed_4 = parser.parse_response(test_response_4)
    command_count = len(parsed_4['commands'])
    print(f"   Total commands generated: {command_count}")
    print(f"   Exceeds limit (20): {command_count > 20}")
    print(f"   Expected result: Should be rejected due to command limit")
    
    # Test 5: Proper task completion flow
    print("\n5. Testing proper task completion flow...")
    test_response_5 = """<narration>I'll create a test file, read it back, and finish.</narration>
<command>[CMD:WRITE_FILE("completion_test.txt", "This is a test of task completion")]</command>
<command>[CMD:READ_FILE("completion_test.txt")]</command>
<command>[CMD:TERMINAL_COMMAND("wc -c completion_test.txt")]</command>
<command>[CMD:FINISH]</command>
<o>Successfully created and verified the test file. The file contains the expected content and is 35 characters long.</o>"""
    
    parsed_5 = parser.parse_response(test_response_5)
    print(f"   Commands in proper flow: {len(parsed_5['commands'])}")
    print(f"   Within limit: {len(parsed_5['commands']) <= 20}")
    print(f"   Has FINISH: {parsed_5['has_finish']}")
    print(f"   Has final output: {bool(parsed_5['final_output'])}")
    
    # Execute this proper flow
    print("   Executing proper completion flow...")
    task_completed = False
    for i, command in enumerate(parsed_5['commands']):
        result = await executor.execute_command(command['type'], command['args'])
        if command['type'] == 'FINISH':
            task_completed = True
            break
    
    print(f"   ✅ Proper flow completed: {task_completed}")
    
    print("\n✅ FINISH command and limit tests completed!")

if __name__ == "__main__":
    asyncio.run(test_finish_command())
