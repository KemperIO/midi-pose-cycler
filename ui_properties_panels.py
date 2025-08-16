"""
MIDI Pose Cycler - Properties Panels
Three separate panels for the Properties editor in the custom workspace
"""

import bpy
from bpy.types import Panel
import os

# Base class for workspace-specific panels
class MidiPoseWorkspacePanel:
  bl_space_type = 'PROPERTIES'
  bl_region_type = 'WINDOW'
  bl_context = "scene"
  
  @classmethod
  def poll(cls, context):
    # Only show in MIDI Pose Cycler workspace
    return (context.workspace.name == "MIDI Pose Cycler" or
            context.scene.get('midi_pose_workspace') == "MIDI Pose Cycler")


# MAIN PANEL - Controls and settings
class MIDIPOSE_PT_properties_main(Panel, MidiPoseWorkspacePanel):
  """Main control panel"""
  bl_label = "MIDI Pose Cycler - Controls"
  bl_idname = "MIDIPOSE_PT_properties_main"
  bl_order = 0  # First panel
  
  def draw_header(self, context):
    self.layout.label(text="", icon='PREFERENCES')
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # MIDI File Section
    box = layout.box()
    row = box.row()
    row.label(text="MIDI Input", icon='FILE_SOUND')
    
    if props.midi_file:
      col = box.column()
      col.label(text=f"File: {os.path.basename(props.midi_file)}", icon='FILE_TICK')
      
      row = col.row(align=True)
      row.operator("midipose.load_midi", text="Change File", icon='FILE_FOLDER')
      row.operator("midipose.reload_midi", text="", icon='FILE_REFRESH')
      
      # Show file info
      if props.selected_track:
        info_box = box.box()
        info_box.label(text=f"Track: {props.selected_track}", icon='NLA')
        
        # Count selected notes if filtering
        if props.filter_notes:
          selected_notes = sum(1 for n in props.note_items if n.selected)
          info_box.label(text=f"Notes: {selected_notes} selected", icon='FILTER')
    else:
      box.operator("midipose.load_midi", text="Load MIDI File", icon='FILEBROWSER')
      box.label(text="Or drag from File Browser", icon='INFO')
    
    # Action Settings
    box = layout.box()
    row = box.row()
    row.label(text="Action Settings", icon='ACTION')
    
    col = box.column()
    
    # Action name with warning
    row = col.row(align=True)
    row.label(text="Name:")
    row.prop(props, "action_name", text="")
    
    # Check for existing action
    action = bpy.data.actions.get(props.action_name)
    if action:
      if action.fcurves and any(fc.keyframe_points for fc in action.fcurves):
        col.label(text="⚠️ Action has keyframes!", icon='ERROR')
        col.prop(props, "skip_keyframe_warning", text="Don't warn about overwriting")
    
    col.separator()
    
    # Animation Settings
    row = col.row()
    row.label(text="Cycle Mode:")
    row.prop(props, "pose_cycle_mode", text="")
    
    # Frame settings
    col.separator()
    
    row = col.row()
    row.label(text="Hold Frames:")
    row.prop(props, "frames_to_hold", text="")
    
    row = col.row()
    row.label(text="Interpolation:")
    row.prop(props, "interpolation_type", text="")
    
    # Frame limit
    col.separator()
    row = col.row(align=True)
    row.prop(props, "use_frame_limit", text="Limit Frames")
    if props.use_frame_limit:
      row.prop(props, "frame_limit", text="")
    
    # Info
    info_text = f"Max: {props.frame_limit} frames" if props.use_frame_limit else "Using all MIDI events"
    col.label(text=info_text, icon='INFO')
    col.label(text=f"Project FPS: {scene.render.fps}", icon='TIME')
    
    # Configurations
    box = layout.box()
    row = box.row()
    row.label(text="Configurations", icon='FILE_FOLDER')
    
    col = box.column()
    
    # Current config
    if props.active_config:
      row = col.row()
      row.label(text="Active:")
      row.label(text=props.active_config)
      col.separator()
    
    # Config actions
    row = col.row(align=True)
    row.operator("midipose.save_config", text="Save", icon='FILE_TICK')
    row.operator("midipose.save_config_as", text="Save As", icon='SAVEAS')
    
    row = col.row(align=True)
    row.operator("midipose.load_config", text="Load", icon='FILE_FOLDER')
    if props.active_config:
      row.operator("midipose.delete_config", text="Delete", icon='X')
    
    # Main Generate Button
    layout.separator()
    
    row = layout.row()
    row.scale_y = 2.0
    
    # Enable button only if we have required data
    can_generate = (props.midi_file and 
                   props.selected_track and 
                   any(p.selected for p in props.pose_items))
    
    row.enabled = can_generate
    row.operator("midipose.render_animation", 
                text="GENERATE ANIMATION", 
                icon='PLAY')
    
    if not can_generate:
      if not props.midi_file:
        layout.label(text="Load a MIDI file first", icon='ERROR')
      elif not props.selected_track:
        layout.label(text="Select a MIDI track", icon='ERROR')
      elif not any(p.selected for p in props.pose_items):
        layout.label(text="Select poses to animate", icon='ERROR')


