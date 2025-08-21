"""Test addon loads without console errors"""

import bpy
import sys
import io
from contextlib import redirect_stdout, redirect_stderr


def main():
    print("\n" + "="*60)
    print("Testing Addon Registration (No Errors)")
    print("="*60)
    
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Register addon with output capture
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        try:
            # Import and register the addon
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
            
        except Exception as e:
            print(f"✗ Failed to register addon: {e}")
            return False
    
    # Check captured output for errors
    stdout_text = stdout_capture.getvalue()
    stderr_text = stderr_capture.getvalue()
    
    errors_found = []
    
    # Check for common error patterns
    error_patterns = [
        "ERROR:",
        "Error:",
        "EXCEPTION",
        "Exception:",
        "Failed",
        "failed",
        "Traceback",
        "not found",
        "undefined",
        "missing"
    ]
    
    for pattern in error_patterns:
        if pattern in stdout_text:
            errors_found.append(f"Found '{pattern}' in stdout")
        if pattern in stderr_text:
            errors_found.append(f"Found '{pattern}' in stderr")
    
    # Report results
    if errors_found:
        print("✗ Errors found during registration:")
        for error in errors_found[:5]:  # Limit to first 5
            print(f"  - {error}")
        print("\nStdout output:")
        print(stdout_text[:500])  # First 500 chars
        if stderr_text:
            print("\nStderr output:")
            print(stderr_text[:500])
        return False
    
    print("✓ Addon registered without errors")
    
    # Verify panels are registered (new 3-tab structure)
    panel_ids = [
        # MPC-Run tab panels
        'MIDIPOSE_PT_run_main',
        'MIDIPOSE_PT_run_output',
        'MIDIPOSE_PT_run_timing',
        'MIDIPOSE_PT_run_input',
        'MIDIPOSE_PT_run_config',
        # MPC-Pose tab panels
        'MIDIPOSE_PT_pose_selection',
        'MIDIPOSE_PT_pose_cycle',
        'MIDIPOSE_PT_pose_order',
        # MPC-MIDI tab panels
        'MIDIPOSE_PT_midi_file',
        'MIDIPOSE_PT_midi_tracks'
    ]
    
    for panel_id in panel_ids:
        if hasattr(bpy.types, panel_id):
            print(f"✓ Panel registered: {panel_id}")
        else:
            print(f"✗ Panel missing: {panel_id}")
            return False
    
    # Verify properties
    if hasattr(bpy.types.Scene, 'midi_pose_props'):
        print("✓ Properties registered")
    else:
        print("✗ Properties not registered")
        return False
    
    # Verify key operators
    operators = [
        ('midipose', 'load_midi'),
        ('midipose', 'render_animation'),
        ('midipose', 'refresh_poses'),
    ]
    
    for module, op in operators:
        if hasattr(getattr(bpy.ops, module, None), op):
            print(f"✓ Operator registered: {module}.{op}")
        else:
            print(f"✗ Operator missing: {module}.{op}")
            return False
    
    print("\n" + "="*60)
    print("✓ All tests passed - No errors!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)