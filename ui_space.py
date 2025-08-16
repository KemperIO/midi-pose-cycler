"""
MIDI Pose Cycler - Full SpaceType UI
Provides a dedicated workspace for MIDI pose animation
"""

import bpy
from bpy.types import Header, Panel, UIList
import os

class MIDIPOSE_HT_header(Header):
  """Header for MIDI Pose Cycler Space"""
  bl_space_type = 'VIEW_3D'
  
  @classmethod
  def poll(cls, context):
    # Show in all VIEW_3D spaces for now
    return True
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # Always show MIDI Pose controls in header
    if True:  # Was: context.area.ui_type == 'MIDIPOSE':
      row = layout.row(align=True)
      row.label(text="MIDI Pose Cycler", icon='FILE_SOUND')
      
      # Quick actions
      row = layout.row(align=True)
      row.separator()
      
      if props.midi_file:
        filename = os.path.basename(props.midi_file)
        row.label(text=f"File: {filename}")
        row.operator("midipose.reload_midi", text="", icon='FILE_REFRESH')
      else:
        row.operator("midipose.load_midi", text="Load MIDI", icon='FILE_FOLDER')
      
      # Config management
      row = layout.row(align=True)
      row.separator()
      row.prop(props, "active_config", text="")
      row.operator("midipose.save_config", text="", icon='FILE_TICK')
      row.operator("midipose.load_config", text="", icon='FOLDER_REDIRECT')
      
      # Main action
      row = layout.row(align=True)
      row.separator()
      row.scale_x = 1.5
      if props.active_config:
        row.operator("midipose.render_animation", text="Run/Rerun", icon='PLAY')
      else:
        row.operator("midipose.render_animation", text="Generate", icon='PLAY')


class MIDIPOSE_PT_main_column(Panel):
  """Main control column"""
  bl_label = "Controls"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "MIDI Pose"
  bl_options = {'DEFAULT_CLOSED'}
  
  @classmethod
  def poll(cls, context):
    return context.area.ui_type == 'MIDIPOSE'
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # Check for narrow layout
    is_narrow = context.region.width < 400
    
    # MIDI File Section
    box = layout.box()
    col = box.column()
    col.label(text="MIDI Input", icon='FILE_SOUND')
    
    if props.midi_file:
      col.label(text=f"File: {os.path.basename(props.midi_file)}")
      row = col.row(align=True)
      row.operator("midipose.load_midi", text="Change File", icon='FILE_FOLDER')
      row.operator("midipose.reload_midi", text="Reload", icon='FILE_REFRESH')
    else:
      col.operator("midipose.load_midi", text="Load MIDI File", icon='FILE_FOLDER')
    
    # Animation Settings
    box = layout.box()
    col = box.column()
    col.label(text="Animation Settings", icon='SETTINGS')
    
    # Action name
    row = col.row()
    row.prop(props, "action_name")
    if bpy.data.actions.get(props.action_name):
      row.label(text="", icon='ERROR')  # Show warning if exists
    
    # Pose Cycle Mode
    col.prop(props, "pose_cycle_mode")
    
    # Frame settings
    col.separator()
    col.prop(props, "frames_to_hold")
    col.prop(props, "interpolation_type")
    
    # Frame limit
    row = col.row(align=True)
    row.prop(props, "use_frame_limit", text="")
    sub = row.row()
    sub.active = props.use_frame_limit
    sub.prop(props, "frame_limit", text="Frame Limit")
    
    if props.use_frame_limit:
      col.label(text="Animation will be capped at this frame count", icon='INFO')
    else:
      col.label(text="Animation uses all MIDI events", icon='INFO')
    
    col.label(text=f"Project FPS: {scene.render.fps}")
    
    # Config Management
    box = layout.box()
    col = box.column()
    col.label(text="Configurations", icon='FILE_FOLDER')
    
    row = col.row()
    row.prop(props, "active_config", text="")
    
    row = col.row(align=True)
    row.operator("midipose.save_config", text="Save Config")
    row.operator("midipose.save_config_as", text="Save As...")
    
    row = col.row(align=True)
    row.operator("midipose.load_config", text="Load Config")
    row.operator("midipose.delete_config", text="Delete")
    
    # Generate button
    layout.separator()
    row = layout.row()
    row.scale_y = 2.0
    row.operator("midipose.render_animation", text="GENERATE ANIMATION", icon='PLAY')


class MIDIPOSE_UL_poses(UIList):
  """UIList for pose selection with preview images"""
  
  def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
    if self.layout_type in {'DEFAULT', 'COMPACT'}:
      # Try to get preview image
      action = bpy.data.actions.get(item.name)
      preview_icon = 'ACTION' if action else 'POSE_HLT'
      
      # Check if we have an asset preview
      if action and action.asset_data and action.asset_data.preview:
        # TODO: Display actual preview image
        preview_icon = 'IMAGE_DATA'
      
      row = layout.row(align=True)
      row.prop(item, "selected", text="", icon=preview_icon, emboss=False)
      row.label(text=item.name)
      
      # Show order number if selected
      if item.selected:
        selected_poses = [p for p in data.pose_items if p.selected]
        index = selected_poses.index(item) + 1 if item in selected_poses else 0
        if index:
          row.label(text=f"#{index}")
    
    elif self.layout_type == 'GRID':
      layout.alignment = 'CENTER'
      layout.prop(item, "selected", text="", icon='POSE_HLT', emboss=False)


