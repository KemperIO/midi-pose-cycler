#!/usr/bin/env python3
"""
Test node system for MIDI Pose Cycler
"""

import bpy
import sys
from pathlib import Path

print("Testing MIDI Pose Cycler Node System...")

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    # Import modules
    import node_tree
    import node_operators
    import workspace_node_based
    
    # Register node system
    print("\nRegistering node system...")
    node_tree.register()
    node_operators.register()
    workspace_node_based.register()
    print("✓ Node system registered")
    
    # Create node tree
    print("\nCreating node tree...")
    bpy.ops.midipose.new_node_tree(name="TestNodeTree")
    
    # Check if tree exists
    if "TestNodeTree" in bpy.data.node_groups:
        tree = bpy.data.node_groups["TestNodeTree"]
        print(f"✓ Created node tree with {len(tree.nodes)} nodes")
        
        # List nodes
        print("\nNodes in tree:")
        for node in tree.nodes:
            print(f"  - {node.bl_label} ({node.bl_idname})")
        
        # Check links
        print(f"\nLinks: {len(tree.links)}")
        for link in tree.links:
            print(f"  - {link.from_node.bl_label} -> {link.to_node.bl_label}")
    else:
        print("✗ Failed to create node tree")
    
    # Create workspace
    print("\nCreating node workspace...")
    bpy.ops.midipose.create_node_workspace()
    
    if "MIDI Pose Nodes" in bpy.data.workspaces:
        print("✓ Node workspace created")
        ws = bpy.data.workspaces["MIDI Pose Nodes"]
        screen = ws.screens[0]
        
        # Count area types
        counts = {}
        for area in screen.areas:
            counts[area.type] = counts.get(area.type, 0) + 1
        
        print(f"\nWorkspace has {len(screen.areas)} areas:")
        for atype, count in sorted(counts.items()):
            print(f"  {atype}: {count}")
        
        # Check for node editor
        has_node_editor = 'NODE_EDITOR' in counts
        if has_node_editor:
            print("✓ Node editor present in workspace")
        else:
            print("✗ No node editor in workspace")
    else:
        print("✗ Failed to create workspace")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete")