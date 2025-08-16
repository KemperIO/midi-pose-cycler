"""
Test workspace creation for MIDI Pose Cycler addon
Run with: python test/run_tests.py test_workspace
"""

import bpy
import sys
import traceback

def test_workspace_creation():
    """Test creating the MIDI Pose Cycler workspace"""
    print("=" * 60)
    print("TEST: Workspace Creation")
    print("=" * 60)
    
    try:
        # Start with clean state
        print("1. Starting with default workspace...")
        
        # Check initial state
        initial_workspaces = list(bpy.data.workspaces.keys())
        print(f"   Initial workspaces: {initial_workspaces}")
        
        # Create workspace
        print("\n2. Creating MIDI Pose Cycler workspace...")
        result = bpy.ops.midipose.create_workspace()
        
        if result == {'FINISHED'}:
            print("   ✓ Workspace created successfully")
        else:
            print(f"   ✗ Failed with result: {result}")
            return False
        
        # Verify workspace exists
        print("\n3. Verifying workspace...")
        if "MIDI Pose Cycler" in bpy.data.workspaces:
            print("   ✓ Workspace exists")
            workspace = bpy.data.workspaces["MIDI Pose Cycler"]
            
            # Check screen areas
            screen = workspace.screens[0]
            print(f"\n4. Checking layout...")
            print(f"   Total areas: {len(screen.areas)}")
            
            # Count area types
            area_types = {}
            for area in screen.areas:
                area_type = area.type
                area_types[area_type] = area_types.get(area_type, 0) + 1
            
            print("\n   Area types:")
            for atype, count in sorted(area_types.items()):
                print(f"   - {atype}: {count}")
            
            # Verify expected areas
            expected = {
                'FILE_BROWSER': 1,
                'ASSETS': 1,
                'VIEW_3D': 1,
                'DOPESHEET_EDITOR': 1,
                'SEQUENCE_EDITOR': 1,
                'PROPERTIES': 3  # Should have 3 properties panels
            }
            
            print("\n5. Validating expected layout...")
            all_good = True
            for etype, ecount in expected.items():
                actual = area_types.get(etype, 0)
                if actual >= ecount:  # Allow more but not less
                    print(f"   ✓ {etype}: {actual} (expected {ecount})")
                else:
                    print(f"   ✗ {etype}: {actual} (expected {ecount})")
                    all_good = False
            
            # Check Properties panels are set to SCENE context
            print("\n6. Checking Properties panels...")
            props_count = 0
            scene_count = 0
            for area in screen.areas:
                if area.type == 'PROPERTIES':
                    props_count += 1
                    for space in area.spaces:
                        if space.type == 'PROPERTIES':
                            if space.context == 'SCENE':
                                scene_count += 1
                                print(f"   ✓ Properties panel {props_count} in SCENE context")
                            else:
                                print(f"   ! Properties panel {props_count} in {space.context} context")
            
            # Test switching back
            print("\n7. Testing workspace switching...")
            original_ws = bpy.context.window.workspace.name
            bpy.context.window.workspace = workspace
            if bpy.context.window.workspace.name == "MIDI Pose Cycler":
                print("   ✓ Successfully switched to workspace")
            else:
                print("   ✗ Failed to switch workspace")
                all_good = False
            
            return all_good
        else:
            print("   ✗ Workspace not found in bpy.data.workspaces")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run workspace tests"""
    print("\nMIDI Pose Cycler - Workspace Tests")
    print("=" * 60)
    
    # Test workspace creation
    success = test_workspace_creation()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("✗ TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()