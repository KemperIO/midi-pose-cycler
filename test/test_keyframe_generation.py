"""Test that keyframes are actually being written to actions"""

import bpy
import sys
import os

def main():
    print("\n" + "="*60)
    print("Testing Keyframe Generation")
    print("="*60)
    
    try:
        # Register addon
        sys.path.insert(0, 'C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src')
        
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "midi_pose_cycler",
            "C:\\Users\\words\\OneDrive\\Desktop\\code\\midi-pose-cycler\\src\\__init__.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules['midi_pose_cycler'] = module
        spec.loader.exec_module(module)
        module.register()
        
        print("✓ Addon registered")
        
        # Create a test armature
        bpy.ops.object.armature_add()
        armature = bpy.context.active_object
        armature.name = "TestArmature"
        print(f"✓ Created test armature: {armature.name}")
        
        # Create some test pose actions
        for i in range(3):
            action = bpy.data.actions.new(name=f"TestPose{i+1}")
            # Add a simple keyframe
            fc = action.fcurves.new(data_path='pose.bones["Bone"].location', index=0)
            fc.keyframe_points.insert(0, float(i))
            print(f"✓ Created test action: {action.name}")
        
        # Set properties for test
        props = bpy.context.scene.midi_pose_props
        props.action_name = "TestOutput"
        props.animation_mode = 'POSE'
        props.frames_to_hold = 5
        props.interpolation_type = 'LINEAR'
        
        # Manually add and select poses
        props.pose_items.clear()
        for i in range(3):
            item = props.pose_items.add()
            item.name = f"TestPose{i+1}"
            item.selected = True
            item.order_index = i
        
        print("\n✓ Properties configured")
        
        # Import animation_renderer to test directly
        from midi_pose_cycler import animation_renderer
        from midi_pose_cycler.animation_renderer import RenderConfig
        
        # Create test config
        config = RenderConfig(
            midi_path="test.mid",
            track_name="test",
            poses=[f"TestPose{i+1}" for i in range(3)],
            target_notes=None,
            frames_to_hold=5,
            interpolation_type='LINEAR',
            fps=24,
            total_frames=100,
            action_name="TestOutput",
            pose_cycle_mode='LOOP',
            animation_mode='POSE',
            start_frame=1
        )
        
        # Test frames where notes occur
        test_frames = [1, 10, 20, 30]
        
        print("\nCalling render_animation...")
        success, pose_mapping = animation_renderer.render_animation(config, test_frames)
        
        if success:
            print(f"✓ render_animation returned success")
            print(f"  Pose mapping has {len(pose_mapping)} entries")
        else:
            print("✗ render_animation failed")
            return False
        
        # Check if action was created and has keyframes
        output_action = bpy.data.actions.get("TestOutput")
        if output_action:
            print(f"✓ Output action '{output_action.name}' exists")
            print(f"  Has {len(output_action.fcurves)} FCurves")
            
            total_keyframes = 0
            for fc in output_action.fcurves:
                num_keys = len(fc.keyframe_points)
                total_keyframes += num_keys
                if num_keys > 0:
                    print(f"  FCurve {fc.data_path}[{fc.array_index}]: {num_keys} keyframes")
            
            if total_keyframes > 0:
                print(f"✓ KEYFRAMES FOUND: {total_keyframes} total keyframes in action!")
                return True
            else:
                print(f"✗ NO KEYFRAMES FOUND in action!")
                return False
        else:
            print("✗ Output action not created")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)