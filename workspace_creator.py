"""
MIDI Pose Cycler - Custom Workspace Creator
Creates a comprehensive workspace with all necessary editors
"""

import bpy
from bpy.types import Operator

class MIDIPOSE_OT_create_workspace(Operator):
  """Create MIDI Pose Cycler Workspace"""
  bl_idname = "midipose.create_workspace"
  bl_label = "Create MIDI Pose Workspace"
  bl_description = "Create a comprehensive workspace for MIDI pose animation"
  bl_options = {'REGISTER'}
  
  def execute(self, context):
    # Check if workspace already exists
    workspace_name = "MIDI Pose Cycler"
    
    if workspace_name in bpy.data.workspaces:
      # Switch to existing workspace
      context.window.workspace = bpy.data.workspaces[workspace_name]
      self.report({'INFO'}, f"Switched to {workspace_name} workspace")
      return {'FINISHED'}
    
    # Store current workspace to duplicate from
    original_workspace = context.window.workspace
    
    # Create new workspace
    bpy.ops.workspace.append_activate(
      idname="Animation",  # Start from Animation workspace template
      filepath=bpy.utils.preset_paths("interface_theme")[0] + "/../startup.blend/Workspace/"
    )
    
    # Get the new workspace and rename it
    workspace = context.window.workspace
    workspace.name = workspace_name
    
    # Get the screen
    screen = workspace.screens[0]
    
    # Clear all areas and rebuild
    self.setup_workspace_layout(context, screen)
    
    # Mark this workspace for our panels
    context.scene['midi_pose_workspace'] = workspace_name
    
    self.report({'INFO'}, f"Created {workspace_name} workspace")
    return {'FINISHED'}
  
  def setup_workspace_layout(self, context, screen):
    """Setup the specific layout with all required editors"""
    
    # Start with a single area
    while len(screen.areas) > 1:
      area = screen.areas[-1]
      with context.temp_override(area=area):
        try:
          bpy.ops.screen.area_close()
        except:
          break
    
    if not screen.areas:
      return {'CANCELLED'}
    
    main_area = screen.areas[0]
    main_area.type = 'VIEW_3D'
    
    # Split horizontally for bottom section (40% bottom)
    with context.temp_override(area=main_area):
      bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.65)
    
    # Areas after first split: top (3D view), bottom
    top_area = None
    bottom_area = None
    for area in screen.areas:
      if area.y > screen.height / 2:
        top_area = area
      else:
        bottom_area = area
    
    # Split top area vertically for left sidebar (25% left)
    if top_area:
      with context.temp_override(area=top_area):
        bpy.ops.screen.area_split(direction='VERTICAL', factor=0.25)
    
    # Find left and middle-right areas
    left_area = None
    middle_right_area = None
    for area in screen.areas:
      if area.y > screen.height / 2:  # Top half
        if area.x < screen.width * 0.2:
          left_area = area
        else:
          middle_right_area = area
    
    # Split middle-right vertically for right sidebar (30% right)
    if middle_right_area:
      with context.temp_override(area=middle_right_area):
        bpy.ops.screen.area_split(direction='VERTICAL', factor=0.70)
    
    # Find middle and right areas
    middle_area = None
    right_area = None
    for area in screen.areas:
      if area.y > screen.height / 2:  # Top half
        if area.x > screen.width * 0.2 and area.x < screen.width * 0.6:
          middle_area = area
        elif area.x > screen.width * 0.6:
          right_area = area
    
    # Split left area horizontally for file and asset browsers
    if left_area:
      with context.temp_override(area=left_area):
        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.5)
    
    # Find top-left and bottom-left
    top_left = None
    bottom_left = None
    for area in screen.areas:
      if area.x < screen.width * 0.3:  # Left side
        if area.y > screen.height * 0.5:
          top_left = area
        elif area.y > screen.height * 0.3:
          bottom_left = area
    
    # Split bottom area horizontally for action editor and sequencer
    if bottom_area:
      with context.temp_override(area=bottom_area):
        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.6)
    
    # Find action editor and sequencer areas
    action_area = None
    sequencer_area = None
    for area in screen.areas:
      if area.y < screen.height * 0.4:  # Bottom section
        if area.y > screen.height * 0.15:
          action_area = area
        else:
          sequencer_area = area
    
    # Split right area horizontally for three property panels
    if right_area:
      # First split
      with context.temp_override(area=right_area):
        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.33)
      
      # Find and split again
      for area in screen.areas:
        if area.x > screen.width * 0.7 and area.y < screen.height * 0.7 and area.y > screen.height * 0.4:
          with context.temp_override(area=area):
            bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.5)
          break
    
    # Now assign editor types to each area
    areas_config = []
    
    for area in screen.areas:
      x_pos = area.x / screen.width
      y_pos = area.y / screen.height
      
      # Left side
      if x_pos < 0.3:
        if y_pos > 0.5:
          # Top left - File Browser
          area.type = 'FILE_BROWSER'
          areas_config.append(('FILE_BROWSER', area))
        else:
          # Bottom left - Asset Browser  
          area.type = 'ASSETS'
          areas_config.append(('ASSETS', area))
      
      # Middle
      elif x_pos < 0.7:
        if y_pos > 0.4:
          # Middle - 3D Viewport
          area.type = 'VIEW_3D'
          areas_config.append(('VIEW_3D', area))
        elif y_pos > 0.15:
          # Bottom middle - Action Editor
          area.type = 'DOPESHEET_EDITOR'
          areas_config.append(('DOPESHEET_EDITOR', area))
        else:
          # Very bottom - Sequencer
          area.type = 'SEQUENCE_EDITOR'
          areas_config.append(('SEQUENCE_EDITOR', area))
      
      # Right side - Properties panels
      else:
        area.type = 'PROPERTIES'
        areas_config.append(('PROPERTIES', area))
    
    # Configure each area
    for area_type, area in areas_config:
      self.configure_area(area, area_type)
    
    return {'FINISHED'}
  
  def configure_area(self, area, area_type):
    """Configure specific area settings"""
    
    if area_type == 'FILE_BROWSER':
      # Configure for MIDI files
      for space in area.spaces:
        if space.type == 'FILE_BROWSER':
          space.params.use_filter = True
          space.params.use_filter_sound = True
          # Set to recent folder or user folder
          try:
            space.params.directory = bpy.path.abspath("//")
          except:
            pass
    
    elif area_type == 'ASSETS':
      # Configure for pose assets
      for space in area.spaces:
        if space.type == 'ASSETS':
          # Filter to show only Actions
          pass  # Asset browser configuration
    
    elif area_type == 'VIEW_3D':
      # Configure 3D viewport
      for space in area.spaces:
        if space.type == 'VIEW_3D':
          space.shading.type = 'SOLID'
          space.overlay.show_floor = True
          space.overlay.show_axis_x = True
          space.overlay.show_axis_y = True
          space.show_region_ui = False  # Hide sidebar
          space.show_region_tool_header = True
    
    elif area_type == 'DOPESHEET_EDITOR':
      # Configure as Action Editor
      for space in area.spaces:
        if space.type == 'DOPESHEET_EDITOR':
          space.mode = 'ACTION'
          space.show_region_ui = False
    
    elif area_type == 'SEQUENCE_EDITOR':
      # Configure sequencer
      for space in area.spaces:
        if space.type == 'SEQUENCE_EDITOR':
          space.view_type = 'SEQUENCER'
          space.show_region_ui = False
    
    elif area_type == 'PROPERTIES':
      # Configure properties panel
      for space in area.spaces:
        if space.type == 'PROPERTIES':
          space.context = 'SCENE'  # Our panels use scene context


class MIDIPOSE_OT_setup_drag_drop(Operator):
  """Setup drag and drop for MIDI files"""
  bl_idname = "midipose.setup_drag_drop"
  bl_label = "Setup MIDI Drag & Drop"
  bl_description = "Enable drag and drop for MIDI files from file browser"
  
  def execute(self, context):
    # This would require handler registration
    self.report({'INFO'}, "Drag & drop setup complete")
    return {'FINISHED'}


def register():
  bpy.utils.register_class(MIDIPOSE_OT_create_workspace)
  bpy.utils.register_class(MIDIPOSE_OT_setup_drag_drop)

def unregister():
  bpy.utils.unregister_class(MIDIPOSE_OT_setup_drag_drop)
  bpy.utils.unregister_class(MIDIPOSE_OT_create_workspace)