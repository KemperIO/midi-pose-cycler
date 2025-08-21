"""
MIDI Pose Cycler - MIDI Tab
MIDI file loading, track selection, and note filtering
"""

import bpy
from bpy.types import Panel
import os

# Base class
class MidiPosePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MPC-MIDI"
    
    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'POSE')


# MIDI FILE PANEL
class MIDIPOSE_PT_midi_file(Panel, MidiPosePanel):
    """MIDI file loading panel"""
    bl_label = "MIDI File"
    bl_idname = "MIDIPOSE_PT_midi_file"
    bl_order = 0
    
    def draw_header(self, context):
        self.layout.label(text="", icon='FILE_SOUND')
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        if props.midi_file:
            # File loaded
            box = layout.box()
            box.label(text="Current File:", icon='FILE_TICK')
            box.label(text=os.path.basename(props.midi_file))
            
            # File path (truncated if too long)
            file_dir = os.path.dirname(props.midi_file)
            if len(file_dir) > 40:
                file_dir = "..." + file_dir[-37:]
            box.label(text=file_dir)
            
            layout.separator()
            
            # File actions
            row = layout.row(align=True)
            row.operator("midipose.load_midi", text="Change File", icon='FILE_FOLDER')
            row.operator("midipose.reload_midi", text="Reload", icon='FILE_REFRESH')
            
            # File info
            if props.track_items:
                layout.separator()
                info_box = layout.box()
                info_box.scale_y = 0.9
                info_box.label(text=f"Tracks: {len(props.track_items)}", icon='NLA')
                
                # Calculate total notes
                total_notes = sum(t.note_count for t in props.track_items)
                info_box.label(text=f"Total Notes: {total_notes}", icon='DOT')
        else:
            # No file loaded
            box = layout.box()
            box.label(text="No MIDI file loaded", icon='INFO')
            box.separator()
            
            # Load button
            box.operator("midipose.load_midi", text="Load MIDI File", icon='FILEBROWSER')
            box.label(text="Or drag from File Browser", icon='MOUSE_LMB_DRAG')
            
            # Tips
            box.separator()
            box.label(text="Supported formats:", icon='FILE_SOUND')
            box.label(text="• .mid")
            box.label(text="• .midi")


# TRACK SELECTION PANEL
class MIDIPOSE_PT_midi_tracks(Panel, MidiPosePanel):
    """Track selection panel"""
    bl_label = "Track Selection"
    bl_idname = "MIDIPOSE_PT_midi_tracks"
    bl_order = 1
    
    def draw_header(self, context):
        self.layout.label(text="", icon='NLA')
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        if not props.midi_file:
            box = layout.box()
            box.label(text="Load a MIDI file first", icon='INFO')
            return
        
        if not props.track_items:
            box = layout.box()
            box.label(text="No tracks found", icon='ERROR')
            box.operator("midipose.reload_midi", text="Reload File", icon='FILE_REFRESH')
            return
        
        # Track list with grid flow for better multi-selection
        box = layout.box()
        box.label(text="Select Tracks:", icon='NLA_PUSHDOWN')
        
        # Use grid flow for track checkboxes
        grid = box.grid_flow(columns=2, align=True)
        for track in props.track_items:
            row = grid.row(align=True)
            row.prop(track, "selected", text=track.name)
            if track.note_count:
                row.label(text=f"({track.note_count})")
        
        # Selected track info
        if props.selected_track:
            layout.separator()
            info_box = layout.box()
            info_box.label(text="Active Track:", icon='CHECKMARK')
            
            row = info_box.row()
            row.label(text=props.selected_track, icon='NLA_PUSHDOWN')
            
            # Track statistics
            if props.note_items:
                total_notes = sum(n.count for n in props.note_items)
                unique_notes = len(props.note_items)
                
                col = info_box.column()
                col.scale_y = 0.9
                col.label(text=f"Total events: {total_notes}")
                col.label(text=f"Unique notes: {unique_notes}")


