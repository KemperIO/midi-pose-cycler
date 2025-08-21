"""
MIDI Pose Cycler - Pose Tab
Pose selection, ordering, and cycle management
"""

import bpy
from bpy.types import Panel

# Base class
class MidiPosePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MPC-Pose"
    
    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'POSE')


# POSE SELECTION PANEL
class MIDIPOSE_PT_pose_selection(Panel, MidiPosePanel):
    """Pose selection panel"""
    bl_label = "Pose Selection"
    bl_idname = "MIDIPOSE_PT_pose_selection"
    bl_order = 0
    
    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.label(text="", icon='ARMATURE_DATA')
        row.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH', emboss=False)
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        if not props.pose_items:
            box = layout.box()
            box.label(text="No poses found in project", icon='INFO')
            box.operator("midipose.refresh_poses", text="Scan for Pose Actions", icon='VIEWZOOM')
            box.separator()
            box.label(text="Tips:", icon='QUESTION')
            box.label(text="• Create actions with poses")
            box.label(text="• Name them descriptively")
            box.label(text="• Drag from Asset Browser")
            return
        
        # Quick selection tools
        row = layout.row(align=True)
        row.operator("midipose.select_all_poses", text="All")
        row.operator("midipose.deselect_all_poses", text="None")
        row.operator("midipose.invert_pose_selection", text="Invert")
        
        layout.separator()
        
        # Pose Selection - Grid Flow
        box = layout.box()
        box.label(text="Available Poses:", icon='CHECKBOX_HLT')
        
        # Use grid flow for pose selection
        grid = box.grid_flow(columns=2, align=True)
        
        for pose in props.pose_items:
            # Check if action exists
            action = bpy.data.actions.get(pose.name)
            icon = 'ACTION' if action else 'POSE_HLT'
            
            # Create row for checkbox and label
            row = grid.row(align=True)
            row.prop(pose, "selected", text="")
            row.label(text=pose.name, icon=icon)
        
        # Summary
        layout.separator()
        selected_count = sum(1 for p in props.pose_items if p.selected)
        
        col = layout.column()
        col.label(text=f"Total: {len(props.pose_items)} poses")
        col.label(text=f"Selected: {selected_count} poses")


# POSE ORDERING PANEL
class MIDIPOSE_PT_pose_order(Panel, MidiPosePanel):
    """Pose ordering panel"""
    bl_label = "Pose Order"
    bl_idname = "MIDIPOSE_PT_pose_order"
    bl_order = 1
    
    def draw_header(self, context):
        self.layout.label(text="", icon='SORT_ASC')
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        # Get selected poses
        selected_poses = [p for p in props.pose_items if p.selected]
        
        if not selected_poses:
            box = layout.box()
            box.label(text="No poses selected", icon='INFO')
            box.label(text="Select poses above to set order")
            return
        
        # Sort selected poses by order_index for display
        selected_poses.sort(key=lambda p: p.order_index)
        
        # Order list
        box = layout.box()
        box.label(text=f"Animation Sequence ({len(selected_poses)} poses):", icon='NLA')
        
        for i, pose in enumerate(selected_poses):
            row = box.row(align=False)
            row.alignment = 'LEFT'
            
            # Order number with better visibility
            sub = row.row()
            sub.scale_x = 0.8
            sub.label(text=f"{i+1}.")
            
            # Pose name - take more space
            sub = row.row()
            sub.scale_x = 2.0
            icon = 'ACTION' if bpy.data.actions.get(pose.name) else 'POSE_HLT'
            sub.label(text=pose.name, icon=icon)
            
            # Spacer to push buttons to the right
            row.separator()
            
            # Move up button - larger and more visible
            sub = row.row(align=True)
            sub.scale_x = 1.2
            sub.scale_y = 1.2
            up_op = sub.operator("midipose.move_pose", text="", icon='TRIA_UP')
            up_op.direction = 'UP'
            up_op.pose_name = pose.name
            sub.enabled = i > 0
            
            # Move down button - larger and more visible
            down_op = sub.operator("midipose.move_pose", text="", icon='TRIA_DOWN')
            down_op.direction = 'DOWN'
            down_op.pose_name = pose.name
            sub.enabled = i < len(selected_poses) - 1


# CYCLE SETTINGS PANEL
class MIDIPOSE_PT_pose_cycle(Panel, MidiPosePanel):
    """Cycle mode settings"""
    bl_label = "Cycle Settings"
    bl_idname = "MIDIPOSE_PT_pose_cycle"
    bl_order = 2
    
    def draw_header(self, context):
        self.layout.label(text="", icon='RECOVER_LAST')
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        # Cycle mode
        row = layout.row()
        row.label(text="Cycle Mode:")
        row.prop(props, "pose_cycle_mode", text="")
        
        # Cycle explanation
        box = layout.box()
        if props.pose_cycle_mode == 'LOOP':
            box.label(text="Poses will cycle in order", icon='LOOP_FORWARDS')
            box.label(text="1 → 2 → 3 → 1 → 2 → 3...")
        elif props.pose_cycle_mode == 'BOOMERANG':
            box.label(text="Forward then backward", icon='LOOP_BACK')
            box.label(text="1 → 2 → 3 → 2 → 1 → 2...")
        elif props.pose_cycle_mode == 'RANDOM':
            box.label(text="Random pose selection", icon='SHADERFX')
            box.label(text="Unpredictable sequence")
        
        # Animation mode info
        layout.separator()
        box = layout.box()
        box.label(text="Animation Mode:", icon='ACTION')
        
        row = box.row()
        row.prop(props, "animation_mode", expand=True)
        
        if props.animation_mode == 'POSE':
            box.label(text="• Single frame poses")
            box.label(text="• Extracted from frame 0")
            box.label(text="• Transitions between poses")
        else:
            box.label(text="• Full action playback")
            box.label(text="• All keyframes preserved")
            box.label(text="• Original timing maintained")


# Registration
classes = [
    MIDIPOSE_PT_pose_selection,
    MIDIPOSE_PT_pose_order,
    MIDIPOSE_PT_pose_cycle,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)