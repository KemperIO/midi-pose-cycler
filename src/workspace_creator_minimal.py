"""
Minimal workspace creator for testing
"""

import bpy
from bpy.types import Operator

class MIDIPOSE_OT_create_workspace(Operator):
    """Create MIDI Pose Cycler Workspace"""
    bl_idname = "midipose.create_workspace"
    bl_label = "Create MIDI Pose Workspace"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        print("Creating workspace...")
        
        # Check if workspace exists
        workspace_name = "MIDI Pose Cycler"
        
        if workspace_name in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces[workspace_name]
            self.report({'INFO'}, f"Switched to {workspace_name}")
            return {'FINISHED'}
        
        # Create new workspace
        bpy.ops.workspace.duplicate()
        workspace = context.window.workspace
        workspace.name = workspace_name
        
        self.report({'INFO'}, f"Created {workspace_name}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MIDIPOSE_OT_create_workspace)

def unregister():
    bpy.utils.unregister_class(MIDIPOSE_OT_create_workspace)