# NOTE FILTERING PANEL
class MIDIPOSE_PT_midi_notes(Panel, MidiPosePanel):
    """Tone filtering panel"""
    bl_label = "Tone Filter"
    bl_idname = "MIDIPOSE_PT_midi_notes"
    bl_order = 2
    
    def draw_header(self, context):
        props = context.scene.midi_pose_props
        row = self.layout.row(align=True)
        row.label(text="", icon='FILTER')
        row.prop(props, "filter_notes", text="")
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        # Get selected tracks
        selected_tracks = [t for t in props.track_items if t.selected]
        
        if not selected_tracks:
            box = layout.box()
            box.label(text="No tracks selected", icon='INFO')
            box.label(text="Select tracks in the Track Selection panel above")
            return
        
        # Show collapsible note filters for each selected track
        for track in selected_tracks:
            box = layout.box()
            
            # Track header with collapsible filter toggle
            row = box.row(align=True)
            
            # Collapse/expand icon
            icon = 'TRIA_DOWN' if track.filter_notes else 'TRIA_RIGHT'
            row.prop(track, "filter_notes", text="", icon=icon, emboss=False)
            
            # Track name and info
            if track.is_dynamic:
                row.label(text=f"{track.name}", icon='TIME')
            else:
                row.label(text=f"{track.name}", icon='NLA_PUSHDOWN')
            
            # Note count summary
            if track.is_dynamic:
                # Show dynamic track settings
                props = context.scene.midi_pose_props
                if props.dynamic_interval_type == 'BEATS':
                    row.label(text=f"(Every {props.dynamic_interval_beats} beats)")
                else:
                    row.label(text=f"(Every {props.dynamic_interval_bars} bars)")
            elif track.filter_notes and track.note_filters:
                selected_notes = sum(1 for n in track.note_filters if n.selected)
                row.label(text=f"({selected_notes}/{len(track.note_filters)} notes)")
            else:
                row.label(text=f"({track.note_count} notes)")
            
            # Collapsible content
            if track.is_dynamic and track.filter_notes:
                # Show dynamic track configuration
                filter_box = box.box()
                filter_box.scale_y = 0.95
                
                props = context.scene.midi_pose_props
                
                # Interval type selector
                row = filter_box.row()
                row.label(text="Generate event every:")
                row.prop(props, "dynamic_interval_type", text="")
                
                # Interval amount
                if props.dynamic_interval_type == 'BEATS':
                    filter_box.prop(props, "dynamic_interval_beats", text="Beats")
                else:
                    filter_box.prop(props, "dynamic_interval_bars", text="Bars")
                
                # Info
                filter_box.separator(factor=0.5)
                info = filter_box.row()
                info.scale_y = 0.8
                info.label(text=f"BPM: {props.bpm}", icon='TIME')
                
            elif track.filter_notes and track.note_filters:
                # Inner box for filter content
                filter_box = box.box()
                filter_box.scale_y = 0.95
                
                # Quick selection buttons
                button_row = filter_box.row(align=True)
                button_row.scale_y = 0.9
                
                op = button_row.operator("midipose.select_all_track_notes", text="All")
                op.track_name = track.name
                
                op = button_row.operator("midipose.deselect_all_track_notes", text="None")
                op.track_name = track.name
                
                op = button_row.operator("midipose.invert_track_notes", text="Invert")
                op.track_name = track.name
                
                filter_box.separator(factor=0.5)
                
                # Tone selection grid - show tone name with MIDI number
                note_grid = filter_box.grid_flow(columns=2, align=True)
                
                display_limit = 12
                for i, note_filter in enumerate(track.note_filters):
                    if i >= display_limit:
                        break
                    
                    # Format: "C3 (60)" - tone name with MIDI number
                    label = f"{note_filter.note_name} ({note_filter.note_number})"
                    note_grid.prop(note_filter, "selected", text=label)
                
                if len(track.note_filters) > display_limit:
                    filter_box.label(text=f"... and {len(track.note_filters) - display_limit} more notes", icon='INFO')


# Registration
classes = [
    MIDIPOSE_PT_midi_file,
    MIDIPOSE_PT_midi_tracks,
    MIDIPOSE_PT_midi_notes,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)