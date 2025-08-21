"""Test mpc.generate_node_workspace command"""

import bpy
import sys


def main():
    print("\n" + "="*60)
    print("Testing mpc.generate_node_workspace command")
    print("="*60)
    
    # Clear all workspaces except current
    print("Starting with blank file...")
    bpy.ops.wm.read_homefile(use_empty=True)
    print("✓ Loaded blank Blender file")
    
    # Register addon
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    
    # Import all modules needed
    import workspace_node_based
    import node_tree
    import node_operators
    
    # Register components
    try:
        node_tree.register()
        print("✓ Node tree registered")
    except Exception as e:
        print(f"✗ Failed to register node tree: {e}")
        return False
    
    try:
        node_operators.register()
        print("✓ Node operators registered")
    except Exception as e:
        print(f"✗ Failed to register node operators: {e}")
        return False
    
    try:
        workspace_node_based.register()
        print("✓ Workspace operator registered")
    except Exception as e:
        print(f"✗ Failed to register workspace operator: {e}")
        return False
    
    # Check operator exists
    if hasattr(bpy.ops.mpc, 'generate_node_workspace'):
        print("✓ Operator 'mpc.generate_node_workspace' found in F3 menu")
    else:
        print("✗ Operator 'mpc.generate_node_workspace' NOT found")
        # List what IS available
        if hasattr(bpy.ops, 'mpc'):
            mpc_ops = dir(bpy.ops.mpc)
            print(f"  Available mpc operators: {mpc_ops}")
        else:
            print("  No 'mpc' namespace found")
        
        if hasattr(bpy.ops, 'midipose'):
            midi_ops = [op for op in dir(bpy.ops.midipose) if not op.startswith('_')]
            print(f"  Available midipose operators: {midi_ops}")
        return False
    
    # Test workspace creation
    print("\nTesting workspace creation...")
    try:
        result = bpy.ops.mpc.generate_node_workspace()
        if result == {'FINISHED'}:
            print("✓ First workspace created successfully")
        else:
            print(f"✗ Unexpected result: {result}")
            return False
    except Exception as e:
        print(f"✗ Error creating workspace: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check workspace exists
    midi_workspaces = [ws.name for ws in bpy.data.workspaces if ws.name.startswith("Midi")]
    if midi_workspaces:
        print(f"✓ Found workspace: {midi_workspaces[0]}")
    else:
        print("✗ No Midi workspace found")
        print(f"  Available workspaces: {[ws.name for ws in bpy.data.workspaces]}")
        return False
    
    # Test multiple creations
    print("\nTesting multiple workspace creation...")
    for i in range(3):
        try:
            result = bpy.ops.mpc.generate_node_workspace()
            if result != {'FINISHED'}:
                print(f"✗ Failed on iteration {i+2}: {result}")
                return False
        except Exception as e:
            print(f"✗ Error on iteration {i+2}: {e}")
            return False
    
    midi_workspaces = sorted([ws.name for ws in bpy.data.workspaces if ws.name.startswith("Midi")])
    print(f"✓ Created {len(midi_workspaces)} workspaces: {', '.join(midi_workspaces)}")
    
    # Check workspace has correct areas
    workspace = bpy.data.workspaces[midi_workspaces[0]]
    screen = workspace.screens[0] if workspace.screens else None
    if screen:
        area_types = {}
        for area in screen.areas:
            area_types[area.type] = area_types.get(area.type, 0) + 1
        
        print(f"\nWorkspace '{midi_workspaces[0]}' areas:")
        for atype, count in sorted(area_types.items()):
            print(f"  {atype}: {count}")
        
        if 'NODE_EDITOR' in area_types:
            print("✓ Node editor present")
        else:
            print("✗ No node editor found")
            return False
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)