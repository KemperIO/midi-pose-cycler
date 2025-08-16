#!/usr/bin/env python3
"""
Test importing workspace creator module
"""

import bpy
import sys
from pathlib import Path

print("Import test starting...")

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
print(f"Added to path: {src_dir}")

# Try importing workspace_creator
try:
    print("\nImporting workspace_creator...")
    import workspace_creator
    print("✓ Successfully imported workspace_creator")
    
    # Check what's in it
    print("\nModule contents:")
    for item in dir(workspace_creator):
        if not item.startswith('_'):
            print(f"  - {item}")
    
    # Try to register
    print("\nRegistering classes...")
    workspace_creator.register()
    print("✓ Successfully registered")
    
    # Check if operator exists
    if hasattr(bpy.ops.midipose, 'create_workspace'):
        print("✓ Operator midipose.create_workspace exists")
        
        # Try to run it
        print("\nAttempting to create workspace...")
        result = bpy.ops.midipose.create_workspace()
        print(f"Result: {result}")
    else:
        print("✗ Operator not found")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nImport test complete")