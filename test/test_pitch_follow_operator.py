#!/usr/bin/env python3
"""Test pitch follow mode through the actual operator"""
import sys
import os
import bpy
import importlib.util

def create_test_midi():
    """Create a test MIDI file with known tone values"""
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    from midi_core import get_mido
    
    mido = get_mido()
    if not mido:
        return None
        
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    track.append(mido.MetaMessage('track_name', name='TestTrack', time=0))
    
    # Add notes with different pitches
    test_notes = [60, 72, 60]  # Low, high, low
    time_delta = 480
    
    for note in test_notes:
        track.append(mido.Message('note_on', note=note, velocity=64, time=time_delta))
        track.append(mido.Message('note_off', note=note, velocity=0, time=time_delta))
    
    temp_path = "C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\test\\test_operator.mid"
    mid.save(temp_path)
    return temp_path

def main():
    print("\n" + "="*60)
    print("Testing PITCH_FOLLOW Mode via Operator")
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
    print("\n1. Creating test MIDI...")
    midi_path = create_test_midi()
    if not midi_path:
        print("✗ Failed to create test MIDI")
        return False
    print(f"✓ Created: {os.path.basename(midi_path)}")
    
    # Setup scene
    props = bpy.context.scene.midi_pose_props
    scene = bpy.context.scene
    
    # Load MIDI using operator
    print("\n2. Loading MIDI via operator...")
    props.midi_file = midi_path
    bpy.ops.midipose.load_midi(filepath=midi_path)
    
    # Check tracks loaded
    if not props.track_items:
        print("✗ No tracks loaded")
        return False
    
    print(f"✓ Loaded {len(props.track_items)} tracks")
    
    # Select first track
    track = props.track_items[0]
    track.selected = True
    print(f"  Selected: {track.name} ({track.note_count} notes)")
    
    # Create poses with actual keyframes
    print("\n3. Creating test poses...")
    props.pose_items.clear()
    for i in range(3):
        action = bpy.data.actions.new(name=f"Pose{i}")
        # Add a test keyframe at frame 0 for location
        fc = action.fcurves.new(data_path="location", index=0)
        fc.keyframe_points.insert(0, i * 0.5)  # Different values for each pose
        
        pose = props.pose_items.add()
        pose.name = action.name
        pose.selected = True
        pose.order_index = i
    print(f"✓ Created {len(props.pose_items)} poses with keyframes")
    
    # Configure for pitch follow
    print("\n4. Configuring PITCH_FOLLOW...")
    props.pose_cycle_mode = 'PITCH_FOLLOW'
    props.action_name = "PitchTestAnimation"
    props.frames_to_hold = 3
    props.animation_mode = 'POSE'
    props.use_frame_limit = True
    props.frame_limit = 100
    
    # Add an armature to animate
    print("\n5. Creating test armature...")
    bpy.ops.object.armature_add()
    armature = bpy.context.active_object
    if not armature:
        print("✗ No active object after creating armature")
        return False
    print(f"✓ Created armature: {armature.name}")
    print(f"  Active object: {bpy.context.active_object.name if bpy.context.active_object else 'None'}")
    
    # Run the render operator
    print("\n6. Running render_animation operator...")
    print(f"  Mode: {props.pose_cycle_mode}")
    print(f"  Tracks: {[t.name for t in props.track_items if t.selected]}")
    print(f"  Poses: {[p.name for p in props.pose_items if p.selected]}")
    
    # Capture output
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Don't capture output so we can see what's happening
    result = bpy.ops.midipose.render_animation()
    
    output = stdout_capture.getvalue()
    errors = stderr_capture.getvalue()
    
    print("\n7. Checking results...")
    
    # Check for errors
    if "ERROR: Pitch follow mode requires tone data" in output or "ERROR: Pitch follow mode requires tone data" in errors:
        print("✗ PITCH_FOLLOW failed: missing tone data")
        print("\nOperator output:")
        print(output)
        if errors:
            print("\nErrors:")
            print(errors)
        return False
    
    if result != {'FINISHED'}:
        print(f"✗ Operator failed: {result}")
        print("\nOutput:", output)
        if errors:
            print("\nErrors:", errors)
        return False
    
    print("✓ Operator completed successfully")
    
    # Check if animation was created
    action = bpy.data.actions.get(props.action_name)
    if not action:
        print("✗ No action created")
        return False
    
    if not action.fcurves:
        print("✗ Action has no keyframes")
        return False
    
    keyframe_count = sum(len(fc.keyframe_points) for fc in action.fcurves)
    print(f"✓ Created action with {keyframe_count} keyframes")
    
    # Cleanup
    os.remove(midi_path)
    
    print("\n" + "="*60)
    print("✓ PITCH_FOLLOW operator test passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)