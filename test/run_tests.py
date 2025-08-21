#!/usr/bin/env python3
"""
Test runner for MIDI Pose Cycler Blender addon
Runs tests in Blender's Python environment

Usage:
    python test/run_tests.py [test_name]
    
Examples:
    python test/run_tests.py              # Run all tests
    python test/run_tests.py workspace    # Run workspace tests
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Get paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SRC_DIR = PROJECT_ROOT / "src"
TEST_DIR = PROJECT_ROOT / "test"
BLENDER_PATH = "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe"

def create_test_script(test_module=None):
    """Create a Python script to run in Blender"""
    
    if test_module:
        test_imports = f"from test_{test_module} import main"
        test_run = "main()"
    else:
        # Run all tests
        test_imports = """
import test_workspace
import test_addon_load
import test_midi_load
"""
        test_run = """
print("\\nRunning all tests...\\n")
results = []

# Test addon loading
print("Testing addon load...")
try:
    import test_addon_load
    results.append(('Addon Load', test_addon_load.main()))
except Exception as e:
    print(f"Failed to run addon load test: {e}")
    results.append(('Addon Load', False))

# Test workspace
print("\\nTesting workspace...")
try:
    import test_workspace
    results.append(('Workspace', test_workspace.main()))
except Exception as e:
    print(f"Failed to run workspace test: {e}")
    results.append(('Workspace', False))

# Test MIDI loading
print("\\nTesting MIDI file loading...")
try:
    import test_midi_load
    results.append(('MIDI Load', test_midi_load.main()))
except Exception as e:
    print(f"Failed to run MIDI load test: {e}")
    results.append(('MIDI Load', False))

# Summary
print("\\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
all_passed = True
for name, result in results:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"{name}: {status}")
    if not result:
        all_passed = False

sys.exit(0 if all_passed else 1)
"""
    
    # Convert paths to Windows format for Blender
    src_dir_win = str(SRC_DIR).replace("/mnt/c", "C:").replace("/", "\\\\")
    test_dir_win = str(TEST_DIR).replace("/mnt/c", "C:").replace("/", "\\\\")
    project_root_win = str(PROJECT_ROOT).replace("/mnt/c", "C:").replace("/", "\\\\")
    
    return f"""
import sys
import os

# Add paths for imports
sys.path.insert(0, r"{src_dir_win}")
sys.path.insert(0, r"{test_dir_win}")
sys.path.insert(0, r"{project_root_win}")

print("Python paths:")
for p in sys.path[:3]:
    print(f"  {{p}}")

# Install the addon
print("\\nInstalling MIDI Pose Cycler addon...")
import bpy

# Remove existing addon if present
addon_name = "midi-pose-cycler"
if addon_name in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_disable(module=addon_name)
    bpy.ops.preferences.addon_remove(module=addon_name)

# Add src directory to addon paths
if str(r"{project_root_win}") not in bpy.utils.script_paths():
    bpy.utils.script_path_user = str(r"{project_root_win}")

# Enable the addon from src/
try:
    # Change to src directory so relative imports work
    import os
    os.chdir(r"{src_dir_win}")
    
    # Add all the submodules to sys.modules first
    sys.modules['midi_core'] = __import__('midi_core')
    sys.modules['animation_renderer'] = __import__('animation_renderer')
    sys.modules['config_manager'] = __import__('config_manager')
    sys.modules['ui_operators'] = __import__('ui_operators')
    sys.modules['workspace_creator'] = __import__('workspace_creator')
    sys.modules['ui_properties_panels'] = __import__('ui_properties_panels')
    
    # Now load the main module
    exec(open(r"{src_dir_win}\\__init__.py").read().replace("from . import", "import"))
    
    # Get the register function from globals
    register = globals().get('register')
    if register:
        register()
        print("✓ Addon registered successfully")
    else:
        print("✗ No register function found")
        sys.exit(1)
except Exception as e:
    print(f"✗ Failed to register addon: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Run tests
{test_imports}
{test_run}
"""

def run_test(test_module=None):
    """Run test in Blender"""
    
    # Create temporary test script
    test_script = create_test_script(test_module)
    
    # Create temp file in Windows-accessible location
    temp_dir = Path("/mnt/c/Users/words/OneDrive/Desktop/code/midi-pose-cycler/tmp")
    temp_dir.mkdir(exist_ok=True)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=str(temp_dir)) as f:
        f.write(test_script)
        script_path = f.name
        # Convert WSL path to Windows path for Blender
        windows_path = script_path.replace("/mnt/c", "C:").replace("/", "\\\\")
    
    try:
        # Build Blender command
        cmd = [
            BLENDER_PATH,
            "--background",  # No UI
            "--factory-startup",  # Clean state
            "--python", windows_path
        ]
        
        print(f"Running: {' '.join(cmd)}")
        print("=" * 60)
        
        # Run Blender with test script
        result = subprocess.run(
            cmd,
            capture_output=False,  # Show output directly
            text=True
        )
        
        return result.returncode
        
    finally:
        # Clean up temp file
        try:
            os.unlink(script_path)
        except:
            pass

def main():
    """Main test runner"""
    
    # Check if Blender exists (WSL path)
    if not os.path.exists(BLENDER_PATH):
        print(f"ERROR: Blender not found at {BLENDER_PATH}")
        print("Please update BLENDER_PATH in run_tests.py")
        sys.exit(1)
    
    # Get test module from args
    test_module = None
    if len(sys.argv) > 1:
        test_module = sys.argv[1].replace("test_", "").replace(".py", "")
        print(f"Running test module: {test_module}")
    else:
        print("Running all tests")
    
    # Run tests
    exit_code = run_test(test_module)
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("✓ Tests completed successfully")
    else:
        print(f"✗ Tests failed with exit code {exit_code}")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()