# POSES PANEL - Pose selection and ordering
class MIDIPOSE_PT_properties_poses(Panel, MidiPoseWorkspacePanel):
  """Pose selection panel"""
  bl_label = "Poses"
  bl_idname = "MIDIPOSE_PT_properties_poses"
  bl_order = 1  # Second panel
  
  def draw_header(self, context):
    row = self.layout.row(align=True)
    row.label(text="", icon='ARMATURE_DATA')
    row.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH', emboss=False)
  
  def draw(self, context):
    layout = self.layout
    props = context.scene.midi_pose_props
    
    if not props.pose_items:
      box = layout.box()
      box.label(text="No poses found in project", icon='INFO')
      box.operator("midipose.refresh_poses", text="Scan for Pose Actions", icon='VIEWZOOM')
      box.separator()
      box.label(text="Tips:", icon='QUESTION')
      box.label(text="• Create actions with poses")
      box.label(text="• Name them descriptively")
      box.label(text="• Drag from Asset Browser")
      return
    
    # Quick selection tools
    row = layout.row(align=True)
    row.operator("midipose.select_all_poses", text="All")
    row.operator("midipose.deselect_all_poses", text="None")
    row.operator("midipose.invert_pose_selection", text="Invert")
    
    layout.separator()
    
    # Pose list with ordering
    box = layout.box()
    
    selected_poses = [p for p in props.pose_items if p.selected]
    
    # Show selected poses in order
    if selected_poses:
      box.label(text=f"Selected Poses ({len(selected_poses)}):", icon='CHECKBOX_HLT')
      
      for i, pose in enumerate(props.pose_items):
        if not pose.selected:
          continue
        
        row = box.row(align=True)
        
        # Order number
        order = selected_poses.index(pose) + 1
        row.label(text=f"#{order}")
        
        # Pose name
        row.prop(pose, "selected", text="", icon='CHECKBOX_HLT')
        
        # Check if action exists
        action = bpy.data.actions.get(pose.name)
        icon = 'ACTION' if action else 'POSE_HLT'
        
        row.label(text=pose.name, icon=icon)
        
        # Move up/down buttons could go here
      
      box.separator()
    
    # Unselected poses
    unselected = [p for p in props.pose_items if not p.selected]
    if unselected:
      box.label(text=f"Available Poses ({len(unselected)}):", icon='CHECKBOX_DEHLT')
      
      for pose in unselected:
        row = box.row(align=True)
        
        # Checkbox
        row.prop(pose, "selected", text="", icon='CHECKBOX_DEHLT')
        
        # Check if action exists
        action = bpy.data.actions.get(pose.name)
        icon = 'ACTION' if action else 'POSE_HLT'
        
        # Name
        row.label(text=pose.name, icon=icon)
    
    # Summary
    layout.separator()
    
    col = layout.column()
    col.label(text=f"Total: {len(props.pose_items)} poses")
    col.label(text=f"Selected: {len(selected_poses)} poses")
    
    if selected_poses:
      col.separator()
      col.label(text=f"Cycle Mode: {props.pose_cycle_mode}", icon='RECOVER_LAST')
      
      # Cycle explanation
      info_box = col.box()
      if props.pose_cycle_mode == 'LOOP':
        info_box.label(text="Poses will cycle in order", icon='LOOP_FORWARDS')
      elif props.pose_cycle_mode == 'BOOMERANG':
        info_box.label(text="Forward then backward", icon='LOOP_BACK')
      elif props.pose_cycle_mode == 'RANDOM':
        info_box.label(text="Random pose selection", icon='RANDOMIZE')


