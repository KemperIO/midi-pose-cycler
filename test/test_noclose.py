#!/usr/bin/env python3
import bpy
import sys
from pathlib import Path

src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

print("Testing workspace_creator_noclose...")
import workspace_creator_noclose
workspace_creator_noclose.register()
print("✓ Registered")

bpy.ops.midipose.create_workspace()

if "MIDI Pose Cycler" in bpy.data.workspaces:
    ws = bpy.data.workspaces["MIDI Pose Cycler"]
    screen = ws.screens[0]
    print(f"✓ Created with {len(screen.areas)} areas")

print("Test complete")