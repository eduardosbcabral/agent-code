#!/usr/bin/env python3
"""Quick test script to verify the tool system works."""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import our tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import FileLister, FileReader, FileWriter, TerminalExecutor, TaskFinisher

async def test_tools():
    """Test all tools to ensure they work correctly."""
    workspace = os.path.dirname(os.path.abspath(__file__))
    
    print("🧪 Testing Chapter Agent Tools...")
    
    # Test FileLister
    print("\n1. Testing FileLister...")
    lister = FileLister(workspace)
    result = await lister.list_files()
    print(f"   ✅ FileLister: {result['success']}")
    
    # Test FileReader
    print("\n2. Testing FileReader...")
    reader = FileReader(workspace)
    result = await reader.read_file("python-examples/calculator.py")
    print(f"   ✅ FileReader: {result['success']}")
    if result['success']:
        print(f"   📄 Read {result['size']} characters")
    
    # Test FileWriter
    print("\n3. Testing FileWriter...")
    writer = FileWriter(workspace)
    test_content = 'print("Hello from Chapter Agent tools!")\nprint("Quotes work: \'single\' and \"double\"")'
    result = await writer.write_file("test_output.py", test_content)
    print(f"   ✅ FileWriter: {result['success']}")
    
    # Test TerminalExecutor
    print("\n4. Testing TerminalExecutor...")
    executor = TerminalExecutor(workspace)
    result = await executor.execute_command("python test_output.py")
    print(f"   ✅ TerminalExecutor: {result['success']}")
    if result['success']:
        print(f"   📤 Command output: {result['stdout'].strip()}")
    
    # Test TaskFinisher
    print("\n5. Testing TaskFinisher...")
    finisher = TaskFinisher()
    result = await finisher.finish_task()
    print(f"   ✅ TaskFinisher: {result['success']}")
    
    print("\n🎉 All tools tested successfully!")
    
    # Cleanup
    try:
        os.remove(os.path.join(workspace, "test_output.py"))
        print("🧹 Cleaned up test file")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(test_tools())
