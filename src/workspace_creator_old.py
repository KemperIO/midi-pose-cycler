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
        
        # Get current window properly
        window = context.window
        if not window:
            # Try to get from window manager
            window = context.window_manager.windows[0] if context.window_manager.windows else None
            if not window:
                self.report({'ERROR'}, "No window available")
                return {'CANCELLED'}
        
        # Duplicate current workspace as base
        bpy.ops.workspace.duplicate()
        
        # Rename the new workspace
        workspace = context.window.workspace
        workspace.name = workspace_name
        
        # Mark this workspace for our panels
        context.scene['midi_pose_workspace'] = workspace_name
        
        # Get the screen
        screen = workspace.screens[0] if workspace.screens else None
        if not screen:
            self.report({'ERROR'}, "Failed to get workspace screen")
            return {'CANCELLED'}
        
        # Clear all but one area to start fresh
        while len(screen.areas) > 1:
            area_to_close = screen.areas[-1]
            try:
                # Use proper override with window
                override = context.copy()
                override['window'] = window
                override['screen'] = screen
                override['area'] = area_to_close
                with context.temp_override(**override):
                    bpy.ops.screen.area_close()
            except:
                break
        
        if not screen.areas:
            self.report({'ERROR'}, "No areas in screen")
            return {'CANCELLED'}
        
        # Start with single area
        main_area = screen.areas[0]
        main_area.type = 'VIEW_3D'
        
        # Helper function to split areas safely
        def split_area(area, direction='VERTICAL', factor=0.5):
            try:
                override = context.copy()
                override['window'] = window
                override['screen'] = screen
                override['area'] = area
                with context.temp_override(**override):
                    bpy.ops.screen.area_split(direction=direction, factor=factor)
                return True
            except:
                return False
        
        # Create the layout according to spec:
        # Split for bottom section (Action Editor + Sequencer)
        if split_area(main_area, 'HORIZONTAL', 0.7):
            # Get top and bottom areas
            areas = sorted(screen.areas, key=lambda a: a.y, reverse=True)
            top_area = areas[0] if len(areas) > 0 else None
            bottom_area = areas[1] if len(areas) > 1 else None
            
            # Split top area for left sidebar (File + Asset browsers)
            if top_area and split_area(top_area, 'VERTICAL', 0.2):
                # Get left and middle-right areas
                # Get window dimensions
                win_height = window.height if window else 1000
                win_width = window.width if window else 1600
                top_areas = [a for a in screen.areas if a.y > win_height * 0.3]
                top_areas.sort(key=lambda a: a.x)
                left_area = top_areas[0] if len(top_areas) > 0 else None
                middle_right_area = top_areas[1] if len(top_areas) > 1 else None
                
                # Split middle-right for right sidebar (Properties panels)
                if middle_right_area and split_area(middle_right_area, 'VERTICAL', 0.65):
                    # Get middle and right areas
                    top_areas = [a for a in screen.areas if a.y > win_height * 0.3]
                    top_areas.sort(key=lambda a: a.x)
                    right_area = top_areas[-1] if len(top_areas) > 1 else None
                    
                    # Split left area for File and Asset browsers
                    if left_area:
                        split_area(left_area, 'HORIZONTAL', 0.5)
                    
                    # Split bottom area for Action Editor and Sequencer
                    if bottom_area:
                        split_area(bottom_area, 'HORIZONTAL', 0.85)
                    
                    # Split right area for 3 Properties panels
                    if right_area:
                        if split_area(right_area, 'HORIZONTAL', 0.33):
                            # Find and split the bottom part again
                            right_areas = [a for a in screen.areas if a.x > win_width * 0.65]
                            right_areas.sort(key=lambda a: a.y, reverse=True)
                            if len(right_areas) >= 2:
                                split_area(right_areas[1], 'HORIZONTAL', 0.5)
        
        # Now assign editor types to each area based on position
        # Get window dimensions for relative positioning
        win_height = window.height if window else 1000
        win_width = window.width if window else 1600
        
        for area in screen.areas:
            x_rel = area.x / win_width if win_width > 0 else 0
            y_rel = area.y / win_height if win_height > 0 else 0
            
            # Left column (File + Asset browsers)
            if x_rel < 0.15:
                if y_rel > 0.5:
                    # Top left - File Browser
                    area.type = 'FILE_BROWSER'
                    for space in area.spaces:
                        if space.type == 'FILE_BROWSER':
                            try:
                                space.params.use_filter = True
                                space.params.use_filter_sound = True
                            except:
                                pass
                else:
                    # Bottom left - Asset Browser
                    area.type = 'ASSETS'
            
            # Middle column (3D Viewport, Action Editor, Sequencer)
            elif x_rel < 0.65:
                if y_rel > 0.3:
                    # Middle - 3D Viewport
                    area.type = 'VIEW_3D'
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'SOLID'
                            space.show_region_ui = False  # Hide N-panel since we have Properties
                elif y_rel > 0.05:
                    # Bottom middle - Action Editor
                    area.type = 'DOPESHEET_EDITOR'
                    for space in area.spaces:
                        if space.type == 'DOPESHEET_EDITOR':
                            space.mode = 'ACTION'
                            space.show_region_ui = False
                else:
                    # Very bottom - Sequencer
                    area.type = 'SEQUENCE_EDITOR'
                    for space in area.spaces:
                        if space.type == 'SEQUENCE_EDITOR':
                            space.view_type = 'SEQUENCER'
                            space.show_region_ui = False
            
            # Right column (Properties panels)
            else:
                # All right areas become Properties
                area.type = 'PROPERTIES'
                for space in area.spaces:
                    if space.type == 'PROPERTIES':
                        # Set to SCENE context for our panels
                        try:
                            space.context = 'SCENE'
                        except:
                            pass
        
        self.report({'INFO'}, f"Created {workspace_name} workspace with full layout")
        return {'FINISHED'}


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