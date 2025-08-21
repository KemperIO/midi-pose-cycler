#!/usr/bin/env python3
"""Test tone filter functionality"""
import sys
import bpy
import importlib.util

def main():
    print("\n" + "="*60)
    print("Testing Tone Filter UI")
    print("="*60)
    
    # Register addon first
    try:
        sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
        
        # Import and register the addon
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
    
    # Get properties
    props = bpy.context.scene.midi_pose_props
    
    # Create test track
    print("\n1. Creating test track...")
    props.track_items.clear()
    track = props.track_items.add()
    track.name = "TestTrack"
    track.note_count = 10
    track.selected = True
    
    # Add some note filters
    print("\n2. Adding tone filters...")
    for i in range(5):
        note_filter = track.note_filters.add()
        note_filter.note_number = 60 + i
        note_filter.note_name = f"C{3 + i//12}"
        note_filter.selected = True
    
    print(f"  ✓ Added {len(track.note_filters)} tone filters")
    
    # Test filter_notes toggle
    print("\n3. Testing filter_notes toggle...")
    print(f"  Initial filter_notes: {track.filter_notes}")
    track.filter_notes = True
    print(f"  After setting True: {track.filter_notes}")
    
    # Check if filters exist
    print("\n4. Checking tone filters...")
    if track.note_filters:
        print(f"  ✓ Track has {len(track.note_filters)} tone filters")
        for i, nf in enumerate(track.note_filters):
            print(f"    - {nf.note_name} ({nf.note_number}): selected={nf.selected}")
    else:
        print("  ✗ No tone filters found")
        return False
    
    print("\n" + "="*60)
    print("✓ All tone filter tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)