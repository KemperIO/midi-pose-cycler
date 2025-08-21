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
        
        # Track list
        box = layout.box()
        
        for track in props.track_items:
            row = box.row(align=True)
            
            is_selected = track.name == props.selected_track
            
            # Radio button style selection
            icon = 'RADIOBUT_ON' if is_selected else 'RADIOBUT_OFF'
            op = row.operator("midipose.select_track", 
                             text="",
                             icon=icon,
                             emboss=False)
            op.track_name = track.name
            
            # Track info
            sub_row = row.row()
            sub_row.active = is_selected
            sub_row.alignment = 'LEFT'
            
            # Track name
            sub = sub_row.row()
            sub.scale_x = 1.5
            sub.label(text=track.name)
            
            # Note count
            sub_row.label(text=f"{track.note_count} notes")
        
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
        
        if not props.selected_track:
            box = layout.box()
            box.label(text="Select a track first", icon='INFO')
            return
        
        if not props.note_items:
            box = layout.box()
            box.label(text="No notes in selected track", icon='INFO')
            return
        
        layout.active = props.filter_notes
        
        if props.filter_notes:
            # Note Selection - Grid Flow
            box = layout.box()
            box.label(text="Select Notes:", icon='FILTER')
            
            # Quick selection
            row = box.row(align=True)
            row.operator("midipose.select_all_notes", text="All")
            row.operator("midipose.deselect_all_notes", text="None")
            row.operator("midipose.invert_note_selection", text="Invert")
            
            box.separator()
            
            # Use grid flow for note selection
            grid = box.grid_flow(columns=2, align=True)
            
            # Show notes with checkbox and info
            display_limit = 30
            for i, note in enumerate(props.note_items):
                if i >= display_limit:
                    break
                
                row = grid.row(align=True)
                row.prop(note, "selected", text="")
                
                # Note info with nickname if present
                if note.nickname:
                    row.label(text=f"{note.note_name} ({note.nickname}) [{note.count}]")
                else:
                    row.label(text=f"{note.note_name} [{note.count}]")
            
            if len(props.note_items) > display_limit:
                box.label(text=f"... and {len(props.note_items) - display_limit} more notes")
            
            # Nickname editing in separate section
            if any(n.selected for n in props.note_items):
                box.separator()
                nick_box = box.box()
                nick_box.label(text="Edit Nicknames:", icon='OUTLINER_DATA_GP_LAYER')
                
                # Only show selected notes for nickname editing
                selected_notes = [n for n in props.note_items if n.selected]
                for note in selected_notes[:10]:  # Limit to 10 for performance
                    row = nick_box.row(align=True)
                    row.label(text=f"{note.note_name}:")
                    row.prop(note, "nickname", text="")
                
                if len(selected_notes) > 10:
                    nick_box.label(text=f"... and {len(selected_notes) - 10} more selected notes")
            
            # Selected count
            selected_count = sum(1 for n in props.note_items if n.selected)
            layout.label(text=f"Using {selected_count} of {len(props.note_items)} notes")
        else:
            box = layout.box()
            box.label(text="Using all notes from track", icon='CHECKBOX_HLT')
            box.label(text="Enable filter to select specific notes")


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