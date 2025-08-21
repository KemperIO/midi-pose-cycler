"""
Test MIDI file loading functionality
Tests that the eight-bars-thang.mid file loads correctly with tracks
"""

import bpy
import os
import sys

def main():
    """Test loading MIDI file and verifying tracks"""
    print("\n" + "="*60)
    print("Testing MIDI File Loading")
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
    
    # Set the MIDI file path directly (simulating the load operator)
    props.midi_file = midi_file
    
    # Try to analyze the MIDI file using midi_core
    try:
        # Import midi_core module - add src to path first
        src_dir = os.path.join(project_dir, "src")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        import midi_core
        
        # Check if mido is available
        if not midi_core.MIDO_AVAILABLE:
            print("✗ mido library not available")
            return False
        
        print("✓ mido library loaded successfully")
        
        # Analyze the MIDI file
        analysis = midi_core.analyze_midi_file(midi_file)
        
        if analysis is None:
            print("✗ Failed to analyze MIDI file")
            return False
        
        print(f"✓ MIDI file analyzed successfully")
        print(f"  - Ticks per beat: {analysis.ticks_per_beat}")
        print(f"  - BPM: {analysis.bpm}")
        print(f"  - Number of tracks: {len(analysis.tracks)}")
        
        # Check that we have at least one track
        if len(analysis.tracks) == 0:
            print("✗ No tracks found in MIDI file")
            return False
        
        print(f"✓ Found {len(analysis.tracks)} track(s)")
        
        # List track details
        for track in analysis.tracks:
            print(f"\n  Track {track.index}: {track.name}")
            print(f"    - Note count: {track.note_count}")
            print(f"    - Unique notes: {len(track.notes)}")
            print(f"    - Channels: {track.channels}")
            
            # Show first few notes
            if track.notes:
                note_list = list(track.notes.items())[:5]
                for note_num, count in note_list:
                    note_name = midi_core.midi_note_to_name(note_num)
                    print(f"      {note_name} (MIDI {note_num}): {count} occurrences")
                if len(track.notes) > 5:
                    print(f"      ... and {len(track.notes) - 5} more notes")
        
        # Now test the operator
        print("\n" + "-"*40)
        print("Testing Load MIDI Operator")
        print("-"*40)
        
        # Clear the file first to test the operator
        props.midi_file = ""
        props.track_items.clear()
        
        # Call the load operator
        try:
            result = bpy.ops.midipose.load_midi(filepath=midi_file)
            if 'FINISHED' in result:
                print("✓ Load MIDI operator executed successfully")
            else:
                print(f"✗ Load MIDI operator returned: {result}")
                return False
        except Exception as e:
            print(f"✗ Failed to execute load operator: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Verify the file was loaded
        if props.midi_file != midi_file:
            print(f"✗ MIDI file path not set correctly")
            print(f"  Expected: {midi_file}")
            print(f"  Got: {props.midi_file}")
            return False
        
        print("✓ MIDI file path set correctly")
        
        # Check that tracks were populated
        if len(props.track_items) == 0:
            print("✗ No tracks populated in UI")
            return False
        
        print(f"✓ {len(props.track_items)} track(s) populated in UI")
        
        # List UI tracks
        for track in props.track_items:
            print(f"  - {track.name}: {track.note_count} notes")
        
        print("\n" + "="*60)
        print("✓ All MIDI loading tests passed!")
        print("="*60)
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import midi_core: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)