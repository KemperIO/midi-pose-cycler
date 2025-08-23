import bpy
import sys

# Open the file
filepath = sys.argv[-1] if len(sys.argv) > 1 else '/workspace/assets/dobby-poses.blend'
bpy.ops.wm.open_mainfile(filepath=filepath)

print("=" * 60)
print(f"Inspecting: {filepath}")
print("=" * 60)

# List all collections
print("\nCollections:")
for col in bpy.data.collections:
    print(f"  - {col.name}")
    for obj in col.objects:
        print(f"    * {obj.name} ({obj.type})")

# List root level objects
print("\nRoot level objects (not in any collection):")
for obj in bpy.data.objects:
    if not obj.users_collection:
        print(f"  - {obj.name} ({obj.type})")

# List armatures specifically
print("\nArmatures:")
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        print(f"  - {obj.name} in collections: {[c.name for c in obj.users_collection]}")

# List actions
print("\nActions:")
for action in bpy.data.actions:
    print(f"  - {action.name}")