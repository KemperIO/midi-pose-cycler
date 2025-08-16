"""
Test addon loading for MIDI Pose Cycler
"""

import bpy
import sys

def test_addon_registration():
    """Test that addon registers correctly"""
    print("=" * 60)
    print("TEST: Addon Registration")
    print("=" * 60)
    
    try:
        # Check if our properties are registered
        print("1. Checking Scene properties...")
        if hasattr(bpy.types.Scene, "midi_pose_props"):
            print("   ✓ midi_pose_props registered")
        else:
            print("   ✗ midi_pose_props not found")
            return False
        
        # Check operators
        print("\n2. Checking operators...")
        operators = [
            "midipose.load_midi",
            "midipose.render_animation",
            "midipose.refresh_poses",
            "midipose.create_workspace",
            "midipose.move_pose",
        ]
        
        all_found = True
        for op_id in operators:
            try:
                # Try to get operator info
                op_class = eval(f"bpy.ops.{op_id.replace('.', '.')}")
                print(f"   ✓ {op_id}")
            except:
                print(f"   ✗ {op_id} not found")
                all_found = False
        
        # Check panels
        print("\n3. Checking panels...")
        panels = [
            "MIDIPOSE_PT_properties_main",
            "MIDIPOSE_PT_properties_poses",
            "MIDIPOSE_PT_properties_midi",
        ]
        
        for panel_name in panels:
            if hasattr(bpy.types, panel_name):
                print(f"   ✓ {panel_name}")
            else:
                print(f"   ✗ {panel_name} not found")
                all_found = False
        
        # Check menu entries
        print("\n4. Checking menu entries...")
        # This is harder to test directly, just note it
        print("   ! Menu entries cannot be easily tested in background mode")
        
        return all_found
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run addon loading tests"""
    print("\nMIDI Pose Cycler - Addon Load Tests")
    print("=" * 60)
    
    success = test_addon_registration()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ADDON LOAD TEST PASSED")
        return True
    else:
        print("✗ ADDON LOAD TEST FAILED")
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)