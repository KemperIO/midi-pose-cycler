"""
MIDI Pose Cycler - Custom Editor Implementation
Since Blender doesn't allow true custom Space types from Python,
this creates a dedicated interface that takes over an existing editor type
"""

import bpy
from bpy.types import Panel, Header, Operator, UIList
import os

# Use a specific context to identify our custom editor mode
class MIDIPOSE_OT_enable_editor(Operator):
  """Enable MIDI Pose Cycler Editor Mode"""
  bl_idname = "midipose.enable_editor"
  bl_label = "MIDI Pose Cycler Editor"
  bl_description = "Switch this area to MIDI Pose Cycler editor"
  
  def execute(self, context):
    # Mark this area as MIDI Pose editor
    area = context.area
    area.type = 'PROPERTIES'
    
    for space in area.spaces:
      if space.type == 'PROPERTIES':
        space.context = 'SCENE'
    
    # Set a flag to identify this as MIDI Pose editor
    context.scene['midi_pose_editor_active'] = True
    
    # Create workspace if needed
    workspace = context.window.workspace
    if workspace.name != "MIDI Pose Cycler":
      bpy.ops.workspace.duplicate()
      new_workspace = context.window.workspace
      new_workspace.name = "MIDI Pose Cycler"
    
    self.report({'INFO'}, "MIDI Pose Cycler Editor activated")
    return {'FINISHED'}


