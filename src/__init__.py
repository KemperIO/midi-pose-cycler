bl_info = {
    "name": "MIDI Pose Cycler",
    "author": "Voldemort Project",
    "version": (0, 5, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > MidiPoseCycler",
    "description": "Animate a loop of poses to MIDI events",
    "category": "Animation",
}

import bpy
from bpy.props import PointerProperty
import importlib
import sys
import os

# Ensure vendor path is in sys.path for mido
addon_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(addon_dir)
vendor_dir = os.path.join(parent_dir, 'vendor')
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

# Import all modules with reload for development
from . import midi_core
from . import animation_renderer
from . import config_manager
from . import ui_operators
from . import ui_properties_panels

# Reload modules for development (helps with updates)
importlib.reload(midi_core)
importlib.reload(animation_renderer)
importlib.reload(config_manager)
importlib.reload(ui_operators)
importlib.reload(ui_properties_panels)

# Classes to register
classes = [
    # Property Groups
    ui_operators.TrackItem,
    ui_operators.NoteItem,
    ui_operators.PoseItem,
    ui_operators.MidiPoseProperties,
    
    # Operators
    ui_operators.MIDIPOSE_OT_load_midi,
    ui_operators.MIDIPOSE_OT_reload_midi,
    ui_operators.MIDIPOSE_OT_analyze_midi,
    ui_operators.MIDIPOSE_OT_select_track,
    ui_operators.MIDIPOSE_OT_render_animation,
    ui_operators.MIDIPOSE_OT_refresh_poses,
    ui_operators.MIDIPOSE_OT_select_all_poses,
    ui_operators.MIDIPOSE_OT_deselect_all_poses,
    ui_operators.MIDIPOSE_OT_invert_pose_selection,
    ui_operators.MIDIPOSE_OT_move_pose,
    ui_operators.MIDIPOSE_OT_save_config,
    ui_operators.MIDIPOSE_OT_save_config_as,
    ui_operators.MIDIPOSE_OT_load_config,
    ui_operators.MIDIPOSE_OT_delete_config,
    
    # Properties Panels
    ui_properties_panels.MIDIPOSE_PT_properties_main,
    ui_properties_panels.MIDIPOSE_PT_properties_poses,
    ui_properties_panels.MIDIPOSE_PT_properties_midi,
]

def register():
    """Register all classes and properties"""
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add properties to scene
    bpy.types.Scene.midi_pose_props = PointerProperty(type=ui_operators.MidiPoseProperties)
    
    print("MIDI Pose Cycler addon registered")

def unregister():
    """Unregister all classes and properties"""
    # Remove properties from scene
    del bpy.types.Scene.midi_pose_props
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("MIDI Pose Cycler addon unregistered")

if __name__ == "__main__":
    register()