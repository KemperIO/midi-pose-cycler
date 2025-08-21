"""Simple test to load addon and check for errors"""

import bpy
import sys

def main():
    print("\n" + "="*60)
    print("Simple Addon Load Test")
    print("="*60)
    
    try:
        # Import and register the addon
        sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
        
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "midi_pose_cycler",
            "C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src\\__init__.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules['midi_pose_cycler'] = module
        spec.loader.exec_module(module)
        
        # Register
        module.register()
        print("✓ Addon registered successfully")
        
    except Exception as e:
        print(f"✗ Failed to register addon: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check if main panel exists
    if hasattr(bpy.types, 'MIDIPOSE_PT_run_main'):
        print("✓ Main panel registered")
    else:
        print("✗ Main panel not found")
        return False
    
    print("\n" + "="*60)
    print("✓ Test passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)