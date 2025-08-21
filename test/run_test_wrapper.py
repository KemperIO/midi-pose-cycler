#!/usr/bin/env python3
"""
Test wrapper for running Blender tests properly
ALWAYS use this wrapper instead of calling Blender directly!

Usage:
    python test/run_test_wrapper.py test_name
    python test/run_test_wrapper.py test_no_errors
    python test/run_test_wrapper.py test_midi_simple
"""

import subprocess
import sys
import os
from pathlib import Path

# Blender executable path
BLENDER_PATH = "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe"

def run_blender_test(test_name):
    """Run a test in Blender using proper wrapper pattern"""
    
    # Get test file path
    test_dir = Path(__file__).parent.absolute()
    test_file = test_dir / f"{test_name}.py"
    
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return 1
    
    # Convert to Windows path for Blender
    test_file_windows = str(test_file).replace('/mnt/c', 'C:').replace('/', '\\')
    
    # Build command
    cmd = [
        BLENDER_PATH,
        "--background",
        "--factory-startup", 
        "--python", test_file_windows
    ]
    
    print(f"Running test: {test_name}")
    print("=" * 60)
    
    try:
        # Run the test
        result = subprocess.run(
            cmd,
            capture_output=False,  # Show output directly
            text=True,
            check=False
        )
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print(f"✓ Test {test_name} passed")
        else:
            print(f"✗ Test {test_name} failed with code {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"✗ Error running test: {e}")
        return 1

def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python test/run_test_wrapper.py test_name")
        print("\nAvailable tests:")
        print("  - test_no_errors    : Check for console errors")
        print("  - test_midi_simple  : Test MIDI file loading")
        print("  - test_addon_load   : Test addon registration")
        print("  - test_workspace    : Test workspace creation")
        return 1
    
    test_name = sys.argv[1]
    
    # Remove .py extension if provided
    if test_name.endswith('.py'):
        test_name = test_name[:-3]
    
    # Add test_ prefix if not provided
    if not test_name.startswith('test_'):
        test_name = f"test_{test_name}"
    
    return run_blender_test(test_name)

if __name__ == "__main__":
    sys.exit(main())