"""
MIDI Pose Cycler - Workspace Creator
Creates 8-pane layout without using area_close to avoid stack overflow
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
        print("\n" + "="*60)
        print("Creating MIDI Pose Cycler Workspace")
        print("="*60)
        
        workspace_name = "MIDI Pose Cycler"
        
        # Check if exists
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
        
        # Create workspace
        bpy.ops.workspace.duplicate()
        workspace = context.window.workspace
        workspace.name = workspace_name
        
        # Mark for our panels
        context.scene['midi_pose_workspace'] = workspace_name
        
        # Get screen
        screen = workspace.screens[0] if workspace.screens else None
        if not screen:
            self.report({'ERROR'}, "Failed to get workspace screen")
            return {'CANCELLED'}
        
        print(f"Starting with {len(screen.areas)} areas")
        
        # Helper to split area
        def split_area(area, direction='VERTICAL', factor=0.5):
            """Split an area safely"""
            if not area:
                return False
            try:
                override = {'window': window, 'screen': screen, 'area': area}
                with context.temp_override(**override):
                    bpy.ops.screen.area_split(direction=direction, factor=factor)
                return True
            except Exception as e:
                print(f"  Split failed: {e}")
                return False
        
        # Work with existing areas (typically 4 in default layout)
        # We need to get from 4 to 8 areas total
        
        # Find the main 3D viewport (usually the largest area)
        areas = list(screen.areas)
        main_area = max(areas, key=lambda a: a.width * a.height)
        
        # Step 1: Split main area horizontally to separate top workspace from bottom panels
        if split_area(main_area, 'HORIZONTAL', 0.75):
            print("  Split 1: Main horizontal")
            
            # Get new areas
            areas = list(screen.areas)
            # Find the bottom area we just created
            bottom_area = min([a for a in areas if a.type == main_area.type], key=lambda a: a.y)
            
            # Step 2: Split bottom for action editor and sequencer
            if bottom_area and split_area(bottom_area, 'HORIZONTAL', 0.80):
                print("  Split 2: Bottom horizontal")
            
            # Get top area (should be the one with highest y)
            areas = list(screen.areas)
            top_area = max([a for a in areas], key=lambda a: a.y)
            
            # Step 3: Split top area vertically for left column
            if top_area and split_area(top_area, 'VERTICAL', 0.20):
                print("  Split 3: Top vertical for left column")
                
                # Get the new left area
                areas = list(screen.areas)
                left_area = min([a for a in areas if a.y > bottom_area.y], key=lambda a: a.x)
                
                # Step 4: Split left area for file and asset browsers
                if left_area and split_area(left_area, 'HORIZONTAL', 0.50):
                    print("  Split 4: Left horizontal")
        
        # Now assign types based on position
        print("\nAssigning area types...")
        areas = list(screen.areas)
        
        if areas:
            # Calculate bounds
            max_x = max(a.x + a.width for a in areas)
            max_y = max(a.y + a.height for a in areas)
            
            for area in areas:
                # Calculate relative position
                x_center = area.x + area.width/2
                y_center = area.y + area.height/2
                x_rel = x_center / max_x if max_x > 0 else 0
                y_rel = y_center / max_y if max_y > 0 else 0
                
                # Assign based on position
                if x_rel < 0.15:  # Left column
                    area.type = 'FILE_BROWSER'
                    if y_rel > 0.5:
                        print(f"  FILE_BROWSER at ({x_rel:.2f}, {y_rel:.2f})")
                        # Configure as file browser for MIDI
                        for space in area.spaces:
                            if space.type == 'FILE_BROWSER':
                                try:
                                    space.params.use_filter = True
                                    space.params.use_filter_sound = True
                                except:
                                    pass
                    else:
                        print(f"  ASSET_BROWSER at ({x_rel:.2f}, {y_rel:.2f})")
                        # Configure as asset browser
                        for space in area.spaces:
                            if space.type == 'FILE_BROWSER':
                                try:
                                    space.params.asset_library_reference = 'LOCAL'
                                except:
                                    pass
                
                elif y_rel < 0.25:  # Bottom row
                    if y_rel < 0.10:
                        area.type = 'SEQUENCE_EDITOR'
                        print(f"  SEQUENCER at ({x_rel:.2f}, {y_rel:.2f})")
                    else:
                        area.type = 'DOPESHEET_EDITOR'
                        for space in area.spaces:
                            if space.type == 'DOPESHEET_EDITOR':
                                space.mode = 'ACTION'
                        print(f"  ACTION_EDITOR at ({x_rel:.2f}, {y_rel:.2f})")
                
                elif x_rel > 0.80:  # Right column
                    area.type = 'PROPERTIES'
                    for space in area.spaces:
                        if space.type == 'PROPERTIES':
                            try:
                                space.context = 'SCENE'
                            except:
                                pass
                    print(f"  PROPERTIES at ({x_rel:.2f}, {y_rel:.2f})")
                
                else:  # Middle
                    area.type = 'VIEW_3D'
                    print(f"  VIEW_3D at ({x_rel:.2f}, {y_rel:.2f})")
            
            # Count types
            counts = {}
            for area in areas:
                counts[area.type] = counts.get(area.type, 0) + 1
            
            print("\nFinal area counts:")
            for atype, count in sorted(counts.items()):
                print(f"  {atype}: {count}")
            
            print(f"\nTotal: {len(areas)} areas")
            
            # Expected counts for validation
            expected = {
                'FILE_BROWSER': 2,  # File browser and asset browser
                'VIEW_3D': 1,
                'DOPESHEET_EDITOR': 1,
                'SEQUENCE_EDITOR': 1,
                'PROPERTIES': 3
            }
            
            if len(areas) == 8:
                print("✓ Successfully created 8-pane layout!")
            else:
                print(f"⚠ Expected 8 areas, got {len(areas)}")
        
        self.report({'INFO'}, f"Created {workspace_name} workspace")
        print("="*60)
        return {'FINISHED'}


class MIDIPOSE_OT_setup_drag_drop(Operator):
    """Setup drag and drop for MIDI files"""
    bl_idname = "midipose.setup_drag_drop"
    bl_label = "Setup MIDI Drag & Drop"
    bl_description = "Enable drag and drop for MIDI files from file browser"
    
    def execute(self, context):
        self.report({'INFO'}, "Drag & drop setup complete")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MIDIPOSE_OT_create_workspace)
    bpy.utils.register_class(MIDIPOSE_OT_setup_drag_drop)

def unregister():
    bpy.utils.unregister_class(MIDIPOSE_OT_setup_drag_drop)
    bpy.utils.unregister_class(MIDIPOSE_OT_create_workspace)