"""
MIDI Pose Cycler - Node-Based Workspace Creator
Creates workspace with node editor for visual workflow
"""

import bpy
from bpy.types import Operator


class MIDIPOSE_OT_generate_node_workspace(Operator):
    """Generate fresh MIDI node workspace (F3 searchable)"""
    bl_idname = "mpc.generate_node_workspace"
    bl_label = "mpc-generate-node-workspace"
    bl_description = "Generate a new MIDI Pose Cycler node workspace"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Always create fresh workspace with unique name
        base_name = "Midi"
        workspace_name = base_name
        counter = 1
        
        while workspace_name in bpy.data.workspaces:
            workspace_name = f"{base_name}.{counter:03d}"
            counter += 1
        
        # Create new workspace from current
        bpy.ops.workspace.duplicate()
        workspace = context.window.workspace
        workspace.name = workspace_name
        
        # Get screen and window
        screen = workspace.screens[0] if workspace.screens else None
        window = context.window
        
        if not screen or not window:
            self.report({'ERROR'}, "Failed to get workspace screen or window")
            return {'CANCELLED'}
        
        # Skip clearing areas - just work with what we have
        # Trying to close areas can cause stack overflow in background mode
        
        if not screen.areas:
            self.report({'ERROR'}, "No areas left in workspace")
            return {'CANCELLED'}
        
        # Now build layout from single area
        main_area = screen.areas[0]
        
        # Create layout: 3x2 grid
        # [FILE] [NODE] [3D]
        # [ASSET][NODE] [OUTLINER]
        # [ACTION][ACTION][ACTION]
        # [SEQ]  [SEQ]  [SEQ]
        
        # Split horizontally: 70% top, 30% bottom
        override = {'area': main_area, 'window': window, 'screen': screen}
        with context.temp_override(**override):
            bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.7)
        
        areas = list(screen.areas)
        top = max(areas, key=lambda a: a.y) if areas else None
        bottom = min(areas, key=lambda a: a.y) if areas else None
        
        if top and bottom:
            # Split bottom: 66% action, 34% seq
            override = {'area': bottom, 'window': window, 'screen': screen}
            with context.temp_override(**override):
                bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.66)
            
            # Split top: 25% left, 75% right
            override = {'area': top, 'window': window, 'screen': screen}
            with context.temp_override(**override):
                bpy.ops.screen.area_split(direction='VERTICAL', factor=0.25)
            
            areas = list(screen.areas)
            top_areas = sorted([a for a in areas if a.y > screen.areas[0].height * 0.3], key=lambda a: a.x)
            
            if len(top_areas) >= 2:
                left_col = top_areas[0]
                right_area = top_areas[1]
                
                # Split right: 66% middle, 34% right
                override = {'area': right_area, 'window': window, 'screen': screen}
                with context.temp_override(**override):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.66)
                
                # Split left column
                override = {'area': left_col, 'window': window, 'screen': screen}
                with context.temp_override(**override):
                    bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.5)
                
                # Refresh areas
                areas = list(screen.areas)
                top_areas = sorted([a for a in areas if a.y > screen.areas[0].height * 0.3], key=lambda a: a.x)
                
                if len(top_areas) >= 3:
                    right_col = top_areas[-1]
                    # Split right column
                    override = {'area': right_col, 'window': window, 'screen': screen}
                    with context.temp_override(**override):
                        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.6)
        
        # Set area types with safety checks
        try:
            self.setup_area_types(screen)
        except Exception as e:
            print(f"Warning: Error setting area types: {e}")
        
        self.report({'INFO'}, f"Created {workspace_name} workspace")
        return {'FINISHED'}
    
    def setup_area_types(self, screen):
        """Configure area types based on position"""
        areas = list(screen.areas)
        
        # Create node tree if needed
        tree_name = "MidiPoseFlow"
        if tree_name not in bpy.data.node_groups:
            try:
                bpy.ops.midipose.new_node_tree(name=tree_name)
            except:
                # Create manually
                tree = bpy.data.node_groups.new(tree_name, 'MidiPoseNodeTree')
        
        node_tree = bpy.data.node_groups.get(tree_name)
        
        # Calculate relative positions
        max_x = max(a.x + a.width for a in areas) if areas else 1
        max_y = max(a.y + a.height for a in areas) if areas else 1
        
        for area in areas:
            x_rel = (area.x + area.width/2) / max_x
            y_rel = (area.y + area.height/2) / max_y
            
            # Bottom row: sequencer
            if y_rel < 0.08:
                area.type = 'SEQUENCE_EDITOR'
                
            # Second bottom: action editor
            elif y_rel < 0.25:
                area.type = 'DOPESHEET_EDITOR'
                for space in area.spaces:
                    if space.type == 'DOPESHEET_EDITOR':
                        space.mode = 'ACTION'
            
            # Top left: file/asset browsers - SKIP FOR NOW TO AVOID CRASH
            elif x_rel < 0.2:
                # File browser can crash on workspace switch
                # Just use properties panel instead
                area.type = 'PROPERTIES'
            
            # Top right: viewport/outliner
            elif x_rel > 0.7:
                if y_rel > 0.5:
                    area.type = 'VIEW_3D'
                else:
                    area.type = 'OUTLINER'
            
            # Middle: node editor
            else:
                area.type = 'NODE_EDITOR'
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        space.tree_type = 'MidiPoseNodeTree'
                        if node_tree:
                            space.node_tree = node_tree


def register():
    bpy.utils.register_class(MIDIPOSE_OT_generate_node_workspace)


def unregister():
    bpy.utils.unregister_class(MIDIPOSE_OT_generate_node_workspace)