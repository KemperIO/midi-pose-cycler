#!/usr/bin/env python3
"""
Test minimal workspace creator
"""

import bpy
import sys
from pathlib import Path

print("Minimal test starting...")

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    print("Importing workspace_creator_minimal...")
    import workspace_creator_minimal
    print("✓ Imported")
    
    print("Registering...")
    workspace_creator_minimal.register()
    print("✓ Registered")
    
    print("Creating workspace...")
    bpy.ops.midipose.create_workspace()
    print("✓ Created")
    
    # Check result
    if "MIDI Pose Cycler" in bpy.data.workspaces:
        print("✓ Workspace exists!")
    else:
        print("✗ Workspace not found")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete")