"""Test dynamic track functionality"""
import sys
import os
import bpy

def main():
    print("\n" + "="*60)
    print("Testing Dynamic Track Feature")
    print("="*60)
    
    # Enable addon
    try:
        bpy.ops.preferences.addon_enable(module='midi-pose-cycler')
        print("✓ Addon enabled")
    except:
        print("✗ Failed to enable addon")
        return False
    
    # Get properties
    props = bpy.context.scene.midi_pose_props
    
    # Test dynamic track properties exist
    if not hasattr(props, 'use_dynamic_track'):
        print("✗ Missing use_dynamic_track property")
        return False
    print("✓ Dynamic track properties exist")
    
    # Test dynamic interval properties
    if not hasattr(props, 'dynamic_interval_type'):
        print("✗ Missing dynamic_interval_type")
        return False
    if not hasattr(props, 'dynamic_interval_beats'):
        print("✗ Missing dynamic_interval_beats")
        return False
    if not hasattr(props, 'dynamic_interval_bars'):
        print("✗ Missing dynamic_interval_bars")
        return False
    print("✓ Dynamic interval properties exist")
    
    # Test dynamic event generation  
    # Add path to src
    addon_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    if addon_dir not in sys.path:
        sys.path.insert(0, addon_dir)
    
    from midi_core import generate_dynamic_events
    
    # Generate events every 2 beats at 120 BPM, 24 FPS
    events = generate_dynamic_events(
        interval_beats=2.0,
        bpm=120.0,
        fps=24,
        max_frames=240,
        start_frame=1
    )
    
    if not events:
        print("✗ No events generated")
        return False
    
    print(f"✓ Generated {len(events)} events")
    
    # Check event spacing (should be 24 frames apart at 120 BPM, 24 FPS)
    # 120 BPM = 2 beats/sec, so 2 beats = 1 sec = 24 frames
    expected_spacing = 24
    for i in range(1, len(events)):
        spacing = events[i] - events[i-1]
        if abs(spacing - expected_spacing) > 1:  # Allow 1 frame tolerance
            print(f"✗ Incorrect spacing: {spacing} (expected {expected_spacing})")
            return False
    
    print("✓ Event spacing correct")
    
    # Test loading MIDI and checking for dynamic track
    test_midi = os.path.join(os.path.dirname(__file__), '..', 'assets', 'eight-bars-thang.mid')
    if os.path.exists(test_midi):
        # Load MIDI file
        bpy.ops.midipose.load_midi(filepath=test_midi)
        
        # Check if dynamic track was added
        dynamic_tracks = [t for t in props.track_items if t.is_dynamic]
        if not dynamic_tracks:
            print("✗ No dynamic track found after loading MIDI")
            return False
        
        print(f"✓ Dynamic track added: '{dynamic_tracks[0].name}'")
    
    print("\n" + "="*60)
    print("✓ Dynamic track feature works!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)