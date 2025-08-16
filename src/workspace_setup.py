"""
MIDI Pose Cycler - Workspace Setup
Creates a custom workspace layout for the addon
Since we can't create new SpaceTypes, we use a custom workspace approach
"""

import bpy
from bpy.types import Operator

def create_midi_pose_workspace():
  """Create a dedicated workspace for MIDI Pose Cycler"""
  
  # Check if workspace already exists
  workspace_name = "MIDI Pose Cycler"
  if workspace_name in bpy.data.workspaces:
    # Switch to it
    bpy.context.window.workspace = bpy.data.workspaces[workspace_name]
    return bpy.data.workspaces[workspace_name]
  
  # Create new workspace
  bpy.ops.workspace.duplicate()
  workspace = bpy.context.window.workspace
  workspace.name = workspace_name
  
  # Clear all screens and start fresh
  screens = list(workspace.screens)
  for screen in screens[1:]:  # Keep first screen
    bpy.data.screens.remove(screen)
  
  screen = workspace.screens[0]
  
  # Remove all areas except one
  while len(screen.areas) > 1:
    area = screen.areas[1]
    with bpy.context.temp_override(area=area):
      bpy.ops.screen.area_close()
  
  # Now split the remaining area into our layout
  main_area = screen.areas[0]
  
  # First split: Create left panel (30% width)
  with bpy.context.temp_override(area=main_area):
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.3)
  
  left_area = screen.areas[0]
  middle_area = screen.areas[1]
  
  # Second split: Split middle area to create right panel (40% of remaining)
  with bpy.context.temp_override(area=middle_area):
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.6)
  
  middle_area = screen.areas[1]
  right_area = screen.areas[2]
  
  # Configure each area
  # LEFT: Properties editor for main controls
  left_area.type = 'PROPERTIES'
  for space in left_area.spaces:
    if space.type == 'PROPERTIES':
      space.context = 'SCENE'  # Scene properties where our addon lives
  
  # MIDDLE: 3D View for pose preview/selection
  middle_area.type = 'VIEW_3D'
  for space in middle_area.spaces:
    if space.type == 'VIEW_3D':
      # Set to solid shading for better pose visibility
      space.shading.type = 'SOLID'
      # Show sidebar
      space.show_region_ui = True
  
  # RIGHT: Text Editor for MIDI data display (or another Properties panel)
  right_area.type = 'PROPERTIES'
  for space in right_area.spaces:
    if space.type == 'PROPERTIES':
      space.context = 'SCENE'
  
  return workspace


class MIDIPOSE_OT_setup_workspace(Operator):
  """Set up MIDI Pose Cycler workspace"""
  bl_idname = "midipose.setup_workspace"
  bl_label = "Setup MIDI Pose Workspace"
  bl_description = "Create a dedicated workspace for MIDI Pose Cycler"
  
  def execute(self, context):
    workspace = create_midi_pose_workspace()
    if workspace:
      self.report({'INFO'}, f"Workspace '{workspace.name}' created")
    else:
      self.report({'ERROR'}, "Failed to create workspace")
    return {'FINISHED'}


def register():
  bpy.utils.register_class(MIDIPOSE_OT_setup_workspace)


def unregister():
  bpy.utils.unregister_class(MIDIPOSE_OT_setup_workspace)