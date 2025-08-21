#!/usr/bin/env python3
"""
Test Wrapper for MIDI Pose Cycler
Run Blender tests without typing the full path

Usage:
    python test_wrapper.py test_name
    python test_wrapper.py test_generate_nodes
    python test_wrapper.py all
"""

import subprocess
import sys
import os
from pathlib import Path

# Blender executable path
BLENDER_PATH = "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe"

# Test directory
TEST_DIR = Path(__file__).parent


def run_test(test_name):
    """Run a single test file"""
    if not test_name.endswith('.py'):
        test_name = f"{test_name}.py"
    
    test_file = TEST_DIR / test_name
    
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")
    
    # Convert WSL path to Windows path for Blender
    windows_path = str(test_file).replace('/mnt/c/', 'C:\\').replace('/', '\\')
    
    cmd = [
        BLENDER_PATH,
        "--background",
        "--factory-startup",
        "--python", windows_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error running test: {e}")
        return False


def list_tests():
    """List all available test files"""
    tests = sorted([f.name for f in TEST_DIR.glob("test_*.py") if f.name != "test_wrapper.py"])
    return tests


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable tests:")
        for test in list_tests():
            print(f"  - {test[:-3]}")  # Remove .py extension
        sys.exit(1)
    
    test_arg = sys.argv[1]
    
    if test_arg == "all":
        # Run all tests
        tests = list_tests()
        print(f"Running {len(tests)} tests...")
        
        failed = []
        for test in tests:
            if not run_test(test):
                failed.append(test)
        
        print(f"\n{'='*60}")
        if failed:
            print(f"✗ {len(failed)} tests failed:")
            for test in failed:
                print(f"  - {test}")
            sys.exit(1)
        else:
            print(f"✓ All {len(tests)} tests passed!")
            sys.exit(0)
    
    else:
        # Run single test
        success = run_test(test_arg)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()