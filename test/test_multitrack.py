"""
Test multi-track selection functionality
Verifies tracks can be selected and filtered independently
"""

import bpy
import os
import sys

def main():
    """Test multi-track selection and filtering"""
    print("\n" + "="*60)
    print("Testing Multi-Track Selection")
    print("="*60)
    
    # Setup
    addon_name = "midi-pose-cycler"
    try:
        bpy.ops.preferences.addon_enable(module=addon_name)
        print(f"✓ Addon enabled")
    except:
        print(f"✗ Failed to enable addon")
        return False
    
    # Add src to path for imports
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(test_dir)
    src_dir = os.path.join(project_dir, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    props = bpy.context.scene.midi_pose_props
    
    # Load test MIDI file
    midi_file = os.path.join(project_dir, "assets", "eight-bars-thang.mid")
    if not os.path.exists(midi_file):
        print(f"✗ Test MIDI file not found")
        return False
    
    print(f"✓ Found test MIDI: {os.path.basename(midi_file)}")
    
    # Load MIDI
    try:
        result = bpy.ops.midipose.load_midi(filepath=midi_file)
        if 'FINISHED' not in result:
            print(f"✗ Failed to load MIDI")
            return False
    except Exception as e:
        print(f"✗ Error loading MIDI: {e}")
        return False
    
    print(f"✓ MIDI loaded: {len(props.track_items)} tracks")
    
    # Test multi-selection
    print("\n--- Testing Multi-Selection ---")
    
    # Select first 3 tracks
    selected_count = 0
    for i, track in enumerate(props.track_items):
        if i < 3:
            track.selected = True
            selected_count += 1
            print(f"  ✓ Selected: {track.name}")
    
    # Verify selection
    selected_tracks = [t for t in props.track_items if t.selected]
    if len(selected_tracks) != selected_count:
        print(f"✗ Selection failed: expected {selected_count}, got {len(selected_tracks)}")
        return False
    
    print(f"✓ Multi-selection works: {len(selected_tracks)} tracks selected")
    
    # Test per-track note filters
    print("\n--- Testing Per-Track Filters ---")
    
    for track in selected_tracks:
        # Enable filter
        track.filter_notes = True
        
        # Check note filters exist
        if not track.note_filters:
            print(f"✗ No note filters for track: {track.name}")
            return False
        
        print(f"  ✓ Track '{track.name}': {len(track.note_filters)} notes available")
        
        # Test filter operators
        try:
            # Deselect all
            bpy.ops.midipose.deselect_all_track_notes(track_name=track.name)
            selected = sum(1 for n in track.note_filters if n.selected)
            if selected != 0:
                print(f"  ✗ Deselect all failed for {track.name}")
                return False
            
            # Select all
            bpy.ops.midipose.select_all_track_notes(track_name=track.name)
            selected = sum(1 for n in track.note_filters if n.selected)
            if selected != len(track.note_filters):
                print(f"  ✗ Select all failed for {track.name}")
                return False
            
            print(f"  ✓ Note filter operators work for {track.name}")
        except Exception as e:
            print(f"  ✗ Filter operator error: {e}")
            return False
    
    print("\n" + "="*60)
    print("✓ Multi-track selection and filtering works!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)