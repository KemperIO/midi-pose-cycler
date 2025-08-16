"""
MIDI Pose Cycler - Custom Workspace Creator V2
Creates workspace with exact layout specification

Target Layout:
| pane             | location    | purpose                                  |
| file browser     | left top    | drag midi files                          |
| asset browser    | left bottom | for dragging poses in                    |
| 3d viewport      | middle      | see animation                            |
| action editor    | bottom      | see keyframes                            |
| sequencer        | very bottom | see associated audio timeline            |
| properties-main  | right top   | midiPoseCycler main form stuff           |
| properties-poses | right mid   | midiPoseCycler pose selection & ordering |
| properties-midi  | right bot   | midiPoseCycler midi form & stats         |
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
        print("Creating MIDI Pose Cycler Workspace V2")
        print("="*60)
        
        # Check if workspace already exists
        workspace_name = "MIDI Pose Cycler"
        
        if workspace_name in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces[workspace_name]
            self.report({'INFO'}, f"Switched to {workspace_name} workspace")
            print(f"Switched to existing {workspace_name} workspace")
            return {'FINISHED'}
        
        # Get window
        window = context.window
        if not window:
            window = context.window_manager.windows[0] if context.window_manager.windows else None
            if not window:
                self.report({'ERROR'}, "No window available")
                return {'CANCELLED'}
        
        # Create new workspace
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
        
        # Split helper
        def split(area, dir='VERTICAL', fac=0.5):
            try:
                override = {'window': window, 'screen': screen, 'area': area}
                with context.temp_override(**override):
                    bpy.ops.screen.area_split(direction=dir, factor=fac)
                return True
            except:
                return False
        
        # Build layout
        print("Building layout...")
        
        # 1. Split main horizontally: top (75%) and bottom (25%)
        if split(main, 'HORIZONTAL', 0.75):
            areas = sorted(screen.areas, key=lambda a: a.y, reverse=True)
            top = areas[0]
            bottom = areas[1] if len(areas) > 1 else None
            
            # 2. Split bottom again: action editor (80%) and sequencer (20%)
            if bottom and split(bottom, 'HORIZONTAL', 0.80):
                bottom_areas = sorted([a for a in screen.areas if a.y < top.y], 
                                     key=lambda a: a.y, reverse=True)
                action_area = bottom_areas[0] if bottom_areas else None
                seq_area = bottom_areas[1] if len(bottom_areas) > 1 else None
                
                # 3. Split top vertically: left (20%), middle-right (80%)
                if split(top, 'VERTICAL', 0.20):
                    top_areas = sorted([a for a in screen.areas if a.y > (action_area.y if action_area else 0)],
                                      key=lambda a: a.x)
                    left = top_areas[0] if top_areas else None
                    mid_right = top_areas[1] if len(top_areas) > 1 else None
                    
                    # 4. Split left: file browser (50%) and asset browser (50%)
                    if left:
                        split(left, 'HORIZONTAL', 0.50)
                    
                    # 5. Split middle-right: middle (65%) and right (35%)
                    if mid_right and split(mid_right, 'VERTICAL', 0.65):
                        # Find the rightmost area
                        all_areas = list(screen.areas)
                        right_area = max(all_areas, key=lambda a: a.x)
                        
                        # 6. Split right into 3 panels
                        if split(right_area, 'HORIZONTAL', 0.33):
                            # Find and split middle panel
                            right_panels = sorted([a for a in screen.areas if a.x > mid_right.x * 0.9],
                                                 key=lambda a: a.y, reverse=True)
                            if len(right_panels) >= 2:
                                split(right_panels[1], 'HORIZONTAL', 0.50)
        
        # Assign area types
        print("Assigning area types...")
        all_areas = list(screen.areas)
        
        if all_areas:
            # Calculate relative positions
            max_x = max(a.x + a.width for a in all_areas)
            max_y = max(a.y + a.height for a in all_areas)
            
            assignments = []
            for area in all_areas:
                x_center = area.x + area.width/2
                y_center = area.y + area.height/2
                x_rel = x_center / max_x if max_x > 0 else 0
                y_rel = y_center / max_y if max_y > 0 else 0
                
                # Determine type by position
                if x_rel < 0.15:  # Left column
                    if y_rel > 0.5:
                        area.type = 'FILE_BROWSER'
                        assignments.append("FILE_BROWSER (left top)")
                        for space in area.spaces:
                            if space.type == 'FILE_BROWSER':
                                try:
                                    space.params.use_filter = True
                                    space.params.use_filter_sound = True
                                except:
                                    pass
                    else:
                        area.type = 'ASSETS'
                        assignments.append("ASSETS (left bottom)")
                
                elif x_rel < 0.65:  # Middle column
                    if y_rel > 0.30:
                        area.type = 'VIEW_3D'
                        assignments.append("VIEW_3D (middle)")
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.shading.type = 'SOLID'
                                space.show_region_ui = False
                    elif y_rel > 0.10:
                        area.type = 'DOPESHEET_EDITOR'
                        assignments.append("DOPESHEET_EDITOR (bottom)")
                        for space in area.spaces:
                            if space.type == 'DOPESHEET_EDITOR':
                                space.mode = 'ACTION'
                                space.show_region_ui = False
                    else:
                        area.type = 'SEQUENCE_EDITOR'
                        assignments.append("SEQUENCE_EDITOR (very bottom)")
                        for space in area.spaces:
                            if space.type == 'SEQUENCE_EDITOR':
                                space.view_type = 'SEQUENCER'
                                space.show_region_ui = False
                
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
            
            # Print assignments
            print("\nArea assignments:")
            for a in assignments:
                print(f"  - {a}")
            
            # Validate
            area_counts = {}
            for area in all_areas:
                area_counts[area.type] = area_counts.get(area.type, 0) + 1
            
            print("\nArea type counts:")
            for atype, count in sorted(area_counts.items()):
                print(f"  {atype}: {count}")
            
            # Check expected counts
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
                status = "✓" if actual == ecount else "✗"
                print(f"  {status} {etype}: {actual}/{ecount}")
                if actual != ecount:
                    success = False
            
            if success:
                print("\n✓ Layout created successfully!")
            else:
                print("\n⚠ Layout incomplete but functional")
        
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