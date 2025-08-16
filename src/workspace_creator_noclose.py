"""
Workspace creator without area closing
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
        
        # Get window
        window = context.window
        if not window:
            window = context.window_manager.windows[0] if context.window_manager.windows else None
            if not window:
                self.report({'ERROR'}, "No window available")
                return {'CANCELLED'}
        
        # Create new workspace
        bpy.ops.workspace.duplicate()
        workspace = context.window.workspace
        workspace.name = workspace_name
        
        # Get screen
        screen = workspace.screens[0] if workspace.screens else None
        if not screen:
            self.report({'ERROR'}, "Failed to get workspace screen")
            return {'CANCELLED'}
        
        print(f"Have {len(screen.areas)} areas")
        
        # Don't close areas, just split what we have
        # Typically starts with 4 areas in default layout
        
        if len(screen.areas) >= 1:
            # Find the largest area (usually 3D viewport)
            main_area = max(screen.areas, key=lambda a: a.width * a.height)
            main_area.type = 'VIEW_3D'
            
            # Split it
            try:
                override = {'window': window, 'screen': screen, 'area': main_area}
                with context.temp_override(**override):
                    # Split horizontally
                    bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.75)
                print("Split main area")
            except Exception as e:
                print(f"Split failed: {e}")
        
        # Count final areas
        print(f"Final: {len(screen.areas)} areas")
        
        self.report({'INFO'}, f"Created {workspace_name}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MIDIPOSE_OT_create_workspace)

def unregister():
    bpy.utils.unregister_class(MIDIPOSE_OT_create_workspace)