#!/usr/bin/env python3
"""Test pitch follow mode integration with actual MIDI data"""
import sys
import os
import bpy
import importlib.util

def create_test_midi():
    """Create a test MIDI file with known tone values"""
    # Import mido
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    from midi_core import get_mido
    
    mido = get_mido()
    if not mido:
        return None
        
    # Create test MIDI with specific tones
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    track.append(mido.MetaMessage('track_name', name='TestTrack', time=0))
    
    # Add notes with different pitches
    test_notes = [60, 64, 67, 72, 60, 64]  # C4, E4, G4, C5, C4, E4
    time_delta = 480  # Quarter note
    
    for note in test_notes:
        track.append(mido.Message('note_on', note=note, velocity=64, time=time_delta))
        track.append(mido.Message('note_off', note=note, velocity=0, time=time_delta))
    
    # Save to temp file
    temp_path = "C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\test\\test_pitch.mid"
    mid.save(temp_path)
    return temp_path

def main():
    print("\n" + "="*60)
    print("Testing PITCH_FOLLOW Mode Integration")
    print("="*60)
    
    # Register addon
    try:
        sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
        spec = importlib.util.spec_from_file_location(
            "midi_pose_cycler",
            "C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src\\__init__.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules['midi_pose_cycler'] = module
        spec.loader.exec_module(module)
        module.register()
        print("✓ Addon registered")
    except Exception as e:
        print(f"✗ Failed to register addon: {e}")
        return False
    
    # Create test MIDI
    print("\n1. Creating test MIDI file...")
    midi_path = create_test_midi()
    if not midi_path:
        print("✗ Failed to create test MIDI")
        return False
    print(f"✓ Created test MIDI: {midi_path}")
    
    # Get properties
    props = bpy.context.scene.midi_pose_props
    scene = bpy.context.scene
    
    # Load MIDI file
    print("\n2. Loading MIDI file...")
    props.midi_file = midi_path
    
    # Analyze it
    from midi_core import analyze_midi_file
    analysis = analyze_midi_file(midi_path)
    if not analysis:
        print("✗ Failed to analyze MIDI")
        return False
    
    print(f"✓ Analyzed MIDI: {len(analysis.tracks)} tracks")
    
    # Setup tracks
    print("\n3. Setting up tracks...")
    props.track_items.clear()
    for track in analysis.tracks:
        item = props.track_items.add()
        item.name = track.name
        item.note_count = track.note_count
        item.selected = True
        
        # Add note filters
        item.note_filters.clear()
        for note_num in sorted(track.notes.keys()):
            note_filter = item.note_filters.add()
            note_filter.note_number = note_num
            from midi_core import midi_note_to_name
            note_filter.note_name = midi_note_to_name(note_num)
            note_filter.selected = True
        
        print(f"  ✓ Track '{item.name}': {item.note_count} notes")
    
    # Create test poses
    print("\n4. Creating test poses...")
    for i in range(3):
        action = bpy.data.actions.new(name=f"TestPose{i}")
        pose_item = props.pose_items.add()
        pose_item.name = action.name
        pose_item.selected = True
        pose_item.order_index = i
        print(f"  ✓ Created pose: {action.name}")
    
    # Set to PITCH_FOLLOW mode
    print("\n5. Setting PITCH_FOLLOW mode...")
    props.pose_cycle_mode = 'PITCH_FOLLOW'
    props.action_name = "TestPitchFollowAnimation"
    props.frames_to_hold = 5
    props.bpm = 120
    
    # Test getting note events with tones
    print("\n6. Testing note event collection...")
    from midi_core import get_note_events_with_tones
    
    selected_tracks = [t for t in props.track_items if t.selected]
    if not selected_tracks:
        print("✗ No tracks selected")
        return False
    
    track = selected_tracks[0]
    frames, tones = get_note_events_with_tones(
        midi_path,
        track.name,
        None,  # No filter
        scene.render.fps,
        1000  # Max frames
    )
    
    if not frames or not tones:
        print(f"✗ No events collected: frames={len(frames) if frames else 0}, tones={len(tones) if tones else 0}")
        return False
    
    if len(frames) != len(tones):
        print(f"✗ Frame/tone mismatch: {len(frames)} frames, {len(tones)} tones")
        return False
    
    print(f"✓ Collected {len(frames)} events with tones")
    print(f"  Tone range: {min(tones)} to {max(tones)}")
    
    # Test render configuration
    print("\n7. Testing render configuration...")
    from animation_renderer import RenderConfig
    
    config = RenderConfig(
        midi_path=midi_path,
        track_name=track.name,
        poses=[p.name for p in props.pose_items if p.selected],
        target_notes=None,
        frames_to_hold=props.frames_to_hold,
        interpolation_type='LINEAR',
        fps=scene.render.fps,
        total_frames=1000,
        action_name=props.action_name,
        pose_cycle_mode='PITCH_FOLLOW',
        animation_mode='POSE',
        start_frame=1,
        note_tones=tones  # This is critical!
    )
    
    if not config.note_tones:
        print("✗ Config missing note_tones")
        return False
    
    print(f"✓ Config has {len(config.note_tones)} tones")
    
    # Test pitch follow mapper directly
    print("\n8. Testing PitchFollowMapper...")
    from tone import Tone
    from pitch_follow_mapper import PitchFollowMapper
    
    min_tone = min(tones)
    max_tone = max(tones)
    mapper = PitchFollowMapper(Tone(min_tone), Tone(max_tone))
    
    tone_objects = [Tone(t) for t in tones]
    pose_indices = mapper.map(tone_objects, 3)  # 3 poses
    
    print(f"✓ Mapped {len(tones)} tones to poses")
    print(f"  Pose indices: {pose_indices}")
    
    # Verify no consecutive repeats (except bounce)
    for i in range(1, len(pose_indices)):
        if pose_indices[i] == pose_indices[i-1]:
            # Check if this was a valid bounce
            if tones[i] != tones[i-1]:
                print(f"✗ Unexpected repeat at index {i}: pose {pose_indices[i]} for different tones")
                return False
    
    print("✓ No invalid consecutive repeats")
    
    # Cleanup
    os.remove(midi_path)
    
    print("\n" + "="*60)
    print("✓ All PITCH_FOLLOW integration tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)