class MIDIPOSE_PT_poses_column(Panel):
  """Poses selection column"""
  bl_label = "Poses"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "Poses"
  bl_options = {'DEFAULT_CLOSED'}
  
  @classmethod
  def poll(cls, context):
    return context.area.ui_type == 'MIDIPOSE'
  
  def draw(self, context):
    layout = self.layout
    props = context.scene.midi_pose_props
    
    # Header
    row = layout.row()
    row.label(text="Available Poses", icon='ARMATURE_DATA')
    row.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH')
    
    # Pose list
    if props.pose_items:
      # Use UIList for better display
      row = layout.row()
      row.template_list(
        "MIDIPOSE_UL_poses", "",
        props, "pose_items",
        props, "active_pose_index",
        rows=10
      )
      
      # Selection info
      selected_count = sum(1 for p in props.pose_items if p.selected)
      layout.label(text=f"Selected: {selected_count} poses")
      
      if selected_count > 0:
        layout.label(text="Poses will cycle in order", icon='INFO')
      
      # Quick actions
      row = layout.row(align=True)
      row.operator("midipose.select_all_poses", text="Select All")
      row.operator("midipose.deselect_all_poses", text="Deselect All")
      row.operator("midipose.invert_pose_selection", text="Invert")
    else:
      layout.label(text="No poses found")
      layout.operator("midipose.refresh_poses", text="Scan for Poses", icon='FILE_REFRESH')


class MIDIPOSE_UL_tracks(UIList):
  """UIList for MIDI track selection"""
  
  def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
    props = context.scene.midi_pose_props
    is_selected = item.name == props.selected_track
    
    if self.layout_type in {'DEFAULT', 'COMPACT'}:
      icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
      row = layout.row(align=True)
      op = row.operator("midipose.select_track", 
                       text=f"{item.name}",
                       icon=icon,
                       emboss=False)
      op.track_name = item.name
      row.label(text=f"{item.note_count} notes")


class MIDIPOSE_UL_notes(UIList):
  """UIList for MIDI note selection with nicknames"""
  
  def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
    if self.layout_type in {'DEFAULT', 'COMPACT'}:
      row = layout.row(align=True)
      row.prop(item, "selected", text="")
      
      # Note name and number
      row.label(text=f"{item.note_name}")
      
      # Nickname field
      row.prop(item, "nickname", text="", emboss=True)
      
      # Count
      row.label(text=f"({item.count})")


class MIDIPOSE_PT_midi_column(Panel):
  """MIDI tracks and notes column"""
  bl_label = "MIDI Data"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "MIDI"
  bl_options = {'DEFAULT_CLOSED'}
  
  @classmethod
  def poll(cls, context):
    return context.area.ui_type == 'MIDIPOSE'
  
  def draw(self, context):
    layout = self.layout
    props = context.scene.midi_pose_props
    
    if not props.midi_file:
      layout.label(text="No MIDI file loaded", icon='INFO')
      return
    
    # Track Selection
    box = layout.box()
    box.label(text="MIDI Tracks", icon='NLA')
    
    if props.track_items:
      # Use UIList for tracks
      row = box.row()
      row.template_list(
        "MIDIPOSE_UL_tracks", "",
        props, "track_items",
        props, "active_track_index",
        rows=5
      )
      
      if props.selected_track:
        box.label(text=f"Selected: {props.selected_track}", icon='CHECKMARK')
    else:
      box.label(text="No tracks found")
    
    # Note Filter
    if props.selected_track and props.note_items:
      box = layout.box()
      row = box.row()
      row.prop(props, "filter_notes", text="Filter Notes")
      row.label(text="", icon='FILTER' if props.filter_notes else 'NONE')
      
      if props.filter_notes:
        # Note list with nicknames
        row = box.row()
        row.template_list(
          "MIDIPOSE_UL_notes", "",
          props, "note_items",
          props, "active_note_index",
          rows=8
        )
        
        # Quick nickname actions
        col = box.column()
        col.label(text="Nicknames help identify notes", icon='INFO')
        
        # Show selected notes with nicknames
        selected_notes = [n for n in props.note_items if n.selected]
        if selected_notes:
          col.separator()
          for note in selected_notes:
            if note.nickname:
              col.label(text=f"  {note.note_name} → {note.nickname}")
      else:
        box.label(text="All notes will be used", icon='INFO')


# Registration helper
def get_panels():
  return [
    MIDIPOSE_HT_header,
    MIDIPOSE_PT_main_column,
    MIDIPOSE_PT_poses_column,
    MIDIPOSE_PT_midi_column,
    MIDIPOSE_UL_poses,
    MIDIPOSE_UL_tracks,
    MIDIPOSE_UL_notes,
  ]