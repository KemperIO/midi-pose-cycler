#!/usr/bin/env python3
"""Test simple video rendering."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Test simple video rendering."""
    try:
        import bpy
    except ImportError:
        print("Error: Must run within Blender")
        return False
    
    # Import modules
    from headless.parser import MarkdownTableParser
    from headless.simple_video_renderer import SimpleVideoRenderer
    
    # Load test config
    test_input = Path(__file__).parent.parent / "headless_test" / "example_input.md"
    config = MarkdownTableParser.parse(test_input.read_text())
    
    # Enable video rendering
    config.form.shouldCreateVideo = True
    
    # Check that action file exists
    action_file = Path(config.form.blendFileToOutputAction)
    if not action_file.exists():
        print(f"ERROR: Action file not found: {action_file}")
        print("Please run animation generation first")
        return False
    
    # Test video rendering
    renderer = SimpleVideoRenderer(config)
    video_file = renderer.render()
    
    if video_file:
        print(f"\n✓ SUCCESS: Video rendered to {video_file}")
        
        # Check file size
        video_path = Path(video_file)
        if video_path.exists():
            size_kb = video_path.stat().st_size / 1024
            print(f"File size: {size_kb:.1f} KB")
            
            if size_kb < 1:
                print("WARNING: Video file is suspiciously small")
                return False
        
        return True
    else:
        print("\n✗ FAILED: Video rendering failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)