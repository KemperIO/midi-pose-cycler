#!/usr/bin/env python3
"""Test fixed workspace creator"""

import bpy
import sys
from pathlib import Path

print("Testing fixed workspace creator...")

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    import workspace_creator_fixed
    workspace_creator_fixed.register()
    print("✓ Registered")
    
    # Create workspace
    bpy.ops.midipose.create_workspace()
    
    # Check result
    if "MIDI Pose Cycler" in bpy.data.workspaces:
        print("✓ Workspace created!")
        
        # Check area count
        ws = bpy.data.workspaces["MIDI Pose Cycler"]
        screen = ws.screens[0]
        print(f"Total areas: {len(screen.areas)}")
        
        # Count types
        counts = {}
        for area in screen.areas:
            counts[area.type] = counts.get(area.type, 0) + 1
        
        # Check if we got all 8
        expected_total = 8
        if len(screen.areas) == expected_total:
            print(f"✓ Got all {expected_total} areas!")
        else:
            print(f"✗ Expected {expected_total} areas, got {len(screen.areas)}")
    else:
        print("✗ Workspace not created")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete")