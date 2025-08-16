#!/usr/bin/env python3
"""
Package the MIDI Pose Cycler Blender extension for distribution.

This script creates a properly formatted .zip file ready for:
- Manual installation in Blender
- Distribution to users
- Submission to Blender Extensions platform
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import argparse
import re

def load_manifest():
  """Load and parse the blender_manifest.toml file."""
  manifest_path = Path(__file__).parent / "blender_manifest.toml"
  
  # Simple TOML parser for just the fields we need
  manifest = {}
  with open(manifest_path, "r") as f:
    lines = f.readlines()
    
    for line in lines:
      # Skip schema_version line
      if "schema_version" in line:
        continue
        
      # Extract version (not schema_version)
      version_match = re.match(r'^version\s*=\s*"([^"]+)"', line)
      if version_match:
        manifest["version"] = version_match.group(1)
      
      # Extract id
      id_match = re.match(r'^id\s*=\s*"([^"]+)"', line)
      if id_match:
        manifest["id"] = id_match.group(1)
    
  return manifest

def get_version_string(manifest):
  """Extract version string from manifest."""
  return manifest.get("version", "0.0.0")

def create_build_dir():
  """Create a clean build directory."""
  build_dir = Path(__file__).parent / "build"
  if build_dir.exists():
    shutil.rmtree(build_dir)
  build_dir.mkdir()
  return build_dir

def get_files_to_package():
  """Get list of files to include in the package."""
  base_dir = Path(__file__).parent
  
  # Files to include
  include_patterns = [
    "*.py",
    "blender_manifest.toml",
    "LICENSE",
    "README.md",
    "CLAUDE.md",
  ]
  
  # Directories to include
  include_dirs = [
    "vendor",
  ]
  
  # Files/dirs to exclude
  exclude_patterns = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    ".gitignore",
    "build",
    "dist",
    "*.zip",
    "package.py",
    "TODO.md",
    ".DS_Store",
    "Thumbs.db",
  ]
  
  files_to_package = []
  
  # Add individual files
  for pattern in include_patterns:
    for file in base_dir.glob(pattern):
      if file.is_file() and not any(exc in str(file) for exc in exclude_patterns):
        files_to_package.append(file.relative_to(base_dir))
  
  # Add directories recursively
  for dir_name in include_dirs:
    dir_path = base_dir / dir_name
    if dir_path.exists():
      for file in dir_path.rglob("*"):
        if file.is_file() and not any(exc in str(file) for exc in exclude_patterns):
          files_to_package.append(file.relative_to(base_dir))
  
  return sorted(files_to_package)

def create_package(output_name=None, verbose=False):
  """Create the extension package."""
  print("🚀 Starting MIDI Pose Cycler packaging...")
  
  # Load manifest for version info
  manifest = load_manifest()
  version = get_version_string(manifest)
  extension_id = manifest.get("id", "midi_pose_cycler")
  
  # Prepare build directory
  build_dir = create_build_dir()
  
  # Determine output filename
  if output_name:
    zip_filename = output_name
  else:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{extension_id}_v{version}_{timestamp}.zip"
  
  zip_path = build_dir / zip_filename
  
  # Get files to package
  files = get_files_to_package()
  
  if verbose:
    print(f"\n📦 Packaging {len(files)} files:")
    for f in files:
      print(f"  - {f}")
  
  # Create the zip file
  base_dir = Path(__file__).parent
  
  with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Add all files with the extension folder as root
    for file_path in files:
      full_path = base_dir / file_path
      # Archive name includes the extension folder
      archive_name = f"{extension_id}/{file_path}"
      zipf.write(full_path, archive_name)
      if verbose:
        print(f"  Added: {archive_name}")
  
  # Calculate package size
  size_mb = zip_path.stat().st_size / (1024 * 1024)
  
  print(f"\n✅ Package created successfully!")
  print(f"📁 Location: {zip_path}")
  print(f"📊 Size: {size_mb:.2f} MB")
  print(f"🏷️  Version: {version}")
  
  # Quick install instructions
  print(f"\n📝 Installation instructions:")
  print(f"  1. Open Blender")
  print(f"  2. Edit → Preferences → Add-ons")
  print(f"  3. Click 'Install...' and select: {zip_filename}")
  print(f"  4. Enable 'Animation: MIDI Pose Cycler'")
  
  return zip_path

def create_release_package():
  """Create a release package with simplified naming."""
  manifest = load_manifest()
  version = get_version_string(manifest)
  extension_id = manifest.get("id", "midi_pose_cycler")
  
  # Simple release name
  zip_filename = f"{extension_id}_v{version}.zip"
  return create_package(zip_filename, verbose=False)

def main():
  """Main entry point with CLI arguments."""
  parser = argparse.ArgumentParser(
    description="Package MIDI Pose Cycler Blender extension"
  )
  parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Show detailed packaging information"
  )
  parser.add_argument(
    "-r", "--release",
    action="store_true",
    help="Create a release package (simplified naming)"
  )
  parser.add_argument(
    "-o", "--output",
    type=str,
    help="Custom output filename for the package"
  )
  
  args = parser.parse_args()
  
  try:
    if args.release:
      create_release_package()
    else:
      create_package(output_name=args.output, verbose=args.verbose)
  except Exception as e:
    print(f"\n❌ Error: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
  main()