#!/usr/bin/env python3
"""Test pose catalog detection from Blender files."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Test pose catalog detection."""
    try:
        import bpy
    except ImportError:
        print("Error: Must run within Blender")
        return False
    
    print("=" * 60)
    print("TESTING POSE CATALOG DETECTION")
    print("=" * 60)
    
    # Test file
    pose_file = Path(__file__).parent.parent / "assets" / "dobby-poses.blend"
    catalog_file = pose_file.parent / "blender_assets.cats.txt"
    
    print(f"\nTesting file: {pose_file}")
    print(f"Catalog file: {catalog_file}")
    
    # Read catalog file
    catalogs = {}
    if catalog_file.exists():
        print("\n=== Catalog File Contents ===")
        with open(catalog_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('VERSION'):
                    parts = line.split(':')
                    if len(parts) >= 3:
                        catalog_id = parts[0]
                        catalog_path = parts[1]
                        catalog_name = parts[2]
                        catalogs[catalog_name] = catalog_id
                        print(f"  Catalog: {catalog_name} -> ID: {catalog_id}")
    
    # Load the blend file
    print("\n=== Loading Blend File ===")
    with bpy.data.libraries.load(str(pose_file), link=False) as (data_from, data_to):
        print(f"  Actions available: {len(data_from.actions)}")
        data_to.actions = list(data_from.actions)
    
    # Check each catalog
    print("\n=== Checking Pose Catalogs ===")
    expected_catalogs = ['hips', 'feet', 'hands']
    found_catalogs = {}
    
    for catalog_name in expected_catalogs:
        print(f"\nCatalog: {catalog_name}")
        catalog_id = catalogs.get(catalog_name)
        
        if catalog_id:
            print(f"  ID: {catalog_id}")
        else:
            print(f"  WARNING: No catalog ID found for '{catalog_name}'")
        
        # Find actions in this catalog
        poses_found = []
        
        for action in bpy.data.actions:
            # Check if action has asset data
            if hasattr(action, 'asset_data') and action.asset_data:
                if catalog_id and str(action.asset_data.catalog_id) == catalog_id:
                    poses_found.append(action.name)
                    print(f"    ✓ Found pose: {action.name}")
        
        # Also check by name pattern as fallback
        if not poses_found:
            print(f"  No poses found by catalog ID, trying name matching...")
            for action in bpy.data.actions:
                # Check various naming patterns
                if (catalog_name.lower() in action.name.lower() or
                    action.name.startswith(f"ak2-{catalog_name[0]}") or  # e.g., ak2-h for hands
                    action.name.startswith(f"ak-{catalog_name[:3]}")):   # e.g., ak-hip for hips
                    poses_found.append(action.name)
                    print(f"    ✓ Found by name: {action.name}")
        
        found_catalogs[catalog_name] = poses_found
        
        if poses_found:
            print(f"  Total poses found: {len(poses_found)}")
        else:
            print(f"  ERROR: No poses found for catalog '{catalog_name}'")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for catalog_name in expected_catalogs:
        poses = found_catalogs[catalog_name]
        if poses:
            print(f"✓ {catalog_name}: {len(poses)} poses found")
        else:
            print(f"✗ {catalog_name}: NO POSES FOUND")
            all_passed = False
    
    # Additional debug info
    print("\n=== All Actions in File ===")
    for action in bpy.data.actions[:20]:  # Show first 20
        catalog_info = ""
        if hasattr(action, 'asset_data') and action.asset_data:
            catalog_info = f" (catalog_id: {action.asset_data.catalog_id})"
        print(f"  - {action.name}{catalog_info}")
    
    if len(bpy.data.actions) > 20:
        print(f"  ... and {len(bpy.data.actions) - 20} more")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)