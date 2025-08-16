"""
Configuration management for MIDI Pose Cycler
Handles saving and loading animation configurations
"""

import bpy
import json
from typing import Dict, Any, Optional

def get_config_data(props) -> Dict[str, Any]:
  """Extract configuration data from properties"""
  config = {
    'version': '0.1.0',
    'midi_file': props.midi_file,
    'selected_track': props.selected_track,
    'action_name': props.action_name,
    'pose_cycle_mode': props.pose_cycle_mode,
    'frames_to_hold': props.frames_to_hold,
    'interpolation_type': props.interpolation_type,
    'use_frame_limit': props.use_frame_limit,
    'frame_limit': props.frame_limit,
    'filter_notes': props.filter_notes,
    'skip_keyframe_warning': props.skip_keyframe_warning,
    
    # Selected poses
    'selected_poses': [p.name for p in props.pose_items if p.selected],
    
    # Note configuration (including nicknames)
    'notes': []
  }
  
  # Save note settings
  for note in props.note_items:
    config['notes'].append({
      'note_number': note.note_number,
      'note_name': note.note_name,
      'selected': note.selected,
      'nickname': note.nickname
    })
  
  return config

def apply_config_data(props, config: Dict[str, Any]) -> bool:
  """Apply configuration data to properties"""
  try:
    # Basic properties
    if 'midi_file' in config:
      props.midi_file = config['midi_file']
    if 'selected_track' in config:
      props.selected_track = config['selected_track']
    if 'action_name' in config:
      props.action_name = config['action_name']
    if 'pose_cycle_mode' in config:
      props.pose_cycle_mode = config['pose_cycle_mode']
    if 'frames_to_hold' in config:
      props.frames_to_hold = config['frames_to_hold']
    if 'interpolation_type' in config:
      props.interpolation_type = config['interpolation_type']
    if 'use_frame_limit' in config:
      props.use_frame_limit = config['use_frame_limit']
    if 'frame_limit' in config:
      props.frame_limit = config['frame_limit']
    if 'filter_notes' in config:
      props.filter_notes = config['filter_notes']
    if 'skip_keyframe_warning' in config:
      props.skip_keyframe_warning = config['skip_keyframe_warning']
    
    # Selected poses
    if 'selected_poses' in config:
      selected_poses = set(config['selected_poses'])
      for pose in props.pose_items:
        pose.selected = pose.name in selected_poses
    
    # Note settings with nicknames
    if 'notes' in config:
      note_map = {n['note_number']: n for n in config['notes']}
      for note in props.note_items:
        if note.note_number in note_map:
          note_data = note_map[note.note_number]
          note.selected = note_data.get('selected', True)
          note.nickname = note_data.get('nickname', '')
    
    return True
  except Exception as e:
    print(f"Error applying config: {e}")
    return False

def save_config_to_scene(config_name: str, props) -> bool:
  """Save configuration to scene custom properties"""
  try:
    scene = bpy.context.scene
    
    # Create configs dict if it doesn't exist
    if 'midi_pose_configs' not in scene:
      scene['midi_pose_configs'] = {}
    
    configs = scene['midi_pose_configs'].to_dict() if hasattr(scene['midi_pose_configs'], 'to_dict') else {}
    
    # Save the config
    configs[config_name] = get_config_data(props)
    
    # Store back as JSON string (Blender custom props limitation)
    scene['midi_pose_configs'] = json.dumps(configs)
    
    # Update active config name
    props.active_config = config_name
    
    return True
  except Exception as e:
    print(f"Error saving config: {e}")
    return False

def load_config_from_scene(config_name: str, props) -> bool:
  """Load configuration from scene custom properties"""
  try:
    scene = bpy.context.scene
    
    if 'midi_pose_configs' not in scene:
      return False
    
    # Parse JSON string
    configs = json.loads(scene['midi_pose_configs'])
    
    if config_name not in configs:
      return False
    
    config = configs[config_name]
    apply_config_data(props, config)
    
    # Update active config name
    props.active_config = config_name
    
    return True
  except Exception as e:
    print(f"Error loading config: {e}")
    return False

def delete_config_from_scene(config_name: str) -> bool:
  """Delete configuration from scene"""
  try:
    scene = bpy.context.scene
    
    if 'midi_pose_configs' not in scene:
      return False
    
    configs = json.loads(scene['midi_pose_configs'])
    
    if config_name in configs:
      del configs[config_name]
      scene['midi_pose_configs'] = json.dumps(configs)
      return True
    
    return False
  except Exception as e:
    print(f"Error deleting config: {e}")
    return False

def get_available_configs() -> list:
  """Get list of available configuration names"""
  try:
    scene = bpy.context.scene
    
    if 'midi_pose_configs' not in scene:
      return []
    
    configs = json.loads(scene['midi_pose_configs'])
    return list(configs.keys())
  except:
    return []