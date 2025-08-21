"""
Configuration management for MIDI Pose Cycler
Handles saving and loading animation configurations
"""

import bpy
import json
from typing import Dict, Any, Optional, List, TypedDict


class ConfigData(TypedDict):
    """Type definition for saved configuration data"""
    version: str
    
    # Core settings
    midi_file: str
    action_name: str
    animation_mode: str
    pose_cycle_mode: str
    
    # Timing settings
    frames_to_hold: int
    interpolation_type: str
    bpm: float
    beats_per_bar: int
    use_smart_timing: bool
    midi_start_frame: int
    midi_start_bar: int
    midi_start_beat: int
    midi_length_bars: int
    midi_length_beats: int
    use_frame_limit: bool
    frame_limit: int
    
    # Track selection (multi-track support)
    selected_tracks: List[Dict[str, Any]]  # List of {name, is_dynamic, filter_notes, note_filters}
    
    # Pose selection
    selected_poses: List[str]  # Pose names in order
    pose_order: Dict[str, int]  # Pose name -> order index
    
    # Note configuration
    notes: List[Dict[str, Any]]  # Legacy for single track
    
    # Other settings
    filter_notes: bool
    skip_keyframe_warning: bool
    
    # Dynamic track settings
    dynamic_interval_beats: float
    dynamic_interval_type: str