# MIDI PANEL - Track selection and note filtering
class MIDIPOSE_PT_properties_midi(Panel, MidiPoseWorkspacePanel):
  """MIDI data panel"""
  bl_label = "MIDI Data"
  bl_idname = "MIDIPOSE_PT_properties_midi"
  bl_order = 2  # Third panel
  
  def draw_header(self, context):
    self.layout.label(text="", icon='NLA')
  
  def draw(self, context):
    layout = self.layout
    props = context.scene.midi_pose_props
    
    if not props.midi_file:
      box = layout.box()
      box.label(text="No MIDI file loaded", icon='INFO')
      box.operator("midipose.load_midi", text="Load MIDI File", icon='FILE_FOLDER')
      return
    
    # File info
    box = layout.box()
    box.label(text="MIDI File", icon='FILE_SOUND')
    box.label(text=os.path.basename(props.midi_file))
    
    # Track Selection
    box = layout.box()
    box.label(text="MIDI Tracks", icon='NLA_PUSHDOWN')
    
    if not props.track_items:
      box.label(text="No tracks found", icon='ERROR')
      box.operator("midipose.reload_midi", text="Reload File", icon='FILE_REFRESH')
      return
    
    # List tracks
    for track in props.track_items:
      row = box.row(align=True)
      
      is_selected = track.name == props.selected_track
      
      # Radio button style
      icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
      op = row.operator("midipose.select_track", 
                       text="",
                       icon=icon,
                       emboss=False)
      op.track_name = track.name
      
      # Track info
      sub_row = row.row()
      sub_row.active = is_selected
      sub_row.alignment = 'LEFT'
      sub_row.label(text=f"{track.name}")
      
      # Note count
      row.label(text=f"{track.note_count} notes")
    
    # Selected track info
    if props.selected_track:
      info_box = box.box()
      info_box.label(text=f"Active: {props.selected_track}", icon='CHECKMARK')
      
      # Track statistics
      if props.note_items:
        total_notes = sum(n.count for n in props.note_items)
        unique_notes = len(props.note_items)
        info_box.label(text=f"Total events: {total_notes}")
        info_box.label(text=f"Unique notes: {unique_notes}")
    
    # Note Filtering
    if props.selected_track and props.note_items:
      layout.separator()
      
      box = layout.box()
      row = box.row()
      row.prop(props, "filter_notes", text="Filter Specific Notes")
      
      if props.filter_notes:
        row.label(text="", icon='FILTER')
        
        # Note list with nicknames
        note_box = box.box()
        
        # Header
        row = note_box.row()
        row.label(text="Note")
        row.label(text="Nickname")
        row.label(text="Count")
        
        note_box.separator()
        
        # List notes (limit display for performance)
        display_limit = 20
        for i, note in enumerate(props.note_items):
          if i >= display_limit:
            note_box.label(text=f"... and {len(props.note_items) - display_limit} more")
            break
          
          row = note_box.row(align=True)
          
          # Selection checkbox
          row.prop(note, "selected", text="")
          
          # Note name
          sub = row.row()
          sub.scale_x = 0.3
          sub.label(text=note.note_name)
          
          # Nickname field
          row.prop(note, "nickname", text="")
          
          # Count
          sub = row.row()
          sub.scale_x = 0.3
          sub.label(text=str(note.count))
        
        # Summary of nicknamed notes
        nicknamed_notes = [(n.note_name, n.nickname) 
                          for n in props.note_items 
                          if n.nickname and n.selected]
        
        if nicknamed_notes:
          box.separator()
          alias_box = box.box()
          alias_box.label(text="Note Aliases:", icon='INFO')
          
          for note_name, nickname in nicknamed_notes[:10]:
            row = alias_box.row()
            row.label(text=f"{note_name} → {nickname}")
          
          if len(nicknamed_notes) > 10:
            alias_box.label(text=f"... and {len(nicknamed_notes) - 10} more")
        
        # Selected count
        selected_count = sum(1 for n in props.note_items if n.selected)
        box.label(text=f"Using {selected_count} of {len(props.note_items)} notes")
      else:
        box.label(text="Using all notes from track", icon='CHECKBOX_HLT')


# Registration
classes = [
  MIDIPOSE_PT_properties_main,
  MIDIPOSE_PT_properties_poses,
  MIDIPOSE_PT_properties_midi,
]

def register():
  for cls in classes:
    bpy.utils.register_class(cls)

def unregister():
  for cls in reversed(classes):
    bpy.utils.unregister_class(cls)