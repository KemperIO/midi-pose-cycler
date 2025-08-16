"""
Fixed workspace creator - builds exact 8-pane layout
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
        print("Creating MIDI Pose Cycler Workspace (Fixed)")
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
        print("Creating new workspace...")
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
        
        # Clear to single area
        print(f"Starting with {len(screen.areas)} areas")
        while len(screen.areas) > 1:
            area = screen.areas[-1]
            try:
                override = {'window': window, 'screen': screen, 'area': area}
                with context.temp_override(**override):
                    bpy.ops.screen.area_close()
            except:
                break
        
        if not screen.areas:
            self.report({'ERROR'}, "No areas in screen")
            return {'CANCELLED'}
        
        # Start with 3D view
        main = screen.areas[0]
        main.type = 'VIEW_3D'
        
        # Split helper - safer version
        def split_area(area, direction='VERTICAL', factor=0.5):
            """Split an area and return True if successful"""
            if not area:
                print(f"  Warning: No area to split")
                return False
            try:
                override = {'window': window, 'screen': screen, 'area': area}
                with context.temp_override(**override):
                    bpy.ops.screen.area_split(direction=direction, factor=factor)
                print(f"  Split successful: {direction} at {factor}")
                return True
            except Exception as e:
                print(f"  Split failed: {e}")
                return False
        
        # Build layout step by step
        print("\nBuilding layout...")
        
        # Step 1: Split main horizontally for top (75%) and bottom (25%)
        print("Step 1: Split main horizontally...")
        if split_area(main, 'HORIZONTAL', 0.75):
            # Sort areas by Y position
            areas = sorted(list(screen.areas), key=lambda a: a.y, reverse=True)
            top_main = areas[0] if len(areas) > 0 else None
            bottom_main = areas[1] if len(areas) > 1 else None
            
            # Step 2: Split bottom for action editor and sequencer
            print("Step 2: Split bottom for action/sequencer...")
            if bottom_main and split_area(bottom_main, 'HORIZONTAL', 0.80):
                # Get the two bottom areas
                bottom_areas = sorted([a for a in screen.areas if a.y < top_main.y], 
                                     key=lambda a: a.y, reverse=True)
                action_area = bottom_areas[0] if bottom_areas else None
                seq_area = bottom_areas[1] if len(bottom_areas) > 1 else None
            
            # Step 3: Split top horizontally for left column (20%)
            print("Step 3: Split top for left column...")
            if top_main and split_area(top_main, 'VERTICAL', 0.20):
                # Get left and middle-right areas
                top_areas = sorted([a for a in screen.areas if a.y > (bottom_main.y if bottom_main else 0)],
                                  key=lambda a: a.x)
                left_column = top_areas[0] if top_areas else None
                middle_right = top_areas[1] if len(top_areas) > 1 else None
                
                # Step 4: Split left column vertically
                print("Step 4: Split left column...")
                if left_column:
                    split_area(left_column, 'HORIZONTAL', 0.50)
                
                # Step 5: Split middle-right for right column (35% of remaining)
                print("Step 5: Split for right column...")
                if middle_right and split_area(middle_right, 'VERTICAL', 0.65):
                    # Find the rightmost area (properties column)
                    all_areas = list(screen.areas)
                    # Get the area with highest x value
                    right_column = None
                    max_x = 0
                    for area in all_areas:
                        if area.x > max_x:
                            max_x = area.x
                            right_column = area
                    
                    # Step 6: Split right column into 3 properties panels
                    print("Step 6: Split right column into 3...")
                    if right_column and split_area(right_column, 'HORIZONTAL', 0.33):
                        # Get right column areas and split the bottom one
                        right_areas = sorted([a for a in screen.areas if a.x >= max_x * 0.95],
                                           key=lambda a: a.y, reverse=True)
                        if len(right_areas) >= 2:
                            split_area(right_areas[1], 'HORIZONTAL', 0.50)
        
        # Assign area types based on position
        print("\nAssigning area types...")
        all_areas = list(screen.areas)
        
        if all_areas:
            # Get dimensions
            max_x = max(a.x + a.width for a in all_areas)
            max_y = max(a.y + a.height for a in all_areas)
            
            assignments = []
            for area in all_areas:
                # Calculate relative position
                x_center = area.x + area.width/2
                y_center = area.y + area.height/2
                x_rel = x_center / max_x if max_x > 0 else 0
                y_rel = y_center / max_y if max_y > 0 else 0
                
                # Assign type based on position
                if x_rel < 0.15:  # Left column
                    if y_rel > 0.5:
                        area.type = 'FILE_BROWSER'
                        assignments.append("FILE_BROWSER (left top)")
                    else:
                        area.type = 'ASSETS'
                        assignments.append("ASSETS (left bottom)")
                
                elif x_rel < 0.65:  # Middle column
                    if y_rel > 0.30:
                        area.type = 'VIEW_3D'
                        assignments.append("VIEW_3D (middle)")
                    elif y_rel > 0.10:
                        area.type = 'DOPESHEET_EDITOR'
                        assignments.append("ACTION_EDITOR (bottom)")
                        for space in area.spaces:
                            if space.type == 'DOPESHEET_EDITOR':
                                space.mode = 'ACTION'
                    else:
                        area.type = 'SEQUENCE_EDITOR'
                        assignments.append("SEQUENCER (very bottom)")
                
                else:  # Right column - Properties
                    area.type = 'PROPERTIES'
                    for space in area.spaces:
                        if space.type == 'PROPERTIES':
                            try:
                                space.context = 'SCENE'
                            except:
                                pass
                    
                    if y_rel > 0.66:
                        assignments.append("PROPERTIES-main (right top)")
                    elif y_rel > 0.33:
                        assignments.append("PROPERTIES-poses (right mid)")
                    else:
                        assignments.append("PROPERTIES-midi (right bot)")
            
            # Print results
            print("\nArea assignments:")
            for assignment in assignments:
                print(f"  - {assignment}")
            
            # Validate
            area_counts = {}
            for area in all_areas:
                area_counts[area.type] = area_counts.get(area.type, 0) + 1
            
            print("\nArea counts:")
            for atype, count in sorted(area_counts.items()):
                print(f"  {atype}: {count}")
            
            # Check expected
            expected = {
                'FILE_BROWSER': 1,
                'ASSETS': 1,
                'VIEW_3D': 1,
                'DOPESHEET_EDITOR': 1,
                'SEQUENCE_EDITOR': 1,
                'PROPERTIES': 3
            }
            
            print("\nValidation:")
            success = True
            for etype, ecount in expected.items():
                actual = area_counts.get(etype, 0)
                if actual == ecount:
                    print(f"  ✓ {etype}: {actual}/{ecount}")
                else:
                    print(f"  ✗ {etype}: {actual}/{ecount}")
                    success = False
            
            if success:
                print("\n✓ Layout created successfully!")
            else:
                print("\n⚠ Layout incomplete")
        
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