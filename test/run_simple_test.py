#!/usr/bin/env python3
"""
Simple test runner that works with WSL/Windows Blender
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
BLENDER_PATH = "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe"

# Convert to Windows paths
project_root_win = str(PROJECT_ROOT).replace("/mnt/c", "C:").replace("/", "\\")
test_script_win = f"{project_root_win}\\test\\test_workspace_simple.py"

# Create command
cmd = [
    BLENDER_PATH,
    "--background",
    "--factory-startup",
    "--python", test_script_win
]

print(f"Running workspace test...")
print(f"Script: {test_script_win}")
print("=" * 60)

# Run test
result = subprocess.run(cmd, capture_output=False, text=True)

print("=" * 60)
if result.returncode == 0:
    print("✓ Test passed")
else:
    print(f"✗ Test failed with code {result.returncode}")

sys.exit(result.returncode)