"""Test workspace creation error handling"""

import bpy
import sys


def main():
    print("Testing workspace creation error handling...")
    
    # Register addon
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    import __init__ as addon
    addon.register()
    print("✓ Addon registered")
    
    # Test F3 operator
    if hasattr(bpy.ops.mpc, 'generate_node_workspace'):
        print("✓ F3 operator 'mpc.generate_node_workspace' registered")
        
        # Try to create workspace
        try:
            result = bpy.ops.mpc.generate_node_workspace()
            if result == {'FINISHED'}:
                print("✓ Workspace created successfully")
                
                # Check workspace exists
                workspaces = [ws.name for ws in bpy.data.workspaces if ws.name.startswith("Midi")]
                if workspaces:
                    print(f"✓ Found workspaces: {', '.join(workspaces)}")
                else:
                    print("✗ No Midi workspaces found")
                    return False
            else:
                print(f"✗ Workspace creation returned: {result}")
                return False
        except Exception as e:
            print(f"✗ Error creating workspace: {e}")
            return False
    else:
        print("✗ Operator 'mpc.generate_node_workspace' not found")
        return False
    
    # Test multiple creations
    try:
        for i in range(3):
            result = bpy.ops.mpc.generate_node_workspace()
            if result != {'FINISHED'}:
                print(f"✗ Failed on iteration {i+2}")
                return False
        
        workspaces = [ws.name for ws in bpy.data.workspaces if ws.name.startswith("Midi")]
        print(f"✓ Created {len(workspaces)} workspaces: {', '.join(sorted(workspaces))}")
    except Exception as e:
        print(f"✗ Error in multiple creation: {e}")
        return False
    
    print("✓ All workspace tests passed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)