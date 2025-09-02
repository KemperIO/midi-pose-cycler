#!/usr/bin/env python3
"""Integration test to verify video length matches MIDI input."""

import sys
import subprocess
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_video_length():
    """Test that video output length is predictable from MIDI input."""
    print("\n" + "="*60)
    print("VIDEO LENGTH INTEGRATION TEST")
    print("="*60)
    
    # Step 1: Generate animation and video
    print("\n1. Running headless generation with video output...")
    result = subprocess.run([
        "python3", "mpc_headless.py",
        "headless_test/example_input.md"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Generation failed")
        print(result.stdout)
        print(result.stderr)
        return False
    
    # Step 2: Parse output for frame range info
    print("\n2. Analyzing output...")
    output_lines = result.stdout.split('\n')
    
    action_start = None
    action_end = None
    poc_start = None
    poc_end = None
    video_file = None
    
    for line in output_lines:
        if "Action frame range:" in line:
            # Extract: "Action frame range: 1 - 192"
            parts = line.split(":")[-1].strip().split(" - ")
            action_start = int(parts[0])
            action_end = int(parts[1])
        elif "POC render range:" in line:
            # Extract: "POC render range: 1 - 48"
            parts = line.split(":")[-1].strip().split(" - ")
            poc_start = int(parts[0])
            poc_end = int(parts[1])
        elif "✓ Video rendered:" in line:
            # Extract video file path
            video_file = line.split(":")[-1].strip()
    
    # Step 3: Verify frame ranges
    print("\n3. Frame range analysis:")
    if action_start and action_end:
        action_frames = action_end - action_start + 1
        action_duration = action_frames / 24.0
        print(f"   Action total: {action_frames} frames ({action_duration:.2f} seconds)")
    else:
        print("   WARNING: Could not parse action frame range")
    
    if poc_start and poc_end:
        poc_frames = poc_end - poc_start + 1
        poc_duration = poc_frames / 24.0
        print(f"   POC render: {poc_frames} frames ({poc_duration:.2f} seconds)")
        
        # Verify POC limit is respected
        if poc_frames > 48:
            print(f"   ERROR: POC exceeded 48 frame limit ({poc_frames} frames)")
            return False
        else:
            print(f"   ✓ POC within 48 frame limit")
    else:
        print("   WARNING: Could not parse POC frame range")
    
    # Step 4: Check video file
    if video_file:
        video_path = Path(video_file)
        if video_path.exists():
            # Get video info with ffmpeg
            print(f"\n4. Checking video file: {video_file}")
            ffmpeg_result = subprocess.run([
                "ffmpeg", "-i", str(video_path)
            ], capture_output=True, text=True)
            
            # Parse duration from ffmpeg stderr (where ffmpeg outputs info)
            for line in ffmpeg_result.stderr.split('\n'):
                if "Duration:" in line:
                    # Extract: "Duration: 00:00:02.00"
                    duration_str = line.split("Duration:")[1].split(",")[0].strip()
                    print(f"   Video duration: {duration_str}")
                    
                    # Convert to seconds
                    parts = duration_str.split(":")
                    hours = float(parts[0])
                    minutes = float(parts[1])
                    seconds = float(parts[2])
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    
                    # Expected duration from POC frames
                    if poc_start and poc_end:
                        expected_seconds = (poc_end - poc_start + 1) / 24.0
                        
                        # Allow small tolerance for encoding
                        tolerance = 0.1
                        if abs(total_seconds - expected_seconds) < tolerance:
                            print(f"   ✓ Video duration matches POC frames ({expected_seconds:.2f}s)")
                        else:
                            print(f"   ERROR: Duration mismatch")
                            print(f"   Expected: {expected_seconds:.2f}s")
                            print(f"   Actual: {total_seconds:.2f}s")
                            return False
                    break
            
            # Check file size
            size_kb = video_path.stat().st_size / 1024
            print(f"   File size: {size_kb:.1f} KB")
            
            if size_kb < 1:
                print("   ERROR: Video file too small")
                return False
            else:
                print("   ✓ Video file has content")
        else:
            print(f"   ERROR: Video file not found: {video_file}")
            return False
    else:
        print("   ERROR: No video file path in output")
        return False
    
    print("\n" + "="*60)
    print("TEST PASSED ✓")
    print("="*60)
    return True


def main():
    """Run the test."""
    # First ensure we have a fresh animation
    print("Preparing test...")
    
    # Clean up old files
    action_file = Path("headless_test/actions.blend")
    if action_file.exists():
        action_file.unlink()
        print(f"Removed old {action_file}")
    
    # Run test
    success = test_video_length()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())