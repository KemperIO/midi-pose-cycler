#!/usr/bin/env python3
"""
Simple workspace test for MIDI Pose Cycler
Tests just the workspace creation
"""

import bpy
import sys
from pathlib import Path

def main():
    """Test workspace creation"""
    print("\n" + "="*60)
    print("WORKSPACE CREATION TEST")
    print("="*60)
    
    # Add src to path
    src_dir = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_dir))
    
    # Import workspace creator directly
    try:
        import workspace_creator
        workspace_creator.register()
        print("✓ Workspace creator registered")
    except Exception as e:
        print(f"✗ Failed to register workspace creator: {e}")
        return False
    
    # Try to create workspace
    try:
        print("\nCreating workspace...")
        bpy.ops.midipose.create_workspace()
        print("✓ Workspace created")
    except Exception as e:
        print(f"✗ Failed to create workspace: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Validate workspace
    workspace_name = "MIDI Pose Cycler"
    if workspace_name not in bpy.data.workspaces:
        print(f"✗ Workspace '{workspace_name}' not found")
        return False
    
    workspace = bpy.data.workspaces[workspace_name]
    screen = workspace.screens[0] if workspace.screens else None
    
    if not screen:
        print("✗ No screen in workspace")
        return False
    
    # Count area types
    area_counts = {}
    for area in screen.areas:
        area_counts[area.type] = area_counts.get(area.type, 0) + 1
    
    print(f"\nFound {len(screen.areas)} areas:")
    for atype, count in sorted(area_counts.items()):
        print(f"  {atype}: {count}")
    
    # Check expected counts
    expected = {
        'FILE_BROWSER': 1,
        'ASSETS': 1,
        'VIEW_3D': 1,
        'DOPESHEET_EDITOR': 1,
        'SEQUENCE_EDITOR': 1,
        'PROPERTIES': 3
    }
    
    print("\nValidation:")
    all_good = True
    for etype, ecount in expected.items():
        actual = area_counts.get(etype, 0)
        if actual == ecount:
            print(f"  ✓ {etype}: {actual}/{ecount}")
        else:
            print(f"  ✗ {etype}: {actual}/{ecount}")
            all_good = False
    
    if all_good:
        print("\n✓ ALL TESTS PASSED")
        return True
    else:
        print("\n✗ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)