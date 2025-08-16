#!/usr/bin/env python3
"""Run basic test"""
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
BLENDER_PATH = "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe"

test_script_win = str(PROJECT_ROOT).replace("/mnt/c", "C:").replace("/", "\\") + "\\test\\test_basic.py"

cmd = [BLENDER_PATH, "--background", "--factory-startup", "--python", test_script_win]

print(f"Running: {test_script_win}")
print("=" * 60)
result = subprocess.run(cmd, capture_output=False, text=True)
print("=" * 60)
print(f"Exit code: {result.returncode}")