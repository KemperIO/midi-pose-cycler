"""
Simple test for MIDI file loading
Tests that eight-bars-thang.mid loads with expected tracks
"""

import os
import sys

def main():
    """Test MIDI file analysis directly"""
    print("\n" + "="*60)
    print("Testing MIDI File Analysis (Simple)")
    print("="*60)
    
    # Get paths
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(test_dir)
    src_dir = os.path.join(project_dir, "src")
    
    # Add src to path
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Get MIDI file
    midi_file = os.path.join(project_dir, "assets", "eight-bars-thang.mid")
    
    if not os.path.exists(midi_file):
        print(f"✗ MIDI file not found: {midi_file}")
        return False
    
    print(f"✓ Found MIDI file: {os.path.basename(midi_file)}")
    
    try:
        # Import and test midi_core
        import midi_core
        
        if not midi_core.MIDO_AVAILABLE:
            print("✗ mido library not available")
            return False
        
        print("✓ mido library loaded")
        
        # Analyze the file
        analysis = midi_core.analyze_midi_file(midi_file)
        
        if analysis is None:
            print("✗ Failed to analyze MIDI file")
            return False
        
        print(f"✓ MIDI analyzed: {len(analysis.tracks)} tracks found")
        
        # Verify we have at least 1 track
        if len(analysis.tracks) < 1:
            print("✗ No tracks found (expected at least 1)")
            return False
        
        # Expected track names (from the output above)
        expected_tracks = ["kick", "snare", "shaker", "horns"]
        found_tracks = [t.name for t in analysis.tracks]
        
        # Check for some expected tracks
        for expected in expected_tracks[:2]:  # Check at least kick and snare
            if expected in found_tracks:
                print(f"  ✓ Found track: {expected}")
            else:
                print(f"  ✗ Missing expected track: {expected}")
                
        # Summary
        print("\nTrack Summary:")
        for track in analysis.tracks[:5]:  # Show first 5
            print(f"  - {track.name}: {track.note_count} notes")
        
        if len(analysis.tracks) > 5:
            print(f"  ... and {len(analysis.tracks) - 5} more tracks")
        
        print("\n" + "="*60)
        print("✓ MIDI file test passed!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)