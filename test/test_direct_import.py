#!/usr/bin/env python3
"""Test importing workspace_creator directly without __init__"""

import bpy
import sys
from pathlib import Path

print("Direct import test...")

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# First check what's in the file
import os
ws_path = os.path.join(src_dir, "workspace_creator.py")
print(f"File exists: {os.path.exists(ws_path)}")
print(f"File size: {os.path.getsize(ws_path)} bytes")

try:
    print("\nImporting workspace_creator directly...")
    import workspace_creator
    print("✓ Imported successfully!")
    
    # Try to use it
    print("\nRegistering...")
    workspace_creator.register()
    print("✓ Registered")
    
    print("\nCreating workspace...")
    bpy.ops.midipose.create_workspace()
    
    # Check result
    if "MIDI Pose Cycler" in bpy.data.workspaces:
        ws = bpy.data.workspaces["MIDI Pose Cycler"]
        screen = ws.screens[0]
        print(f"✓ Workspace created with {len(screen.areas)} areas")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDirect import test complete")