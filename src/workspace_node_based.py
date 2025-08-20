"""
MIDI Pose Cycler - Node-Based Workspace Creator
Creates workspace with node editor for visual workflow
"""

import bpy
from bpy.types import Operator


class MIDIPOSE_OT_create_node_workspace(Operator):
    """Create MIDI Pose Cycler Node Workspace"""
    bl_idname = "midipose.create_node_workspace"
    bl_label = "Create Node Workspace"
    bl_description = "Create node-based workspace for MIDI pose animation"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        print("\n" + "="*60)
        print("Creating MIDI Pose Cycler Node Workspace")
        print("="*60)
        
        workspace_name = "MIDI Pose Nodes"
        
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
        context.scene['midi_pose_node_workspace'] = workspace_name
        
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
        
        # Find main area (usually largest)
        areas = list(screen.areas)
        main_area = max(areas, key=lambda a: a.width * a.height)
        
        # Layout according to spec:
        # | file browser  | node ui      | 3d viewport   |
        # | asset browser | node ui      | outliner      |
        # | action editor | action editor| action editor |
        # | sequencer     | sequencer    | sequencer     |
        
        # Step 1: Split horizontally for bottom section (75% top, 25% bottom)
        if split_area(main_area, 'HORIZONTAL', 0.75):
            print("  Split 1: Main horizontal for bottom section")
            
            areas = list(screen.areas)
            top_area = max(areas, key=lambda a: a.y)
            bottom_area = min(areas, key=lambda a: a.y)
            
            # Step 2: Split bottom for action editor and sequencer
            if bottom_area and split_area(bottom_area, 'HORIZONTAL', 0.70):
                print("  Split 2: Bottom for action/sequencer")
                
                # Get the two bottom areas
                bottom_areas = sorted([a for a in screen.areas if a.y < top_area.y], 
                                     key=lambda a: a.y, reverse=True)
                action_area = bottom_areas[0] if bottom_areas else None
                seq_area = bottom_areas[1] if len(bottom_areas) > 1 else None
            
            # Step 3: Split top into 3 columns (25% left, 50% middle, 25% right)
            if top_area and split_area(top_area, 'VERTICAL', 0.25):
                print("  Split 3: Top left column")
                
                areas = list(screen.areas)
                # Find the left and middle-right areas
                top_areas = [a for a in areas if a.y > (bottom_area.y if bottom_area else 0)]
                top_areas.sort(key=lambda a: a.x)
                left_col = top_areas[0] if top_areas else None
                middle_right = top_areas[1] if len(top_areas) > 1 else None
                
                # Step 4: Split middle-right (66% middle, 34% right)
                if middle_right and split_area(middle_right, 'VERTICAL', 0.66):
                    print("  Split 4: Middle and right columns")
                    
                    # Get all three columns
                    areas = list(screen.areas)
                    top_areas = [a for a in areas if a.y > (bottom_area.y if bottom_area else 0)]
                    top_areas.sort(key=lambda a: a.x)
                    
                    if len(top_areas) >= 3:
                        left_col = top_areas[0]
                        middle_col = top_areas[1]
                        right_col = top_areas[2]
                        
                        # Step 5: Split left column vertically
                        if split_area(left_col, 'HORIZONTAL', 0.50):
                            print("  Split 5: Left column for file/asset browsers")
                        
                        # Step 6: Split right column vertically
                        if split_area(right_col, 'HORIZONTAL', 0.70):
                            print("  Split 6: Right column for viewport/outliner")
        
        # Assign area types based on position
        print("\nAssigning area types...")
        areas = list(screen.areas)
        
        # Create or get node tree
        tree_name = "MidiPoseFlow"
        node_tree = bpy.data.node_groups.get(tree_name)
        if not node_tree:
            # Create new tree with default nodes
            bpy.ops.midipose.new_node_tree(name=tree_name)
            node_tree = bpy.data.node_groups.get(tree_name)
        
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
                
                # Very bottom = sequencer
                if y_rel < 0.08:
                    area.type = 'SEQUENCE_EDITOR'
                    for space in area.spaces:
                        if space.type == 'SEQUENCE_EDITOR':
                            space.view_type = 'SEQUENCER'
                    print(f"  SEQUENCER at ({x_rel:.2f}, {y_rel:.2f})")
                
                # Bottom = action editor
                elif y_rel < 0.25:
                    area.type = 'DOPESHEET_EDITOR'
                    for space in area.spaces:
                        if space.type == 'DOPESHEET_EDITOR':
                            space.mode = 'ACTION'
                    print(f"  ACTION_EDITOR at ({x_rel:.2f}, {y_rel:.2f})")
                
                # Left column
                elif x_rel < 0.20:
                    area.type = 'FILE_BROWSER'
                    if y_rel > 0.50:
                        print(f"  FILE_BROWSER at ({x_rel:.2f}, {y_rel:.2f})")
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
                                    # Would set to asset mode
                                    pass
                                except:
                                    pass
                
                # Right column
                elif x_rel > 0.70:
                    if y_rel > 0.50:
                        area.type = 'VIEW_3D'
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.shading.type = 'SOLID'
                        print(f"  VIEW_3D at ({x_rel:.2f}, {y_rel:.2f})")
                    else:
                        area.type = 'OUTLINER'
                        print(f"  OUTLINER at ({x_rel:.2f}, {y_rel:.2f})")
                
                # Middle = Node editor
                else:
                    area.type = 'NODE_EDITOR'
                    for space in area.spaces:
                        if space.type == 'NODE_EDITOR':
                            space.tree_type = 'MidiPoseNodeTree'
                            space.node_tree = node_tree
                            space.show_region_ui = True
                    print(f"  NODE_EDITOR at ({x_rel:.2f}, {y_rel:.2f})")
            
            # Count types
            counts = {}
            for area in areas:
                counts[area.type] = counts.get(area.type, 0) + 1
            
            print("\nFinal area counts:")
            for atype, count in sorted(counts.items()):
                print(f"  {atype}: {count}")
            
            print(f"\nTotal: {len(areas)} areas")
            
            # Expected: 
            # 2 FILE_BROWSER (file + asset)
            # 1 NODE_EDITOR
            # 1 VIEW_3D
            # 1 OUTLINER
            # 1 DOPESHEET_EDITOR
            # 1 SEQUENCE_EDITOR
            # = 7 total
        
        self.report({'INFO'}, f"Created {workspace_name} workspace")
        print("="*60)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MIDIPOSE_OT_create_node_workspace)


def unregister():
    bpy.utils.unregister_class(MIDIPOSE_OT_create_node_workspace)