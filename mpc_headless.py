#!/usr/bin/env python
"""Headless MIDI Pose Cycler - Generate animations from markdown table input.

Usage:
    blender --background --python mpc_headless.py -- input.md
    blender --background --python mpc_headless.py -- --input "markdown string"
"""

import sys
import argparse
from pathlib import Path

# Add headless module to path
sys.path.insert(0, str(Path(__file__).parent))

from headless.parser import MarkdownTableParser
from headless.animation_generator import AnimationGenerator
from headless.video_renderer import VideoRenderer


def main():
    """Main entry point for headless operation."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MIDI Pose Cycler Headless Mode')
    parser.add_argument('input', nargs='?', help='Path to markdown input file')
    parser.add_argument('--input', dest='input_string', help='Markdown input as string')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate input without generating')
    
    # Handle Blender's -- separator
    if '--' in sys.argv:
        argv = sys.argv[sys.argv.index('--') + 1:]
    else:
        argv = sys.argv[1:]
    
    args = parser.parse_args(argv)
    
    # Get input markdown
    if args.input_string:
        markdown_input = args.input_string
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
    except ImportError:
        print("Error: This script must be run from within Blender")
        print("Usage: blender --background --python mpc_headless.py -- input.md")
        sys.exit(1)
    
    sys.exit(main())