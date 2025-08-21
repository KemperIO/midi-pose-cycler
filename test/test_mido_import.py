"""Test mido import"""
import sys
import os

# Add parent directory to path to find src
test_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(test_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

# Try to import midi_core which will test mido import
try:
    import midi_core
    print(f"✓ midi_core imported successfully")
    print(f"  MIDO_AVAILABLE: {midi_core.MIDO_AVAILABLE}")
    print(f"  mido module: {midi_core.mido}")
except Exception as e:
    print(f"✗ Failed to import midi_core: {e}")
    import traceback
    traceback.print_exc()