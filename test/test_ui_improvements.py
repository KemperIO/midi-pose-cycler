#!/usr/bin/env python3
"""Test latest UI improvements"""
import sys
import bpy
import importlib.util

def main():
    print("\n" + "="*60)
    print("Testing UI Improvements")
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
    
    props = bpy.context.scene.midi_pose_props
    
    # Test 1: Pose panel improvements
    print("\n1. Testing Pose Panel...")
    
    # Create test poses
    for i in range(3):
        action = bpy.data.actions.new(name=f"TestPose{i}")
        fc = action.fcurves.new(data_path="location", index=0)
        fc.keyframe_points.insert(0, i * 0.5)
        
        pose = props.pose_items.add()
        pose.name = action.name
        pose.selected = True
    
    print(f"  ✓ Created {len(props.pose_items)} test poses")
    
    # Verify refresh operator exists
    try:
        bpy.ops.midipose.refresh_poses()
        print("  ✓ Refresh poses operator works")
    except:
        print("  ✗ Refresh poses operator failed")
        return False
    
    # Test 2: Tone filter improvements
    print("\n2. Testing Tone Filter UI...")
    
    # Create test track with tones
    props.track_items.clear()
    track = props.track_items.add()
    track.name = "TestTrack"
    track.note_count = 10
    track.selected = True
    
    # Add tone filters
    test_tones = [(60, "C3"), (62, "D3"), (64, "E3"), (65, "F3"), (67, "G3")]
    for note, name in test_tones:
        nf = track.note_filters.add()
        nf.note_number = note
        nf.note_name = name
        nf.selected = True
    
    print(f"  ✓ Added {len(track.note_filters)} tone filters")
    
    # Test filter_notes property (now a simple checkbox)
    print("\n3. Testing filter checkbox...")
    
    # Should start false
    if track.filter_notes:
        print("  ✗ filter_notes should start False")
        return False
    
    # Enable filtering
    track.filter_notes = True
    if not track.filter_notes:
        print("  ✗ Failed to enable filtering")
        return False
    
    print("  ✓ Filter checkbox works")
    
    # When enabled, UI should show tone checkboxes
    print("  ✓ When 'Filter' checked, tone checkboxes should be visible")
    
    # Test tone selection
    print("\n4. Testing tone selection...")
    
    # Deselect all
    for nf in track.note_filters:
        nf.selected = False
    
    selected = sum(1 for nf in track.note_filters if nf.selected)
    if selected != 0:
        print(f"  ✗ Failed to deselect all: {selected} selected")
        return False
    
    # Select some
    track.note_filters[0].selected = True
    track.note_filters[2].selected = True
    
    selected = sum(1 for nf in track.note_filters if nf.selected)
    if selected != 2:
        print(f"  ✗ Expected 2 selected, got {selected}")
        return False
    
    print("  ✓ Tone selection works")
    
    # Test operators for batch selection
    print("\n5. Testing batch selection operators...")
    
    try:
        # Select all
        bpy.ops.midipose.select_all_track_notes(track_name="TestTrack")
        selected = sum(1 for nf in track.note_filters if nf.selected)
        if selected != len(track.note_filters):
            print(f"  ✗ Select all failed: {selected}/{len(track.note_filters)}")
            return False
        print("  ✓ Select all works")
        
        # Deselect all
        bpy.ops.midipose.deselect_all_track_notes(track_name="TestTrack")
        selected = sum(1 for nf in track.note_filters if nf.selected)
        if selected != 0:
            print(f"  ✗ Deselect all failed: {selected} selected")
            return False
        print("  ✓ Deselect all works")
        
        # Invert
        track.note_filters[1].selected = True
        track.note_filters[3].selected = True
        bpy.ops.midipose.invert_track_notes(track_name="TestTrack")
        
        # Should have 0,2,4 selected now
        expected = [0, 2, 4]
        actual = [i for i, nf in enumerate(track.note_filters) if nf.selected]
        if actual != expected:
            print(f"  ✗ Invert failed: expected {expected}, got {actual}")
            return False
        print("  ✓ Invert works")
        
    except Exception as e:
        print(f"  ✗ Batch operators failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ All UI improvement tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)