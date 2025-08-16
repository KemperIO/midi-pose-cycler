import bpy
import random
from typing import List, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class RenderConfig:
    """Configuration for rendering animation"""
    midi_path: str
    track_name: str
    poses: List[str]
    target_notes: Optional[Set[int]]
    frames_to_hold: int
    interpolation_type: str
    fps: int
    total_frames: int
    action_name: str = "MidiPoseCyclingAnimation"
    pose_cycle_mode: str = "LOOP"  # LOOP, BOOMERANG, RANDOM
    
def insert_pose_keyframe(obj: bpy.types.Object, pose_action: bpy.types.Action, 
                         frame: int, interpolation: str = 'LINEAR') -> None:
    """Insert keyframes from a pose action into the current action at a specific frame"""
    if not pose_action:
        return
    
    # Ensure we have an active action to write to
    if not obj.animation_data:
        obj.animation_data_create()
    
    if not obj.animation_data.action:
        obj.animation_data.action = bpy.data.actions.new(name=config.action_name if 'config' in locals() else "MidiPoseCyclingAnimation")
    
    current_action = obj.animation_data.action
    
    # Copy keyframe values from the pose action
    for fcurve in pose_action.fcurves:
        target_fcurve = current_action.fcurves.find(fcurve.data_path, index=fcurve.array_index)
        if not target_fcurve:
            target_fcurve = current_action.fcurves.new(fcurve.data_path, index=fcurve.array_index)
        
        # Get the value at frame 0 of the pose
        if fcurve.keyframe_points:
            value = fcurve.evaluate(0)
            keyframe = target_fcurve.keyframe_points.insert(frame, value, options={'FAST'})
            keyframe.interpolation = interpolation

def get_next_pose_index(current_index: int, num_poses: int, mode: str, direction: int = 1) -> Tuple[int, int]:
    """Get next pose index based on cycle mode.
    Returns: (next_index, direction)
    """
    if mode == 'RANDOM':
        return random.randint(0, num_poses - 1), direction
    elif mode == 'BOOMERANG':
        next_index = current_index + direction
        if next_index >= num_poses:
            # Hit the end, reverse direction
            direction = -1
            next_index = num_poses - 2 if num_poses > 1 else 0
        elif next_index < 0:
            # Hit the beginning, reverse direction
            direction = 1
            next_index = 1 if num_poses > 1 else 0
        return next_index, direction
    else:  # LOOP (default)
        return (current_index + 1) % num_poses, direction

def render_animation(config: RenderConfig, note_frames: List[int]) -> bool:
    """Render the animation based on MIDI events and poses"""
    
    # Get the active object
    obj = bpy.context.active_object
    if not obj:
        return False
    
    # Get pose actions
    pose_actions = []
    for pose_name in config.poses:
        pose_action = bpy.data.actions.get(pose_name)
        if pose_action:
            pose_actions.append(pose_action)
    
    if not pose_actions or not note_frames:
        return False
    
    # Ensure we have animation data
    if not obj.animation_data:
        obj.animation_data_create()
    
    # Get or create the action with the specified name
    action = bpy.data.actions.get(config.action_name)
    if action:
        # Clear existing keyframes
        action.fcurves.clear()
    else:
        action = bpy.data.actions.new(name=config.action_name)
    
    obj.animation_data.action = action
    
    pose_index = 0
    direction = 1  # For boomerang mode
    frame_count = 0
    
    # Process each MIDI note event
    for i, frame in enumerate(note_frames):
        current_pose = pose_actions[pose_index]
        
        # Insert keyframe at the note time with CONSTANT to hold the pose
        insert_pose_keyframe(obj, current_pose, frame, 'CONSTANT')
        frame_count += 1
        
        # Calculate hold end frame
        hold_end_frame = frame + config.frames_to_hold
        
        # Check if we need to adjust the hold for the next note
        if i < len(note_frames) - 1:
            next_frame = note_frames[i + 1]
            if next_frame > hold_end_frame:
                # Insert keyframe at end of hold with configured interpolation
                insert_pose_keyframe(obj, current_pose, hold_end_frame, config.interpolation_type)
                frame_count += 1
        else:
            # Last note, insert hold end
            insert_pose_keyframe(obj, current_pose, hold_end_frame, config.interpolation_type)
            frame_count += 1
        
        # Get next pose index based on cycle mode
        pose_index, direction = get_next_pose_index(pose_index, len(pose_actions), config.pose_cycle_mode, direction)
    
    # Update scene frame range
    scene = bpy.context.scene
    scene.frame_start = 0
    scene.frame_end = min(hold_end_frame, config.total_frames) if note_frames else config.total_frames
    
    return True

def get_available_poses() -> List[str]:
    """Get list of available pose actions in the project"""
    poses = []
    for action in bpy.data.actions:
        # Filter for likely pose actions (customize this logic as needed)
        if not action.name.startswith("Midi"):
            poses.append(action.name)
    return sorted(poses)

def get_interpolation_types() -> List[Tuple[str, str, str]]:
    """Get available interpolation types for Blender keyframes"""
    return [
        ('CONSTANT', 'Constant', 'No interpolation'),
        ('LINEAR', 'Linear', 'Linear interpolation'),
        ('BEZIER', 'Bezier', 'Smooth Bezier interpolation'),
        ('SINE', 'Sinusoidal', 'Sinusoidal easing'),
        ('QUAD', 'Quadratic', 'Quadratic easing'),
        ('CUBIC', 'Cubic', 'Cubic easing'),
        ('QUART', 'Quartic', 'Quartic easing'),
        ('QUINT', 'Quintic', 'Quintic easing'),
        ('EXPO', 'Exponential', 'Exponential easing'),
        ('CIRC', 'Circular', 'Circular easing'),
        ('BACK', 'Back', 'Back easing'),
        ('BOUNCE', 'Bounce', 'Bounce easing'),
        ('ELASTIC', 'Elastic', 'Elastic easing'),
    ]