def get_config_data(props) -> ConfigData:
    """Extract configuration data from properties"""
    config: ConfigData = {
        'version': '0.2.0',  # Updated for multi-track support
        
        # Core settings
        'midi_file': props.midi_file,
        'action_name': props.action_name,
        'animation_mode': props.animation_mode,
        'pose_cycle_mode': props.pose_cycle_mode,
        
        # Timing settings
        'frames_to_hold': props.frames_to_hold,
        'interpolation_type': props.interpolation_type,
        'bpm': props.bpm,
        'beats_per_bar': props.beats_per_bar,
        'use_smart_timing': props.use_smart_timing,
        'midi_start_frame': props.midi_start_frame,
        'midi_start_bar': props.midi_start_bar,
        'midi_start_beat': props.midi_start_beat,
        'midi_length_bars': props.midi_length_bars,
        'midi_length_beats': props.midi_length_beats,
        'use_frame_limit': props.use_frame_limit,
        'frame_limit': props.frame_limit,
        
        # Track selection (multi-track support)
        'selected_tracks': [],
        
        # Pose selection with order
        'selected_poses': [],
        'pose_order': {},
        
        # Legacy single track
        'selected_track': props.selected_track,  # Keep for backwards compat
        'notes': [],
        'filter_notes': props.filter_notes,
        
        # Other settings
        'skip_keyframe_warning': props.skip_keyframe_warning,
        
        # Dynamic track settings
        'dynamic_interval_beats': props.dynamic_interval_beats,
        'dynamic_interval_type': props.dynamic_interval_type,
    }
    
    # Save selected tracks with their note filters
    for track in props.track_items:
        if track.selected:
            track_data = {
                'name': track.name,
                'is_dynamic': track.is_dynamic,
                'filter_notes': track.filter_notes,
                'note_filters': []
            }
            
            # Save note filter settings for this track
            if track.filter_notes:
                for note_filter in track.note_filters:
                    track_data['note_filters'].append({
                        'note_number': note_filter.note_number,
                        'note_name': note_filter.note_name,
                        'selected': note_filter.selected,
                        'nickname': note_filter.nickname
                    })
            
            config['selected_tracks'].append(track_data)
    
    # Save selected poses with order
    selected_poses = [p for p in props.pose_items if p.selected]
    selected_poses.sort(key=lambda p: p.order_index)
    config['selected_poses'] = [p.name for p in selected_poses]
    config['pose_order'] = {p.name: p.order_index for p in props.pose_items}
    
    # Legacy note settings for backwards compatibility
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
        # First, reload MIDI file if needed
        if 'midi_file' in config and config['midi_file']:
            props.midi_file = config['midi_file']
            
            # Auto-reload the MIDI file to populate tracks
            if props.midi_file:
                import os
                if os.path.exists(props.midi_file):
                    # Trigger MIDI reload to populate tracks
                    # We need to manually load the MIDI file as we can't call the operator here
                    from . import midi_core
                    analysis = midi_core.analyze_midi_file(props.midi_file)
                    if analysis:
                        # Populate track list
                        props.track_items.clear()
                        seen_names = set()
                        for track in analysis.tracks:
                            if track.name not in seen_names:
                                item = props.track_items.add()
                                item.name = track.name
                                item.note_count = track.note_count
                                item.track_index = track.index
                                item.selected = False
                                item.is_dynamic = False
                                
                                # Add note filters
                                item.note_filters.clear()
                                for note_num in sorted(track.notes.keys()):
                                    note_filter = item.note_filters.add()
                                    note_filter.note_number = note_num
                                    note_filter.note_name = midi_core.midi_note_to_name(note_num)
                                    note_filter.selected = True
                                
                                item.selected_note_count = len(track.notes)
                                seen_names.add(track.name)
                        
                        # Add dynamic track option
                        dynamic_track = props.track_items.add()
                        dynamic_track.name = "Every X Beats/Bars"
                        dynamic_track.note_count = 0
                        dynamic_track.track_index = -1
                        dynamic_track.selected = False
                        dynamic_track.is_dynamic = True
        
        # Core properties
        if 'action_name' in config:
            props.action_name = config['action_name']
        if 'animation_mode' in config:
            props.animation_mode = config['animation_mode']
        if 'pose_cycle_mode' in config:
            props.pose_cycle_mode = config['pose_cycle_mode']
        
        # Timing properties
        if 'frames_to_hold' in config:
            props.frames_to_hold = config['frames_to_hold']
        if 'interpolation_type' in config:
            props.interpolation_type = config['interpolation_type']
        if 'bpm' in config:
            props.bpm = config['bpm']
        if 'beats_per_bar' in config:
            props.beats_per_bar = config['beats_per_bar']
        if 'use_smart_timing' in config:
            props.use_smart_timing = config['use_smart_timing']
        if 'midi_start_frame' in config:
            props.midi_start_frame = config['midi_start_frame']
        if 'midi_start_bar' in config:
            props.midi_start_bar = config.get('midi_start_bar', 1)
        if 'midi_start_beat' in config:
            props.midi_start_beat = config.get('midi_start_beat', 1)
        if 'midi_length_bars' in config:
            props.midi_length_bars = config.get('midi_length_bars', 0)
        if 'midi_length_beats' in config:
            props.midi_length_beats = config.get('midi_length_beats', 0)
        if 'use_frame_limit' in config:
            props.use_frame_limit = config['use_frame_limit']
        if 'frame_limit' in config:
            props.frame_limit = config['frame_limit']
        
        # Other settings
        if 'filter_notes' in config:
            props.filter_notes = config['filter_notes']
        if 'skip_keyframe_warning' in config:
            props.skip_keyframe_warning = config['skip_keyframe_warning']
        
        # Dynamic track settings
        if 'dynamic_interval_beats' in config:
            props.dynamic_interval_beats = config.get('dynamic_interval_beats', 1.0)
        if 'dynamic_interval_type' in config:
            props.dynamic_interval_type = config.get('dynamic_interval_type', 'BEATS')
        
        # Apply track selection (multi-track)
        if 'selected_tracks' in config:
            # First clear all track selections
            for track in props.track_items:
                track.selected = False
                track.filter_notes = False
            
            # Apply saved track selections
            for saved_track in config['selected_tracks']:
                # Find matching track in current list
                for track in props.track_items:
                    if track.name == saved_track['name']:
                        track.selected = True
                        track.filter_notes = saved_track.get('filter_notes', False)
                        
                        # Apply note filters if present
                        if 'note_filters' in saved_track and track.filter_notes:
                            note_map = {n['note_number']: n for n in saved_track['note_filters']}
                            for note_filter in track.note_filters:
                                if note_filter.note_number in note_map:
                                    note_data = note_map[note_filter.note_number]
                                    note_filter.selected = note_data.get('selected', True)
                                    note_filter.nickname = note_data.get('nickname', '')
                        break
        
        # Legacy single track support
        elif 'selected_track' in config:
            props.selected_track = config['selected_track']
            # Try to select the track if it exists
            for track in props.track_items:
                if track.name == props.selected_track:
                    track.selected = True
                    break
        
        # Apply pose selection and order
        if 'selected_poses' in config:
            selected_poses = set(config['selected_poses'])
            for pose in props.pose_items:
                pose.selected = pose.name in selected_poses
        
        if 'pose_order' in config:
            pose_order = config['pose_order']
            for pose in props.pose_items:
                if pose.name in pose_order:
                    pose.order_index = pose_order[pose.name]
        
        # Legacy note settings (for backwards compatibility)
        if 'notes' in config and props.note_items:
            note_map = {n['note_number']: n for n in config['notes']}
            for note in props.note_items:
                if note.note_number in note_map:
                    note_data = note_map[note.note_number]
                    note.selected = note_data.get('selected', True)
                    note.nickname = note_data.get('nickname', '')
        
        return True
    except Exception as e:
        print(f"Error applying config: {e}")
        import traceback
        traceback.print_exc()
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