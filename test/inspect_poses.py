import bpy
import sys

# Open the file
filepath = sys.argv[-1] if len(sys.argv) > 1 else '/workspace/assets/dobby-poses.blend'
bpy.ops.wm.open_mainfile(filepath=filepath)

print("=" * 60)
print(f"Inspecting poses in: {filepath}")
print("=" * 60)

# List all actions
print("\nAll Actions:")
for action in bpy.data.actions:
    print(f"  - {action.name}")
    
# Check if there's a catalog file
import os
from pathlib import Path

blend_path = Path(filepath)
catalog_file = blend_path.parent / "blender_assets.cats.txt"

if catalog_file.exists():
    print(f"\nCatalog file found: {catalog_file}")
    with open(catalog_file, 'r') as f:
        print("Catalog contents:")
        for line in f:
            if line.strip() and not line.startswith('#'):
                print(f"  {line.strip()}")
else:
    print(f"\nNo catalog file found at: {catalog_file}")

# Try to find pose libraries
print("\nPose Libraries:")
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and obj.pose_library:
        print(f"  - {obj.name} has pose library: {obj.pose_library.name}")
        for pose_marker in obj.pose_library.pose_markers:
            print(f"    * {pose_marker.name} (frame {pose_marker.frame})")