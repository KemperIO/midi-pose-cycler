"""
Test MIDI file loading through the actual operator
This test ensures the LOAD MIDI operator works, not just the core functions
"""

import bpy
import os
import sys

def main():
    """Test the actual MIDI load operator"""
    print("\n" + "="*60)
    print("Testing MIDI Load Operator (Real User Experience)")
    print("="*60)
    
    # Register the addon first
    addon_name = "midi-pose-cycler"
    try:
        bpy.ops.preferences.addon_enable(module=addon_name)
        print(f"✓ Addon '{addon_name}' enabled")
    except Exception as e:
        print(f"✗ Failed to enable addon: {e}")
        return False
    
    # Get the MIDI file path
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(test_dir)
    midi_file = os.path.join(project_dir, "assets", "eight-bars-thang.mid")
    
    if not os.path.exists(midi_file):
        print(f"✗ MIDI file not found: {midi_file}")
        return False
    
    print(f"✓ Found MIDI file: {os.path.basename(midi_file)}")
    
    # Get the properties
    props = bpy.context.scene.midi_pose_props
    
    # Clear any existing data
    props.midi_file = ""
    props.track_items.clear()
    props.selected_track = ""
    
    print("\n--- Testing MIDI Load Operator ---")
    
    # Call the actual operator that users would use
    try:
        result = bpy.ops.midipose.load_midi(filepath=midi_file)
        if 'FINISHED' not in result:
            print(f"✗ Load MIDI operator failed with result: {result}")
            return False
    except Exception as e:
        print(f"✗ Load MIDI operator raised exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✓ Load MIDI operator executed successfully")
    
    # Verify the results
    if props.midi_file != midi_file:
        print(f"✗ MIDI file path not set correctly")
        print(f"  Expected: {midi_file}")
        print(f"  Got: {props.midi_file}")
        return False
    
    print("✓ MIDI file path set correctly")
    
    # Check that tracks were loaded
    if len(props.track_items) == 0:
        print("✗ No tracks loaded! This is the error the user sees!")
        print("  Check console for 'ERROR: mido library not available'")
        return False
    
    print(f"✓ {len(props.track_items)} tracks loaded")
    
    # Verify we have expected tracks
    track_names = [track.name for track in props.track_items]
    expected_tracks = ["kick", "snare", "shaker", "horns"]
    
    for expected in expected_tracks:
        if expected in track_names:
            print(f"  ✓ Found track: {expected}")
        else:
            print(f"  ✗ Missing expected track: {expected}")
            return False
    
    # Test track selection
    print("\n--- Testing Track Selection ---")
    
    try:
        result = bpy.ops.midipose.select_track(track_name="kick")
        if 'FINISHED' not in result:
            print(f"✗ Select track operator failed: {result}")
            return False
    except Exception as e:
        print(f"✗ Select track operator raised exception: {e}")
        return False
    
    if props.selected_track != "kick":
        print(f"✗ Track not selected correctly")
        print(f"  Expected: kick")
        print(f"  Got: {props.selected_track}")
        return False
    
    print("✓ Track 'kick' selected successfully")
    
    # Check that notes were populated
    if len(props.note_items) == 0:
        print("✗ No notes populated for selected track")
        return False
    
    print(f"✓ {len(props.note_items)} note(s) populated")
    
    print("\n" + "="*60)
    print("✓ MIDI operator test PASSED!")
    print("  User can successfully load and use MIDI files")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)