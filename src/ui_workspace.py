"""
MIDI Pose Cycler - Enhanced Workspace UI
Provides a multi-column workspace layout for MIDI pose animation
"""

import bpy
from bpy.types import Panel, UIList
import os

# Base class for MIDI Pose panels
class MidiPosePanel:
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "MIDI Pose"
  
  @classmethod
  def poll(cls, context):
    return True


class MIDIPOSE_PT_workspace_main(Panel, MidiPosePanel):
  """Main control panel with enhanced layout"""
  bl_label = "MIDI Pose Cycler"
  bl_idname = "MIDIPOSE_PT_workspace_main"
  
  def draw_header(self, context):
    layout = self.layout
    props = context.scene.midi_pose_props
    if props.midi_file:
      layout.label(text="", icon='FILE_TICK')
    else:
      layout.label(text="", icon='FILE_SOUND')
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # Determine if we have enough width for multi-column
    width = context.region.width
    use_columns = width > 500
    
    # Main container
    if use_columns:
      main_row = layout.row()
      # Create three columns
      col_left = main_row.column()
      col_left.scale_x = 1.2
      col_mid = main_row.column()
      col_right = main_row.column()
    else:
      # Single column for narrow layouts
      col_left = layout.column()
      col_mid = layout.column() 
      col_right = layout.column()
    
    # LEFT COLUMN - Main Controls
    self.draw_main_controls(col_left, context)
    
    # MIDDLE COLUMN - Poses
    self.draw_poses_section(col_mid, context)
    
    # RIGHT COLUMN - MIDI Data
    self.draw_midi_section(col_right, context)
    
    # Bottom section - Generate button
    layout.separator()
    row = layout.row()
    row.scale_y = 2.0
    row.operator("midipose.render_animation", text="GENERATE ANIMATION", icon='PLAY')
  
  def draw_main_controls(self, layout, context):
    """Draw main control section"""
    scene = context.scene
    props = scene.midi_pose_props
    
    # MIDI File
    box = layout.box()
    col = box.column()
    col.label(text="MIDI Input", icon='FILE_SOUND')
    
    if props.midi_file:
      col.label(text=f"File: {os.path.basename(props.midi_file)}")
      row = col.row(align=True)
      row.operator("midipose.load_midi", text="Change", icon='FILE_FOLDER')
      row.operator("midipose.reload_midi", text="Reload", icon='FILE_REFRESH')
    else:
      col.operator("midipose.load_midi", text="Load MIDI File", icon='FILE_FOLDER')
    
    # Animation Settings
    box = layout.box()
    col = box.column()
    col.label(text="Animation", icon='SETTINGS')
    
    # Action name with warning indicator
    row = col.row(align=True)
    row.prop(props, "action_name", text="Action")
    if bpy.data.actions.get(props.action_name):
      if any(fc.keyframe_points for fc in bpy.data.actions[props.action_name].fcurves):
        row.label(text="", icon='ERROR')
    
    col.separator()
    
    # Cycle Mode
    col.prop(props, "pose_cycle_mode", text="Cycle")
    
    # Frame settings
    col.prop(props, "frames_to_hold", text="Hold")
    col.prop(props, "interpolation_type", text="Interp")
    
    # Frame limit
    row = col.row(align=True)
    row.prop(props, "use_frame_limit", text="")
    sub = row.row()
    sub.active = props.use_frame_limit
    sub.prop(props, "frame_limit", text="Limit")
    
    if props.use_frame_limit:
      col.label(text=f"Cap at {props.frame_limit} frames", icon='INFO')
    else:
      col.label(text="Use all MIDI events", icon='INFO')
    
    col.label(text=f"FPS: {scene.render.fps}")
    
    # Config Management  
    box = layout.box()
    col = box.column()
    col.label(text="Configs", icon='FILE_FOLDER')
    
    col.prop(props, "active_config", text="")
    
    row = col.row(align=True)
    row.operator("midipose.save_config", text="Save")
    row.operator("midipose.save_config_as", text="Save As")
    
    row = col.row(align=True)
    row.operator("midipose.load_config", text="Load")
    row.operator("midipose.delete_config", text="Delete")
  
  def draw_poses_section(self, layout, context):
    """Draw poses selection section"""
    props = context.scene.midi_pose_props
    
    box = layout.box()
    row = box.row()
    row.label(text="Poses", icon='ARMATURE_DATA')
    row.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH')
    
    if props.pose_items:
      # Show pose list with selection
      for i, pose in enumerate(props.pose_items):
        row = box.row(align=True)
        
        # Try to get action for icon
        action = bpy.data.actions.get(pose.name)
        icon = 'ACTION' if action else 'POSE_HLT'
        
        # Selection checkbox
        row.prop(pose, "selected", text="", icon=icon)
        
        # Pose name
        sub = row.row()
        sub.active = pose.selected
        sub.label(text=pose.name)
        
        # Show order number if selected
        if pose.selected:
          selected_poses = [p for p in props.pose_items if p.selected]
          order = selected_poses.index(pose) + 1 if pose in selected_poses else 0
          if order:
            row.label(text=f"#{order}")
      
      # Stats and actions
      selected_count = sum(1 for p in props.pose_items if p.selected)
      box.label(text=f"Selected: {selected_count}/{len(props.pose_items)}")
      
      row = box.row(align=True)
      row.operator("midipose.select_all_poses", text="All")
      row.operator("midipose.deselect_all_poses", text="None") 
      row.operator("midipose.invert_pose_selection", text="Invert")
    else:
      box.label(text="No poses found")
      box.operator("midipose.refresh_poses", text="Scan for Poses")
  
  def draw_midi_section(self, layout, context):
    """Draw MIDI data section"""
    props = context.scene.midi_pose_props
    
    if not props.midi_file:
      box = layout.box()
      box.label(text="MIDI Data", icon='NLA')
      box.label(text="No MIDI loaded", icon='INFO')
      return
    
    # Track Selection
    box = layout.box()
    box.label(text="MIDI Tracks", icon='NLA')
    
    if props.track_items:
      for track in props.track_items:
        row = box.row(align=True)
        is_selected = track.name == props.selected_track
        
        icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
        op = row.operator("midipose.select_track",
                         text=track.name,
                         icon=icon,
                         depress=is_selected)
        op.track_name = track.name
        row.label(text=f"{track.note_count}")
      
      if props.selected_track:
        box.label(text=f"Active: {props.selected_track}", icon='CHECKMARK')
    else:
      box.label(text="No tracks found")
    
    # Note Filter
    if props.selected_track and props.note_items:
      box = layout.box()
      row = box.row()
      row.prop(props, "filter_notes", text="Filter Notes")
      
      if props.filter_notes:
        # Note list with nicknames
        for note in props.note_items:
          row = box.row(align=True)
          row.prop(note, "selected", text="")
          
          # Note display
          col = row.column()
          col.scale_x = 0.5
          col.label(text=note.note_name)
          
          # Nickname
          row.prop(note, "nickname", text="")
          
          # Count
          col = row.column()
          col.scale_x = 0.3
          col.label(text=f"({note.count})")
        
        # Show notes with nicknames
        nicknamed_notes = [n for n in props.note_items if n.nickname and n.selected]
        if nicknamed_notes:
          box.separator()
          for note in nicknamed_notes:
            box.label(text=f"  {note.note_name} = {note.nickname}", icon='FORWARD')
      else:
        box.label(text="All notes will be used", icon='INFO')


class MIDIPOSE_UL_poses_grid(UIList):
  """UIList for pose selection in grid layout"""
  
  def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
    if self.layout_type in {'DEFAULT', 'COMPACT'}:
      action = bpy.data.actions.get(item.name)
      
      # Try to show preview if available
      if action and action.asset_data:
        icon_value = 0
        # TODO: Get actual preview icon_id if available
        if hasattr(action.asset_data, 'preview') and action.asset_data.preview:
          # This would need custom icon loading
          pass
      
      icon = 'ACTION' if action else 'POSE_HLT'
      
      row = layout.row(align=True)
      row.prop(item, "selected", text="", icon=icon, emboss=False)
      row.label(text=item.name)
      
      if item.selected:
        selected_poses = [p for p in data.pose_items if p.selected]
        order = selected_poses.index(item) + 1 if item in selected_poses else 0
        if order:
          row.label(text=f"#{order}")
    
    elif self.layout_type == 'GRID':
      layout.alignment = 'CENTER'
      layout.prop(item, "selected", text="", icon='POSE_HLT', emboss=False)
      layout.label(text=item.name[:8])  # Truncate for grid