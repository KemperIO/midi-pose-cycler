"""
MIDI Pose Cycler - Custom Space Type Implementation
Creates a custom editor type for MIDI Pose Cycler
"""

import bpy
from bpy.types import Space, Region, Header, Panel

# Custom Space Type
class MIDIPOSE_SPACE(Space):
  """MIDI Pose Cycler Editor Space"""
  bl_idname = "MIDI_POSE_CYCLER"
  bl_label = "MIDI Pose Cycler"
  
  def draw(self, context):
    # Space drawing is handled by regions and panels
    pass


# Custom Region for the space
class MIDIPOSE_REGION_window(Region):
  """Main window region for MIDI Pose Cycler"""
  bl_space_type = 'MIDI_POSE_CYCLER'
  bl_region_type = 'WINDOW'
  
  def draw(self, context):
    # Region drawing handled by panels
    pass


# Header for the custom space
class MIDIPOSE_HT_header(Header):
  """Header for MIDI Pose Cycler Editor"""
  bl_space_type = 'MIDI_POSE_CYCLER'
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # Standard header template
    layout.template_header()
    
    # Quick status indicators
    row = layout.row(align=True)
    row.label(text="MIDI Pose Cycler", icon='FILE_SOUND')
    
    layout.separator_spacer()
    
    # File status
    if props.midi_file:
      import os
      row = layout.row(align=True)
      row.label(text=f"File: {os.path.basename(props.midi_file)}", icon='FILE_TICK')
      row.operator("midipose.reload_midi", text="", icon='FILE_REFRESH')
    else:
      layout.operator("midipose.load_midi", text="Load MIDI", icon='FILE_FOLDER')
    
    # Track status
    if props.selected_track:
      layout.label(text=f"Track: {props.selected_track}")
    
    # Pose status
    selected_poses = sum(1 for p in props.pose_items if p.selected)
    if selected_poses > 0:
      layout.label(text=f"Poses: {selected_poses}")
    
    # Config status
    if props.active_config:
      layout.label(text=f"Config: {props.active_config}")
    
    layout.separator_spacer()
    
    # Quick generate button
    if props.midi_file and props.selected_track and selected_poses > 0:
      row = layout.row(align=True)
      row.scale_x = 1.2
      row.operator("midipose.render_animation", text="Generate", icon='PLAY')


