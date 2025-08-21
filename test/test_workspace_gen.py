"""Test workspace generation without crashes"""

import bpy
import sys


def main():
    print("\nTesting workspace generation...")
    
    # Register components
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    
    import workspace_node_based
    import node_tree
    import node_operators
    
    # Register
    try:
        node_tree.register()
        node_operators.register()
        workspace_node_based.register()
        print("✓ Components registered")
    except Exception as e:
        print(f"✗ Registration failed: {e}")
        return False
    
    # Test workspace generation
    try:
        result = bpy.ops.mpc.generate_node_workspace()
        if result == {'FINISHED'}:
            print("✓ Workspace created successfully")
        else:
            print(f"✗ Unexpected result: {result}")
            return False
    except Exception as e:
        print(f"✗ Workspace creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check workspace exists
    workspaces = [ws.name for ws in bpy.data.workspaces if ws.name.startswith("Midi")]
    if workspaces:
        print(f"✓ Found workspace: {workspaces[0]}")
        
        # Check areas
        ws = bpy.data.workspaces[workspaces[0]]
        if ws.screens:
            screen = ws.screens[0]
            area_types = {}
            for area in screen.areas:
                area_types[area.type] = area_types.get(area.type, 0) + 1
            
            print("Area types:")
            for atype, count in sorted(area_types.items()):
                print(f"  {atype}: {count}")
            
            if 'NODE_EDITOR' in area_types:
                print("✓ Node editor present")
            else:
                print("✗ No node editor")
                return False
    else:
        print("✗ No workspace found")
        return False
    
    print("✓ Test passed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)