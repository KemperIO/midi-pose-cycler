"""Test panel UI without crashes"""

import bpy
import sys


def main():
    print("\n" + "="*60)
    print("Testing Panel UI")
    print("="*60)
    
    # Register addon components
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    
    try:
        # Import the __init__ file which handles registration
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "midi_pose_cycler",
            "C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src\\__init__.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules['midi_pose_cycler'] = module
        spec.loader.exec_module(module)
        
        # Now register
        module.register()
        
        print("✓ Addon registered")
    except Exception as e:
        print(f"✗ Failed to register: {e}")
        return False
    
    # Check panels exist
    panel_ids = [
        'MIDIPOSE_PT_properties_main',
        'MIDIPOSE_PT_properties_poses', 
        'MIDIPOSE_PT_properties_midi'
    ]
    
    for panel_id in panel_ids:
        if hasattr(bpy.types, panel_id):
            print(f"✓ Found panel: {panel_id}")
        else:
            print(f"✗ Missing panel: {panel_id}")
            return False
    
    # Test accessing properties
    try:
        props = bpy.context.scene.midi_pose_props
        
        # Test setting values
        props.action_name = "TestAction"
        props.bpm = 140.0
        props.frames_to_hold = 5
        
        print(f"✓ Properties accessible")
        print(f"  Action: {props.action_name}")
        print(f"  BPM: {props.bpm}")
        print(f"  Frames: {props.frames_to_hold}")
    except Exception as e:
        print(f"✗ Failed to access properties: {e}")
        return False
    
    # Test operators exist
    operators = [
        'midipose.load_midi',
        'midipose.select_track',
        'midipose.refresh_poses',
        'midipose.render_animation'
    ]
    
    for op_id in operators:
        if hasattr(bpy.ops.midipose, op_id.split('.')[1]):
            print(f"✓ Found operator: {op_id}")
        else:
            print(f"✗ Missing operator: {op_id}")
            return False
    
    print("\n" + "="*60)
    print("✓ All panel tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)