# Main editor panel that takes over the Properties editor
class MIDIPOSE_PT_custom_editor(Panel):
  """MIDI Pose Cycler Custom Editor"""
  bl_label = ""
  bl_idname = "MIDIPOSE_PT_custom_editor"
  bl_space_type = 'PROPERTIES'
  bl_region_type = 'WINDOW'
  bl_context = "scene"
  bl_options = {'HIDE_HEADER'}
  
  @classmethod
  def poll(cls, context):
    # Show only when in MIDI Pose editor mode
    return (context.workspace.name == "MIDI Pose Cycler" or 
            context.scene.get('midi_pose_editor_active', False))
  
  def draw(self, context):
    layout = self.layout
    scene = context.scene
    props = scene.midi_pose_props
    
    # Full-width header
    header_row = layout.row()
    header_row.scale_y = 1.5
    header_row.label(text="MIDI POSE CYCLER", icon='FILE_SOUND')
    
    # Quick status bar
    status_row = layout.row()
    status_row.alignment = 'CENTER'
    
    if props.midi_file:
      status_row.label(text=f"📁 {os.path.basename(props.midi_file)}")
    else:
      status_row.label(text="No MIDI loaded")
    
    if props.selected_track:
      status_row.label(text=f"🎵 {props.selected_track}")
    
    selected_poses = sum(1 for p in props.pose_items if p.selected)
    if selected_poses > 0:
      status_row.label(text=f"🎭 {selected_poses} poses")
    
    layout.separator()
    
    # Three-column layout
    main_row = layout.row()
    
    # Check region width for responsive layout
    try:
      region_width = context.region.width
    except:
      region_width = 800
    
    use_columns = region_width > 700
    
    if use_columns:
      # Three columns
      col_control = main_row.column()
      col_control.scale_x = 1.0
      
      main_row.separator()
      
      col_poses = main_row.column()
      col_poses.scale_x = 1.2
      
      main_row.separator()
      
      col_midi = main_row.column()
      col_midi.scale_x = 1.0
    else:
      # Vertical stack
      col_control = layout.column()
      layout.separator()
      col_poses = layout.column()
      layout.separator()
      col_midi = layout.column()
    
    # Draw each section
    self.draw_controls(col_control, context)
    self.draw_poses(col_poses, context)
    self.draw_midi(col_midi, context)
    
    # Bottom action bar
    layout.separator()
    action_row = layout.row()
    action_row.scale_y = 2.0
    action_row.operator("midipose.render_animation", 
                       text="🎬 GENERATE ANIMATION", 
                       icon='PLAY')
  
  def draw_controls(self, col, context):
    """Control section"""
    scene = context.scene
    props = scene.midi_pose_props
    
    # Section header
    box = col.box()
    box.label(text="⚙️ CONTROLS", icon='PREFERENCES')
    
    # MIDI File
    sub_box = box.box()
    sub_box.label(text="MIDI File", icon='FILE_SOUND')
    
    if props.midi_file:
      sub_box.label(text=os.path.basename(props.midi_file), icon='FILE_TICK')
      row = sub_box.row(align=True)
      row.operator("midipose.load_midi", text="Change")
      row.operator("midipose.reload_midi", text="Reload")
    else:
      sub_box.operator("midipose.load_midi", text="📂 Load MIDI File")
    
    # Action
    sub_box = box.box()
    sub_box.label(text="Action", icon='ACTION')
    
    row = sub_box.row(align=True)
    row.prop(props, "action_name", text="")
    
    action = bpy.data.actions.get(props.action_name)
    if action and action.fcurves and any(fc.keyframe_points for fc in action.fcurves):
      row.label(text="⚠️", icon='ERROR')
    
    if props.skip_keyframe_warning:
      sub_box.label(text="⏭️ Skipping warnings", icon='INFO')
    
    # Animation
    sub_box = box.box()
    sub_box.label(text="Animation", icon='ANIM')
    
    sub_box.prop(props, "pose_cycle_mode", text="")
    
    row = sub_box.row(align=True)
    split = row.split(factor=0.4)
    split.label(text="Hold:")
    split.prop(props, "frames_to_hold", text="")
    
    sub_box.prop(props, "interpolation_type", text="")
    
    # Frame limit
    row = sub_box.row(align=True)
    row.prop(props, "use_frame_limit", text="")
    if props.use_frame_limit:
      row.prop(props, "frame_limit", text="Limit")
      sub_box.label(text=f"📏 Max {props.frame_limit} frames", icon='INFO')
    else:
      row.label(text="Unlimited")
      sub_box.label(text="♾️ Use all MIDI events", icon='INFO')
    
    sub_box.label(text=f"🎬 FPS: {scene.render.fps}")
    
    # Configurations
    sub_box = box.box()
    sub_box.label(text="Configurations", icon='FILE_FOLDER')
    
    if props.active_config:
      sub_box.label(text=f"📌 {props.active_config}")
    
    row = sub_box.row(align=True)
    row.operator("midipose.save_config", text="💾 Save")
    row.operator("midipose.save_config_as", text="💾 Save As")
    
    row = sub_box.row(align=True)
    row.operator("midipose.load_config", text="📂 Load")
    if props.active_config:
      row.operator("midipose.delete_config", text="🗑️ Delete")
  
  def draw_poses(self, col, context):
    """Poses section"""
    props = context.scene.midi_pose_props
    
    # Section header
    box = col.box()
    row = box.row()
    row.label(text="🎭 POSES", icon='ARMATURE_DATA')
    row.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH')
    
    if not props.pose_items:
      sub_box = box.box()
      sub_box.label(text="No poses found", icon='INFO')
      sub_box.operator("midipose.refresh_poses", text="🔍 Scan for Poses")
      return
    
    # Quick select
    row = box.row(align=True)
    row.operator("midipose.select_all_poses", text="✅ All")
    row.operator("midipose.deselect_all_poses", text="❌ None")
    row.operator("midipose.invert_pose_selection", text="🔄 Invert")
    
    # Pose grid
    pose_box = box.box()
    
    # Calculate columns based on width
    try:
      width = context.region.width / 3  # Approximate column width
      cols = max(1, int(width / 150))
    except:
      cols = 2
    
    flow = pose_box.grid_flow(row_major=True, columns=cols, even_columns=True, align=False)
    
    for pose in props.pose_items:
      row = flow.row(align=True)
      
      # Check if action exists
      action = bpy.data.actions.get(pose.name)
      
      # Visual indicator
      if pose.selected:
        selected_poses = [p for p in props.pose_items if p.selected]
        order = selected_poses.index(pose) + 1
        icon_text = f"#{order}"
      else:
        icon_text = ""
      
      # Checkbox with icon
      sub = row.row(align=True)
      sub.prop(pose, "selected", text="")
      
      # Name label
      name_row = sub.row()
      name_row.active = pose.selected
      
      # Truncate long names
      max_len = 15
      name = pose.name[:max_len] + "..." if len(pose.name) > max_len else pose.name
      name_row.label(text=name)
      
      # Order number
      if icon_text:
        row.label(text=icon_text)
    
    # Summary
    selected_count = sum(1 for p in props.pose_items if p.selected)
    box.separator()
    info_row = box.row()
    info_row.label(text=f"✅ {selected_count}/{len(props.pose_items)} selected")
    if selected_count > 0:
      info_row.label(text=f"🔄 {props.pose_cycle_mode}")
  
  def draw_midi(self, col, context):
    """MIDI data section"""
    props = context.scene.midi_pose_props
    
    # Section header
    box = col.box()
    box.label(text="🎵 MIDI DATA", icon='NLA')
    
    if not props.midi_file:
      sub_box = box.box()
      sub_box.label(text="No MIDI file loaded", icon='INFO')
      return
    
    # Tracks
    sub_box = box.box()
    sub_box.label(text="Tracks", icon='NLA_PUSHDOWN')
    
    if props.track_items:
      track_col = sub_box.column()
      
      for track in props.track_items:
        row = track_col.row(align=True)
        is_selected = track.name == props.selected_track
        
        # Radio button
        icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
        op = row.operator("midipose.select_track", 
                         text="",
                         icon=icon,
                         emboss=False)
        op.track_name = track.name
        
        # Track name and count
        text_row = row.row()
        text_row.active = is_selected
        text_row.label(text=f"{track.name}")
        row.label(text=f"[{track.note_count}]")
      
      if props.selected_track:
        sub_box.separator()
        sub_box.label(text=f"✅ {props.selected_track}", icon='CHECKMARK')
    else:
      sub_box.label(text="No tracks found")
    
    # Notes
    if props.selected_track and props.note_items:
      sub_box = box.box()
      row = sub_box.row()
      row.prop(props, "filter_notes", text="Filter Notes")
      
      if props.filter_notes:
        # Note list with nicknames
        note_col = sub_box.column()
        
        # Compact note display
        for note in props.note_items[:10]:  # Limit display
          row = note_col.row(align=True)
          
          # Selection
          row.prop(note, "selected", text="")
          
          # Note
          row.label(text=f"{note.note_name}")
          
          # Nickname field
          row.prop(note, "nickname", text="")
          
          # Count
          row.label(text=f"×{note.count}")
        
        if len(props.note_items) > 10:
          note_col.label(text=f"... and {len(props.note_items) - 10} more")
        
        # Show nicknamed notes
        nicknamed = [(n.note_name, n.nickname) 
                    for n in props.note_items 
                    if n.nickname and n.selected]
        
        if nicknamed:
          sub_box.separator()
          for note_name, nickname in nicknamed[:5]:
            row = sub_box.row()
            row.label(text=f"{note_name} → {nickname}")
      else:
        sub_box.label(text="🎹 Using all notes", icon='CHECKBOX_HLT')


# Add to editor type menu
def editor_menu_func(self, context):
  """Add option to editor type menu"""
  layout = self.layout
  layout.operator("midipose.enable_editor", 
                 text="MIDI Pose Cycler",
                 icon='FILE_SOUND')


classes = [
  MIDIPOSE_OT_enable_editor,
  MIDIPOSE_PT_custom_editor,
]

def register():
  for cls in classes:
    bpy.utils.register_class(cls)
  
  # Add to editor menus
  if hasattr(bpy.types, 'TOPBAR_MT_editor_menus'):
    bpy.types.TOPBAR_MT_editor_menus.append(editor_menu_func)

def unregister():
  # Remove from menus
  if hasattr(bpy.types, 'TOPBAR_MT_editor_menus'):
    bpy.types.TOPBAR_MT_editor_menus.remove(editor_menu_func)
  
  for cls in reversed(classes):
    bpy.utils.unregister_class(cls)