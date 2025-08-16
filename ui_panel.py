import bpy
from bpy.types import Panel

class MIDIPOSE_PT_main_panel(Panel):
    """Main panel for MIDI Pose Cycler"""
    bl_label = "MIDI Pose Cycler"
    bl_idname = "MIDIPOSE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MIDI Pose"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.midi_pose_props
        
        # MIDI File Section
        box = layout.box()
        box.label(text="MIDI Input", icon='FILE_SOUND')
        
        row = box.row(align=True)
        if props.midi_file:
            import os
            row.label(text=os.path.basename(props.midi_file))
            row.operator("midipose.load_midi", text="", icon='FILE_FOLDER')
            row.operator("midipose.reload_midi", text="", icon='FILE_REFRESH')
        else:
            row.operator("midipose.load_midi", text="Load MIDI File", icon='FILE_FOLDER')
        
        
        # Settings Section
        box = layout.box()
        box.label(text="Settings", icon='SETTINGS')
        
        col = box.column(align=True)
        col.prop(props, "frames_to_hold")
        col.prop(props, "interpolation_type")
        col.prop(props, "total_frames")
        
        row = box.row()
        row.label(text=f"FPS: {scene.render.fps}")
        
        # Render Button
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator("midipose.render_animation", text="RENDER ANIMATION", icon='PLAY')

class MIDIPOSE_PT_track_selection(Panel):
    """Panel for track selection"""
    bl_label = "Track Selection"
    bl_idname = "MIDIPOSE_PT_track_selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MIDI Pose"
    bl_parent_id = "MIDIPOSE_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        props = context.scene.midi_pose_props
        return bool(props.track_items)
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        for track in props.track_items:
            row = layout.row()
            is_selected = track.name == props.selected_track
            
            # Create a button that both selects and analyzes
            icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
            op = row.operator("midipose.select_track", 
                            text=f"{track.name} ({track.note_count} notes)", 
                            icon=icon,
                            depress=is_selected)
            op.track_name = track.name

class MIDIPOSE_PT_poses(Panel):
    """Panel for pose selection"""
    bl_label = "Pose Selection"
    bl_idname = "MIDIPOSE_PT_poses"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MIDI Pose"
    bl_parent_id = "MIDIPOSE_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        self.layout.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH', emboss=False)
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        if props.pose_items:
            layout.label(text="Select poses (order matters):")
            for pose in props.pose_items:
                row = layout.row()
                row.prop(pose, "selected", text=pose.name)
        else:
            layout.label(text="No poses found.")
            layout.operator("midipose.refresh_poses", text="Refresh Poses", icon='FILE_REFRESH')

class MIDIPOSE_PT_note_filter(Panel):
    """Panel for note filtering"""
    bl_label = "Note Filter"
    bl_idname = "MIDIPOSE_PT_note_filter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MIDI Pose"
    bl_parent_id = "MIDIPOSE_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        props = context.scene.midi_pose_props
        return bool(props.note_items)
    
    def draw_header(self, context):
        props = context.scene.midi_pose_props
        self.layout.prop(props, "filter_notes", text="")
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        if props.filter_notes:
            for note in props.note_items:
                row = layout.row()
                row.prop(note, "selected", text=f"{note.note_name} ({note.count})")
        else:
            layout.label(text="Enable to filter specific notes")
            layout.label(text="(All notes will be used)")