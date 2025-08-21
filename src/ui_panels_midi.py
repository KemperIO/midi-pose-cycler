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
        
        # Track list with multi-selection
        box = layout.box()
        box.label(text="Select Tracks:", icon='NLA_PUSHDOWN')
        
        for track in props.track_items:
            # Main row for track
            col = box.column()
            row = col.row(align=False)  # Don't align tightly
            
            # Checkbox for selection - fixed width
            sub = row.row()
            sub.alignment = 'LEFT'
            sub.scale_x = 0.3  # Smaller checkbox area
            sub.prop(track, "selected", text="")
            
            # Track name - separate column with proper spacing
            sub = row.row()
            sub.active = track.selected
            sub.alignment = 'LEFT'
            sub.scale_x = 1.5
            sub.label(text=track.name)
            
            # Note count
            if track.filter_notes:
                selected_notes = sum(1 for n in track.note_filters if n.selected)
                sub_row.label(text=f"{selected_notes}/{track.note_count} notes")
            else:
                sub_row.label(text=f"{track.note_count} notes")
            
            # Note filter toggle
            if track.selected:
                row.prop(track, "filter_notes", text="", icon='FILTER', toggle=True)
                
                # Show note filter dropdown if enabled
                if track.filter_notes:
                    filter_box = col.box()
                    filter_box.scale_y = 0.9
                    
                    # Quick selection
                    row = filter_box.row(align=True)
                    row.scale_y = 0.8
                    
                    op = row.operator("midipose.select_all_track_notes", text="All")
                    op.track_name = track.name
                    
                    op = row.operator("midipose.deselect_all_track_notes", text="None")
                    op.track_name = track.name
                    
                    op = row.operator("midipose.invert_track_notes", text="Invert")
                    op.track_name = track.name
                    
                    # Note grid
                    grid = filter_box.grid_flow(columns=2, align=True)
                    for note_filter in track.note_filters[:10]:  # Limit display
                        row = grid.row(align=True)
                        row.prop(note_filter, "selected", text="")
                        row.label(text=f"{note_filter.note_name}")
                    
                    if len(track.note_filters) > 10:
                        filter_box.label(text=f"... and {len(track.note_filters) - 10} more notes")
        
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
    """Note filtering panel"""
    bl_label = "Note Filter"
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
        
        # Show note filters for each selected track
        for track in selected_tracks:
            box = layout.box()
            
            # Track header with filter toggle
            row = box.row()
            row.label(text=f"{track.name}:", icon='NLA_PUSHDOWN')
            row.prop(track, "filter_notes", text="Filter", toggle=True)
            
            if track.filter_notes and track.note_filters:
                # Quick selection buttons
                row = box.row(align=True)
                row.scale_y = 0.8
                
                op = row.operator("midipose.select_all_track_notes", text="All")
                op.track_name = track.name
                
                op = row.operator("midipose.deselect_all_track_notes", text="None")
                op.track_name = track.name
                
                op = row.operator("midipose.invert_track_notes", text="Invert")
                op.track_name = track.name
                
                # Note selection grid
                grid = box.grid_flow(columns=2, align=True)
                
                display_limit = 12
                for i, note_filter in enumerate(track.note_filters):
                    if i >= display_limit:
                        break
                    
                    row = grid.row(align=True)
                    row.prop(note_filter, "selected", text="")
                    row.label(text=note_filter.note_name)
                
                if len(track.note_filters) > display_limit:
                    box.label(text=f"... and {len(track.note_filters) - display_limit} more notes")
                
                # Summary
                selected_notes = sum(1 for n in track.note_filters if n.selected)
                box.label(text=f"Using {selected_notes}/{len(track.note_filters)} notes")
            else:
                # Not filtering
                info = box.row()
                info.scale_y = 0.8
                info.label(text=f"Using all {track.note_count} notes", icon='CHECKBOX_HLT')


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