#!/usr/bin/env python3
"""Test tone filter UI expansion and functionality"""
import sys
import os
import bpy
import importlib.util

def main():
    print("\n" + "="*60)
    print("Testing Tone Filter UI Expansion")
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
    
    # Create test tracks with tone filters
    print("\n1. Creating test tracks with tone filters...")
    props.track_items.clear()
    
    # Track 1: Regular MIDI track
    track1 = props.track_items.add()
    track1.name = "Piano"
    track1.note_count = 20
    track1.selected = True
    track1.is_dynamic = False
    
    # Add tone filters for track 1
    for i, (note, name) in enumerate([(60, "C3"), (62, "D3"), (64, "E3"), (65, "F3"), (67, "G3")]):
        nf = track1.note_filters.add()
        nf.note_number = note
        nf.note_name = name
        nf.selected = True
    
    print(f"  ✓ Track 1: {track1.name} with {len(track1.note_filters)} tone filters")
    
    # Track 2: Another MIDI track
    track2 = props.track_items.add()
    track2.name = "Bass"
    track2.note_count = 15
    track2.selected = True
    track2.is_dynamic = False
    
    # Add tone filters for track 2
    for i, (note, name) in enumerate([(36, "C1"), (38, "D1"), (40, "E1")]):
        nf = track2.note_filters.add()
        nf.note_number = note
        nf.note_name = name
        nf.selected = i == 0  # Only first selected
    
    print(f"  ✓ Track 2: {track2.name} with {len(track2.note_filters)} tone filters")
    
    # Track 3: Dynamic track (no tone filters)
    track3 = props.track_items.add()
    track3.name = "Every 2 beats"
    track3.is_dynamic = True
    track3.selected = False
    
    print(f"  ✓ Track 3: {track3.name} (dynamic)")
    
    # Test filter_notes toggle
    print("\n2. Testing filter_notes toggle...")
    
    # Initially all should be collapsed
    for i, track in enumerate(props.track_items):
        if track.filter_notes:
            print(f"  ✗ Track {i+1} filter_notes should start False, got True")
            return False
    print("  ✓ All tracks start with filters collapsed")
    
    # Toggle track 1 filters
    track1.filter_notes = True
    if not track1.filter_notes:
        print("  ✗ Failed to expand track 1 filters")
        return False
    print("  ✓ Track 1 filters expanded")
    
    # Check filter content
    print("\n3. Checking filter content...")
    
    if not track1.note_filters:
        print("  ✗ Track 1 has no tone filters")
        return False
    
    selected_count = sum(1 for nf in track1.note_filters if nf.selected)
    print(f"  ✓ Track 1: {selected_count}/{len(track1.note_filters)} tones selected")
    
    # Test selection operations
    print("\n4. Testing tone selection...")
    
    # Deselect all
    for nf in track1.note_filters:
        nf.selected = False
    
    selected_count = sum(1 for nf in track1.note_filters if nf.selected)
    if selected_count != 0:
        print(f"  ✗ Failed to deselect all: {selected_count} still selected")
        return False
    print("  ✓ Deselected all tones")
    
    # Select specific tones
    track1.note_filters[0].selected = True
    track1.note_filters[2].selected = True
    
    selected_count = sum(1 for nf in track1.note_filters if nf.selected)
    if selected_count != 2:
        print(f"  ✗ Expected 2 selected, got {selected_count}")
        return False
    print("  ✓ Selected specific tones")
    
    # Test tone names
    print("\n5. Testing tone names...")
    
    for nf in track1.note_filters:
        if not nf.note_name:
            print(f"  ✗ Tone {nf.note_number} has no name")
            return False
        
        # Check format
        if nf.note_number == 60 and nf.note_name != "C3":
            print(f"  ✗ MIDI 60 should be C3, got {nf.note_name}")
            return False
    
    print("  ✓ All tones have correct names")
    
    # Test dynamic track
    print("\n6. Testing dynamic track...")
    
    if track3.note_filters:
        print(f"  ✗ Dynamic track should have no tone filters, has {len(track3.note_filters)}")
        return False
    print("  ✓ Dynamic track has no tone filters")
    
    # Test multi-track selection
    print("\n7. Testing multi-track selection...")
    
    selected_tracks = [t for t in props.track_items if t.selected]
    if len(selected_tracks) != 2:
        print(f"  ✗ Expected 2 selected tracks, got {len(selected_tracks)}")
        return False
    
    print(f"  ✓ {len(selected_tracks)} tracks selected")
    
    # Test per-track filter state
    print("\n8. Testing per-track filter state...")
    
    track2.filter_notes = True
    
    if not track1.filter_notes:
        print("  ✗ Track 1 filters should still be expanded")
        return False
    
    if not track2.filter_notes:
        print("  ✗ Track 2 filters should be expanded")
        return False
    
    print("  ✓ Multiple tracks can have filters expanded")
    
    print("\n" + "="*60)
    print("✓ All tone filter UI tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)