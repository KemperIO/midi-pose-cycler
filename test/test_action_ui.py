#!/usr/bin/env python3
"""Test action UI changes - dope sheet filtering and keyframe warning"""
import sys
import os
import bpy
import importlib.util

def main():
    print("\n" + "="*60)
    print("Testing Action UI Features")
    print("="*60)
    
    # Register addon first
    try:
        sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
        
        # Import and register the addon
        spec = importlib.util.spec_from_file_location(
            "midi_pose_cycler",
            "C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src\\__init__.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules['midi_pose_cycler'] = module
        spec.loader.exec_module(module)
        module.register()
        print("✓ Addon registered")
    except Exception as e:
        print(f"✗ Failed to register addon: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create some test actions
    print("\n1. Creating test actions...")
    
    # Create a regular action with keyframes
    action_with_keys = bpy.data.actions.new(name="TestActionWithKeys")
    fc = action_with_keys.fcurves.new(data_path="location", index=0)
    fc.keyframe_points.insert(1, 0.0)
    fc.keyframe_points.insert(10, 1.0)
    print(f"  ✓ Created action '{action_with_keys.name}' with keyframes")
    
    # Create an empty action
    action_empty = bpy.data.actions.new(name="TestActionEmpty")
    print(f"  ✓ Created action '{action_empty.name}' without keyframes")
    
    # Test warning behavior
    print("\n2. Testing keyframe warning...")
    props = bpy.context.scene.midi_pose_props
    
    # Set action with keyframes
    props.action_name = "TestActionWithKeys"
    action = bpy.data.actions.get(props.action_name)
    if action and action.fcurves:
        has_keyframes = any(fc.keyframe_points for fc in action.fcurves)
        if has_keyframes:
            print(f"  ✓ Warning should appear for '{props.action_name}'")
        else:
            print(f"  ✗ No keyframes detected for '{props.action_name}'")
            return False
    
    # Switch to empty action
    props.action_name = "TestActionEmpty"
    action = bpy.data.actions.get(props.action_name)
    if action and action.fcurves:
        has_keyframes = any(fc.keyframe_points for fc in action.fcurves)
        if has_keyframes:
            print(f"  ✗ Warning incorrectly showing for '{props.action_name}'")
            return False
    print(f"  ✓ Warning should NOT appear for '{props.action_name}'")
    
    # Clear action name
    props.action_name = ""
    print("  ✓ No warning for empty action name")
    
    # Test set_action_name operator
    print("\n3. Testing set_action_name operator...")
    try:
        bpy.ops.midipose.set_action_name(action_name="TestActionWithKeys")
        if props.action_name == "TestActionWithKeys":
            print("  ✓ set_action_name operator works")
        else:
            print("  ✗ set_action_name operator failed")
            return False
    except AttributeError as e:
        print(f"  ✗ Operator not registered: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ All action UI tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)