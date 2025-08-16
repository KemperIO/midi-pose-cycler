#!/usr/bin/env python3
"""
Basic test - just imports and registers workspace creator
"""

import bpy
import sys

print("Basic test starting...")
print(f"Blender version: {bpy.app.version_string}")
print(f"Python version: {sys.version}")

# Test basic workspace operations
print("\nTesting workspace operations...")

# Duplicate workspace
try:
    bpy.ops.workspace.duplicate()
    print("✓ Can duplicate workspace")
except Exception as e:
    print(f"✗ Cannot duplicate workspace: {e}")

# Create a test workspace
try:
    ws = bpy.context.window.workspace
    ws.name = "Test Workspace"
    print(f"✓ Created workspace: {ws.name}")
    
    # Get screen
    screen = ws.screens[0]
    print(f"✓ Got screen with {len(screen.areas)} areas")
    
    # Try to split an area
    if screen.areas:
        area = screen.areas[0]
        print(f"  First area type: {area.type}")
        
        # Try override
        override = {'window': bpy.context.window, 'screen': screen, 'area': area}
        with bpy.context.temp_override(**override):
            bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
            print("✓ Split area successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nBasic test complete")