#!/usr/bin/env python3
"""Headless MIDI Pose Cycler - Generate animations from markdown table input.

Usage:
    # Direct invocation (NEW):
    python mpc_headless.py input.md
    python mpc_headless.py -s "markdown string"
    python mpc_headless.py --input "markdown string"
    
    # Or traditional Blender invocation:
    blender --background --python mpc_headless.py -- input.md
    blender --background --python mpc_headless.py -- -s "markdown string"
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add headless module to path
sys.path.insert(0, str(Path(__file__).parent))

# Only import Blender-dependent modules if we're in Blender
def import_blender_modules():
    """Import modules that require Blender."""
    global MarkdownTableParser, AnimationGenerator, VideoRenderer
    from headless.parser import MarkdownTableParser
    from headless.animation_generator import AnimationGenerator
    from headless.video_renderer import VideoRenderer


def run_in_blender(args):
    """Run this script inside Blender with the given arguments."""
    # Check if we're in Docker
    in_docker = os.path.exists('/.dockerenv')
    
    # Find Blender executable
    if in_docker:
        blender_paths = [
            "blender",  # In Docker, Blender should be in PATH
        ]
    else:
        blender_paths = [
            "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe",
            "blender",  # Try system PATH
        ]
    
    blender_exe = None
    for path in blender_paths:
        if os.path.exists(path) or path == "blender":
            blender_exe = path
            break
    
    if not blender_exe:
        print("Error: Could not find Blender executable")
        print("Please ensure Blender 4.5 is installed or available in PATH")
        return 1
    
    # Build command
    cmd = [
        blender_exe,
        "--background",
        "--factory-startup",
        "--python", __file__,
        "--"
    ] + args
    
    # Run Blender
    # Only show command if verbose or debugging
    if os.environ.get('DEBUG') or '--verbose' in args:
        print(f"Launching Blender: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode


def parse_arguments(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='MIDI Pose Cycler Headless Mode')
    parser.add_argument('input', nargs='?', help='Path to markdown input file')
    parser.add_argument('--input', dest='input_string', help='Markdown input as string')
    parser.add_argument('-s', dest='input_string_short', help='Markdown input as string (short form)')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate input without generating')
    return parser.parse_args(argv)


def main():
    """Main entry point for headless operation."""
    # Import Blender modules now that we're in Blender
    import_blender_modules()
    
    # Handle Blender's -- separator
    if '--' in sys.argv:
        argv = sys.argv[sys.argv.index('--') + 1:]
    else:
        argv = sys.argv[1:]
    
    args = parse_arguments(argv)
    
    # Get input markdown
    if args.input_string or args.input_string_short:
        markdown_input = args.input_string or args.input_string_short
    elif args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            return 1
        markdown_input = input_path.read_text()
    else:
        print("Error: No input provided. Use file path or --input flag")
        return 1
    
    # Parse markdown tables
    try:
        config = MarkdownTableParser.parse(markdown_input)
    except Exception as e:
        print(f"Error parsing input: {e}")
        return 1
    
    # Validate configuration
    print("\n" + "="*80)
    print("MIDI POSE CYCLER - HEADLESS MODE")
    print("="*80)
    
    is_valid = config.print_validation_table()
    
    if not is_valid:
        print("\nValidation failed. Please fix errors and try again.")
        return 1
    
    if args.validate_only:
        print("\nValidation complete (--validate-only flag set)")
        return 0
    
    # Generate animation
    print("\n" + "="*80)
    print("GENERATING ANIMATION")
    print("="*80)
    
    try:
        generator = AnimationGenerator(config)
        output_file = generator.generate()
        print(f"\n✓ Animation created: {output_file}")
    except Exception as e:
        print(f"\n✗ Animation generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Render video if requested
    if config.form.shouldCreateVideo:
        print("\n" + "="*80)
        print("RENDERING VIDEO")
        print("="*80)
        
        try:
            renderer = VideoRenderer(config)
            video_file = renderer.render()
            if video_file:
                print(f"\n✓ Video rendered: {video_file}")
            else:
                print("\n✗ Video rendering failed")
                return 1
        except Exception as e:
            print(f"\n✗ Video rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    return 0


if __name__ == "__main__":
    # Check if running in Blender
    try:
        import bpy
        # We're in Blender, run the main function
        sys.exit(main())
    except ImportError:
        # We're not in Blender, so launch Blender with this script
        # Parse arguments to pass them to Blender
        args = sys.argv[1:]
        
        if not args:
            print("Error: No input provided")
            print("Usage: python mpc_headless.py input.md")
            print("   or: python mpc_headless.py --input \"markdown string\"")
            sys.exit(1)
        
        # Run this script in Blender
        sys.exit(run_in_blender(args))