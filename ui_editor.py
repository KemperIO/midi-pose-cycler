"""
MIDI Pose Cycler - Editor-Style UI
Maximizes use of editor space with proper regions
"""

import bpy
from bpy.types import Panel, Header, Menu, UIList
import os

# Custom draw function for maximizing space usage
def draw_panel_no_header(self, context):
  """Draw panel without header to save space"""
  self.layout.label(text="")


class MIDIPOSE_PT_editor_main(Panel):
  """Main editor panel taking full advantage of space"""
  bl_label = "MIDI Pose Cycler Editor"
  bl_idname = "MIDIPOSE_PT_editor_main"
  bl_space_type = 'NODE_EDITOR'  # Use Node Editor as base
  bl_region_type = 'UI'
  bl_category = "MIDI Pose"
  bl_options = {'HIDE_HEADER'}
  
  @classmethod
  def poll(cls, context):
    # Show when in a specific node tree context
    return True
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # Use full width
    layout.use_property_split = False
    layout.use_property_decorate = False
    
    # Create main row for three columns
    main_row = layout.row()
    main_row.alignment = 'EXPAND'
    
    # Determine layout based on region width
    region_width = context.region.width
    use_columns = region_width > 600
    
    if use_columns:
      # Three column layout
      col_main = main_row.column()
      col_main.scale_x = 1.0
      
      col_poses = main_row.column()
      col_poses.scale_x = 1.2
      
      col_midi = main_row.column()
      col_midi.scale_x = 1.0
    else:
      # Single column for narrow views
      col_main = layout.column()
      col_poses = layout.column()
      col_midi = layout.column()
    
    # MAIN COLUMN - Controls
    self.draw_main_column(col_main, context)
    
    # POSES COLUMN - Pose Selection
    self.draw_poses_column(col_poses, context)
    
    # MIDI COLUMN - Track and Note Data
    self.draw_midi_column(col_midi, context)
  
  def draw_main_column(self, col, context):
    """Main control column"""
    scene = context.scene
    props = scene.midi_pose_props
    
    # Title
    header_row = col.row()
    header_row.scale_y = 1.5
    header_row.label(text="CONTROLS", icon='SETTINGS')
    
    col.separator()
    
    # MIDI File Section
    box = col.box()
    box.label(text="MIDI File", icon='FILE_SOUND')
    
    if props.midi_file:
      box.label(text=os.path.basename(props.midi_file), icon='FILE_TICK')
      row = box.row(align=True)
      row.operator("midipose.load_midi", text="Change")
      row.operator("midipose.reload_midi", text="Reload")
    else:
      box.operator("midipose.load_midi", text="Load MIDI File", icon='FILEBROWSER')
    
    # Action Settings
    box = col.box()
    box.label(text="Action", icon='ACTION')
    
    row = box.row(align=True)
    row.prop(props, "action_name", text="")
    action = bpy.data.actions.get(props.action_name)
    if action and action.fcurves:
      has_keys = any(fc.keyframe_points for fc in action.fcurves)
      if has_keys:
        row.label(text="Has Keys!", icon='ERROR')
    
    # Animation Settings
    box = col.box()
    box.label(text="Animation", icon='ANIM')
    
    row = box.row()
    row.prop(props, "pose_cycle_mode", text="")
    
    row = box.row(align=True)
    row.label(text="Hold:")
    row.prop(props, "frames_to_hold", text="")
    
    row = box.row(align=True)
    row.label(text="Blend:")
    row.prop(props, "interpolation_type", text="")
    
    # Frame Limit
    row = box.row(align=True)
    row.prop(props, "use_frame_limit", text="Limit")
    if props.use_frame_limit:
      row.prop(props, "frame_limit", text="")
    
    box.label(text=f"FPS: {scene.render.fps}", icon='TIME')
    
    # Configurations
    box = col.box()
    box.label(text="Configurations", icon='FILE_FOLDER')
    
    row = box.row(align=True)
    row.prop(props, "active_config", text="")
    row.operator("midipose.save_config", text="", icon='FILE_TICK')
    
    row = box.row(align=True)
    row.operator("midipose.save_config_as", text="Save As")
    row.operator("midipose.load_config", text="Load")
    row.operator("midipose.delete_config", text="", icon='X')
    
    # Generate Button
    col.separator()
    row = col.row()
    row.scale_y = 2.5
    row.operator("midipose.render_animation", 
                text="GENERATE ANIMATION", 
                icon='PLAY')
  
  def draw_poses_column(self, col, context):
    """Poses selection column"""
    props = context.scene.midi_pose_props
    
    # Title
    header_row = col.row()
    header_row.scale_y = 1.5
    header_row.label(text="POSES", icon='ARMATURE_DATA')
    header_row.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH')
    
    col.separator()
    
    if not props.pose_items:
      box = col.box()
      box.label(text="No poses found", icon='INFO')
      box.operator("midipose.refresh_poses", text="Scan for Poses")
      return
    
    # Quick select buttons
    row = col.row(align=True)
    row.operator("midipose.select_all_poses", text="All")
    row.operator("midipose.deselect_all_poses", text="None")
    row.operator("midipose.invert_pose_selection", text="Invert")
    
    # Pose grid/list
    box = col.box()
    
    # Calculate grid layout
    num_poses = len(props.pose_items)
    cols_count = 2 if context.region.width > 400 else 1
    
    pose_idx = 0
    while pose_idx < num_poses:
      row = box.row(align=True)
      
      for c in range(cols_count):
        if pose_idx >= num_poses:
          break
        
        pose = props.pose_items[pose_idx]
        
        # Create a sub-row for each pose
        sub = row.row(align=True)
        sub.scale_x = 1.0 / cols_count
        
        # Check if action exists
        action = bpy.data.actions.get(pose.name)
        icon = 'ACTION' if action else 'POSE_HLT'
        
        # Selection toggle
        sub.prop(pose, "selected", text="", icon=icon, emboss=True)
        
        # Name (truncate if needed)
        name_display = pose.name[:15] + "..." if len(pose.name) > 15 else pose.name
        text_row = sub.row()
        text_row.active = pose.selected
        text_row.label(text=name_display)
        
        # Order number
        if pose.selected:
          selected_poses = [p for p in props.pose_items if p.selected]
          order = selected_poses.index(pose) + 1
          sub.label(text=f"#{order}")
        
        pose_idx += 1
    
    # Summary
    selected_count = sum(1 for p in props.pose_items if p.selected)
    col.label(text=f"Selected: {selected_count} of {num_poses} poses")
    
    if selected_count > 0:
      col.label(text=f"Cycle Mode: {props.pose_cycle_mode}", icon='RECOVER_LAST')
  
  def draw_midi_column(self, col, context):
    """MIDI data column"""
    props = context.scene.midi_pose_props
    
    # Title
    header_row = col.row()
    header_row.scale_y = 1.5
    header_row.label(text="MIDI DATA", icon='NLA')
    
    col.separator()
    
    if not props.midi_file:
      box = col.box()
      box.label(text="No MIDI file loaded", icon='INFO')
      return
    
    # Track Selection
    box = col.box()
    box.label(text="Tracks", icon='NLA_PUSHDOWN')
    
    if props.track_items:
      for track in props.track_items:
        row = box.row(align=True)
        is_selected = track.name == props.selected_track
        
        # Radio button style selection
        icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
        op = row.operator("midipose.select_track",
                         text="",
                         icon=icon,
                         emboss=False)
        op.track_name = track.name
        
        # Track info
        sub = row.row()
        sub.active = is_selected
        sub.label(text=f"{track.name}")
        sub.label(text=f"[{track.note_count}]")
      
      if props.selected_track:
        box.separator()
        box.label(text=f"Active: {props.selected_track}", icon='CHECKMARK')
    else:
      box.label(text="No tracks with notes found")
    
    # Note Filtering
    if props.selected_track and props.note_items:
      col.separator()
      
      box = col.box()
      row = box.row()
      row.prop(props, "filter_notes", text="Filter Notes")
      row.label(text="", icon='FILTER' if props.filter_notes else 'NONE')
      
      if props.filter_notes:
        # Note list in compact format
        note_box = box.box()
        
        # Column headers
        row = note_box.row()
        row.label(text="Note")
        row.label(text="Nickname")
        row.label(text="Count")
        
        note_box.separator()
        
        # Note items
        for note in props.note_items:
          row = note_box.row(align=True)
          
          # Selection
          row.prop(note, "selected", text="")
          
          # Note name
          row.label(text=note.note_name)
          
          # Nickname field
          row.prop(note, "nickname", text="")
          
          # Count
          row.label(text=str(note.count))
        
        # Summary of nicknamed notes
        nicknamed = [(n.note_name, n.nickname) 
                     for n in props.note_items 
                     if n.nickname and n.selected]
        
        if nicknamed:
          col.separator()
          sum_box = col.box()
          sum_box.label(text="Named Notes:", icon='INFO')
          for note_name, nickname in nicknamed:
            sum_box.label(text=f"  {note_name} = {nickname}")
      else:
        box.label(text="Using all notes", icon='CHECKBOX_HLT')


class MIDIPOSE_PT_editor_header(Header):
  """Header for MIDI Pose editor context"""
  bl_space_type = 'NODE_EDITOR'
  
  def draw(self, context):
    layout = self.layout
    props = context.scene.midi_pose_props
    
    layout.template_header()
    
    # Quick status
    if props.midi_file:
      layout.label(text=f"MIDI: {os.path.basename(props.midi_file)}")
    
    if props.selected_track:
      layout.label(text=f"Track: {props.selected_track}")
    
    selected_poses = sum(1 for p in props.pose_items if p.selected)
    if selected_poses:
      layout.label(text=f"Poses: {selected_poses}")
    
    layout.separator_spacer()
    
    # Quick generate button
    if props.midi_file and props.selected_track and selected_poses:
      layout.operator("midipose.render_animation", 
                     text="Generate", 
                     icon='PLAY')