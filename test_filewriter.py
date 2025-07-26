"""Test script to verify FileWriter improvements."""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_filewriter():
    """Test the FileWriter with problematic content."""
    try:
        from tools.file_writer import FileWriter
        from tools.path_resolver import PathResolver
        
        print("Testing FileWriter improvements...")
        
        workspace = "./workspace"
        writer = FileWriter(workspace)
        
        # Test case 1: Content with escaped quotes (common AI generation issue)
        test_content_1 = '''def greet():
    return \"Hello World!\"

if __name__ == \"__main__\":
    print(\"Testing quotes\")'''
        
        print("\n1. Testing escaped quotes content...")
        result1 = await writer.write_file("test_quotes.py", test_content_1)
        print(f"   Result: {result1['success']}")
        
        # Check the actual file content
        if result1['success']:
            with open(os.path.join(workspace, "test_quotes.py"), 'r') as f:
                actual_content = f.read()
                print("   Actual content:")
                for i, line in enumerate(actual_content.split('\n'), 1):
                    print(f"   {i:2}: {repr(line)}")
        
        # Test case 2: Mixed content with some proper quotes
        test_content_2 = '''def example():
    good_string = "This is fine"
    bad_string = \"This needs fixing\"
    return good_string'''
        
        print("\n2. Testing mixed quote content...")
        result2 = await writer.write_file("test_mixed.py", test_content_2)
        print(f"   Result: {result2['success']}")
        
        if result2['success']:
            with open(os.path.join(workspace, "test_mixed.py"), 'r') as f:
                actual_content = f.read()
                print("   Actual content:")
                for i, line in enumerate(actual_content.split('\n'), 1):
                    print(f"   {i:2}: {repr(line)}")
        
        print("\n✅ FileWriter test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_filewriter())
