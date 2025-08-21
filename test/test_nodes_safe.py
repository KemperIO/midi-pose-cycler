"""Test node system without crashes"""

import bpy
import sys


def main():
    print("\n" + "="*60)
    print("Testing Node System (Safe)")
    print("="*60)
    
    # Register addon components
    sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
    
    try:
        import node_tree
        import node_operators
        
        node_tree.register()
        node_operators.register()
        print("✓ Node system registered")
    except Exception as e:
        print(f"✗ Failed to register: {e}")
        return False
    
    # Create node tree
    try:
        tree = bpy.data.node_groups.new("TestTree", 'MidiPoseNodeTree')
        print("✓ Created node tree")
    except Exception as e:
        print(f"✗ Failed to create tree: {e}")
        return False
    
    # Test MIDI Input node
    try:
        midi_node = tree.nodes.new('MidiInputNode')
        midi_node.location = (0, 0)
        print("✓ Created MIDI Input node")
        
        # Test setting file path
        midi_node.midi_file = "test.mid"
        print(f"  File: {midi_node.midi_file}")
    except Exception as e:
        print(f"✗ MIDI Input node failed: {e}")
        return False
    
    # Test Track Selector node
    try:
        track_node = tree.nodes.new('TrackSelectorNode')
        track_node.location = (250, 0)
        print("✓ Created Track Selector node")
        
        # Test properties
        track_node.selected_track = 1
        print(f"  Selected track: {track_node.selected_track}")
    except Exception as e:
        print(f"✗ Track Selector failed: {e}")
        return False
    
    # Test Pose Input node
    try:
        pose_node = tree.nodes.new('PoseInputNode')
        pose_node.location = (0, -200)
        print("✓ Created Pose Input node")
        
        # Test filter
        pose_node.filter_prefix = "test"
        print(f"  Filter: {pose_node.filter_prefix}")
        
        # Test getting poses (should not crash)
        poses = pose_node.get_available_poses()
        print(f"  Found {len(poses)} poses")
    except Exception as e:
        print(f"✗ Pose Input node failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Timing node
    try:
        timing_node = tree.nodes.new('TimingNode')
        timing_node.location = (500, -100)
        print("✓ Created Timing node")
        
        # Test smart timing
        timing_node.use_smart_timing = True
        timing_node.bpm = 140
        print(f"  Smart timing: {timing_node.use_smart_timing}")
        print(f"  BPM: {timing_node.bpm}")
    except Exception as e:
        print(f"✗ Timing node failed: {e}")
        return False
    
    # Test connections
    try:
        tree.links.new(midi_node.outputs[0], track_node.inputs[0])
        tree.links.new(pose_node.outputs[0], timing_node.inputs[1])
        print("✓ Created node connections")
    except Exception as e:
        print(f"✗ Failed to connect nodes: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ All node tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)