# Main panel for the custom space
class MIDIPOSE_PT_main(Panel):
  """Main panel for MIDI Pose Cycler"""
  bl_label = ""
  bl_idname = "MIDIPOSE_PT_main"
  bl_space_type = 'MIDI_POSE_CYCLER'
  bl_region_type = 'WINDOW'
  bl_options = {'HIDE_HEADER'}
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # Create three-column layout
    main_row = layout.row()
    
    # Adaptive layout based on width
    region_width = context.region.width if hasattr(context, 'region') else 800
    use_columns = region_width > 600
    
    if use_columns:
      # Three columns
      col_control = main_row.column()
      col_control.scale_x = 0.8
      
      col_poses = main_row.column()
      col_poses.scale_x = 1.0
      
      col_midi = main_row.column()
      col_midi.scale_x = 0.8
    else:
      # Stack vertically
      col_control = layout.column()
      layout.separator()
      col_poses = layout.column()
      layout.separator()
      col_midi = layout.column()
    
    # CONTROL COLUMN
    self.draw_controls(col_control, context)
    
    # POSES COLUMN
    self.draw_poses(col_poses, context)
    
    # MIDI COLUMN
    self.draw_midi(col_midi, context)
  
  def draw_controls(self, col, context):
    """Draw control column"""
    scene = context.scene
    props = scene.midi_pose_props
    
    # Title
    header = col.row()
    header.scale_y = 1.3
    header.label(text="CONTROLS", icon='PREFERENCES')
    
    # MIDI File
    box = col.box()
    box.label(text="MIDI File", icon='FILE_SOUND')
    if props.midi_file:
      import os
      box.label(text=os.path.basename(props.midi_file))
      row = box.row(align=True)
      row.operator("midipose.load_midi", text="Change File")
      row.operator("midipose.reload_midi", text="", icon='FILE_REFRESH')
    else:
      box.operator("midipose.load_midi", text="Load MIDI File", icon='FILEBROWSER')
    
    # Action Settings
    box = col.box()
    box.label(text="Action", icon='ACTION')
    
    row = box.row(align=True)
    row.prop(props, "action_name", text="")
    
    # Check for existing keyframes
    action = bpy.data.actions.get(props.action_name)
    if action and action.fcurves:
      if any(fc.keyframe_points for fc in action.fcurves):
        row.label(text="", icon='ERROR')
    
    box.prop(props, "skip_keyframe_warning")
    
    # Animation Settings
    box = col.box()
    box.label(text="Animation", icon='ANIM')
    
    box.prop(props, "pose_cycle_mode", text="Cycle Mode")
    
    row = box.row(align=True)
    row.label(text="Hold:")
    row.prop(props, "frames_to_hold", text="")
    row.label(text="frames")
    
    box.prop(props, "interpolation_type", text="Interpolation")
    
    # Frame Limit
    row = box.row(align=True)
    row.prop(props, "use_frame_limit", text="")
    row.label(text="Frame Limit:")
    sub = row.row()
    sub.active = props.use_frame_limit
    sub.prop(props, "frame_limit", text="")
    
    if props.use_frame_limit:
      box.label(text=f"Max {props.frame_limit} frames", icon='INFO')
    else:
      box.label(text="Using all MIDI events", icon='INFO')
    
    box.label(text=f"Project FPS: {scene.render.fps}")
    
    # Configurations
    box = col.box()
    box.label(text="Configurations", icon='FILE_FOLDER')
    
    row = box.row(align=True)
    row.prop(props, "active_config", text="")
    row.operator("midipose.save_config", text="", icon='FILE_TICK')
    
    row = box.row(align=True)
    row.operator("midipose.save_config_as", text="Save As...")
    row.operator("midipose.load_config", text="Load")
    
    if props.active_config:
      row = box.row()
      row.operator("midipose.delete_config", text="Delete Config", icon='X')
    
    # Main Generate Button
    col.separator()
    row = col.row()
    row.scale_y = 2.5
    row.operator("midipose.render_animation", text="GENERATE ANIMATION", icon='PLAY')
  
  def draw_poses(self, col, context):
    """Draw poses column"""
    props = context.scene.midi_pose_props
    
    # Title
    header = col.row()
    header.scale_y = 1.3
    header.label(text="POSES", icon='ARMATURE_DATA')
    header.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH')
    
    if not props.pose_items:
      box = col.box()
      box.label(text="No poses found", icon='INFO')
      box.operator("midipose.refresh_poses", text="Scan for Poses", icon='VIEW_ORTHO')
      return
    
    # Quick actions
    row = col.row(align=True)
    row.operator("midipose.select_all_poses", text="All")
    row.operator("midipose.deselect_all_poses", text="None")
    row.operator("midipose.invert_pose_selection", text="Invert")
    
    # Pose list
    box = col.box()
    
    # Grid layout for poses
    cols = 2 if context.region.width > 400 else 1
    flow = box.grid_flow(row_major=True, columns=cols, even_columns=True, even_rows=False, align=True)
    
    for i, pose in enumerate(props.pose_items):
      # Pose item row
      row = flow.row(align=True)
      
      # Check for action
      action = bpy.data.actions.get(pose.name)
      icon = 'ACTION' if action else 'POSE_HLT'
      
      # Selection
      row.prop(pose, "selected", text="", icon=icon)
      
      # Name
      sub = row.row()
      sub.active = pose.selected
      name_display = pose.name[:20] + "..." if len(pose.name) > 20 else pose.name
      sub.label(text=name_display)
      
      # Order indicator
      if pose.selected:
        selected_poses = [p for p in props.pose_items if p.selected]
        order = selected_poses.index(pose) + 1
        row.label(text=f"#{order}")
    
    # Summary
    selected_count = sum(1 for p in props.pose_items if p.selected)
    col.separator()
    col.label(text=f"Selected: {selected_count} of {len(props.pose_items)}")
    
    if selected_count > 0:
      col.label(text=f"Mode: {props.pose_cycle_mode}", icon='RECOVER_LAST')
  
  def draw_midi(self, col, context):
    """Draw MIDI data column"""
    props = context.scene.midi_pose_props
    
    # Title
    header = col.row()
    header.scale_y = 1.3
    header.label(text="MIDI DATA", icon='NLA')
    
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
        
        # Radio button selection
        icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
        op = row.operator("midipose.select_track", text="", icon=icon, emboss=False)
        op.track_name = track.name
        
        # Track info
        sub = row.row()
        sub.active = is_selected
        sub.label(text=track.name)
        row.label(text=f"[{track.note_count}]")
      
      if props.selected_track:
        box.separator()
        row = box.row()
        row.label(text="Active:", icon='CHECKMARK')
        row.label(text=props.selected_track)
    else:
      box.label(text="No tracks found")
    
    # Note Filter
    if props.selected_track and props.note_items:
      col.separator()
      box = col.box()
      
      row = box.row()
      row.prop(props, "filter_notes", text="Filter Notes")
      row.label(text="", icon='FILTER' if props.filter_notes else 'NONE')
      
      if props.filter_notes:
        # Note list
        note_box = box.column()
        
        for note in props.note_items:
          row = note_box.row(align=True)
          
          # Selection
          row.prop(note, "selected", text="")
          
          # Note name
          row.label(text=note.note_name)
          
          # Nickname
          row.prop(note, "nickname", text="", placeholder="nickname")
          
          # Count
          row.label(text=f"({note.count})")
        
        # Nicknamed notes summary
        nicknamed = [(n.note_name, n.nickname) for n in props.note_items 
                     if n.nickname and n.selected]
        
        if nicknamed:
          col.separator()
          sum_box = col.box()
          sum_box.label(text="Note Aliases:", icon='INFO')
          for note_name, nickname in nicknamed:
            row = sum_box.row()
            row.label(text=f"{note_name}")
            row.label(text="→")
            row.label(text=nickname)
      else:
        box.label(text="Using all notes", icon='CHECKBOX_HLT')


# Tool shelf panel
class MIDIPOSE_PT_tools(Panel):
  """Tool shelf for MIDI Pose Cycler"""
  bl_label = "Tools"
  bl_idname = "MIDIPOSE_PT_tools"
  bl_space_type = 'MIDI_POSE_CYCLER'
  bl_region_type = 'TOOLS'
  bl_category = "MIDI Pose"
  
  def draw(self, context):
    layout = self.layout
    col = layout.column()
    
    col.operator("midipose.setup_workspace", text="Setup Workspace", icon='WORKSPACE')
    col.separator()
    col.operator("midipose.refresh_poses", text="Refresh Poses", icon='FILE_REFRESH')


# Classes to register
classes = [
  MIDIPOSE_SPACE,
  MIDIPOSE_REGION_window,
  MIDIPOSE_HT_header,
  MIDIPOSE_PT_main,
  MIDIPOSE_PT_tools,
]

def register():
  for cls in classes:
    bpy.utils.register_class(cls)

def unregister():
  for cls in reversed(classes):
    bpy.utils.unregister_class(cls)