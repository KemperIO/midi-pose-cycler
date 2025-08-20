"""
MIDI Pose Cycler - Node Tree System
Custom node tree type for visual MIDI animation workflow
"""

import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import (
    StringProperty, 
    IntProperty, 
    FloatProperty, 
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    PointerProperty
)


# Custom socket types
class MidiDataSocket(NodeSocket):
    """Socket type for MIDI data flow"""
    bl_idname = 'MidiDataSocketType'
    bl_label = "MIDI Data"
    
    # Socket color
    def draw_color(self, context, node):
        return (0.4, 0.8, 1.0, 1.0)  # Light blue
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)


class PoseDataSocket(NodeSocket):
    """Socket type for pose data flow"""
    bl_idname = 'PoseDataSocketType'
    bl_label = "Pose Data"
    
    def draw_color(self, context, node):
        return (0.8, 0.6, 0.2, 1.0)  # Orange
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)


class AnimationSocket(NodeSocket):
    """Socket type for animation output"""
    bl_idname = 'AnimationSocketType'
    bl_label = "Animation"
    
    def draw_color(self, context, node):
        return (0.2, 0.8, 0.2, 1.0)  # Green
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)


# Custom node tree
class MidiPoseNodeTree(NodeTree):
    """Node tree for MIDI pose cycling workflow"""
    bl_idname = 'MidiPoseNodeTree'
    bl_label = "MIDI Pose Cycler"
    bl_icon = 'NODETREE'
    
    def update(self):
        """Called when node tree is updated"""
        # Could trigger preview updates here
        pass


# Base node class
class MidiPoseNode(Node):
    """Base class for MIDI Pose nodes"""
    
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MidiPoseNodeTree'
    
    def copy(self, node):
        pass
    
    def free(self):
        pass


# Node implementations
class MidiInputNode(MidiPoseNode):
    """Load and analyze MIDI file"""
    bl_idname = 'MidiInputNode'
    bl_label = "MIDI Input"
    bl_icon = 'FILE_SOUND'
    
    midi_file: StringProperty(
        name="MIDI File",
        description="Path to MIDI file",
        subtype='FILE_PATH'
    )
    
    def init(self, context):
        self.outputs.new('MidiDataSocketType', "MIDI Data")
        self.width = 200
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "midi_file", text="")
        if self.midi_file:
            # Show analysis info
            col = layout.column()
            col.label(text="Tracks: 4", icon='OUTLINER_DATA_SPEAKER')
            col.label(text="Duration: 3:24", icon='TIME')
            col.label(text="BPM: 120", icon='SNAP_INCREMENT')
    
    def draw_label(self):
        return "MIDI Input"


class TrackSelectorNode(MidiPoseNode):
    """Select and filter MIDI tracks"""
    bl_idname = 'TrackSelectorNode'
    bl_label = "Track Selector"
    bl_icon = 'OUTLINER_DATA_SPEAKER'
    
    selected_track: IntProperty(
        name="Track",
        description="Selected MIDI track",
        default=0,
        min=0
    )
    
    merge_same_name: BoolProperty(
        name="Merge Same Names",
        description="Merge tracks with same name",
        default=True
    )
    
    def init(self, context):
        self.inputs.new('MidiDataSocketType', "MIDI In")
        self.outputs.new('MidiDataSocketType', "Track Out")
        self.width = 200
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        # Track list (would be dynamic based on input)
        col.label(text="Select Track:")
        box = col.box()
        box.label(text="1: Drums", icon='PLAY_SOUND')
        box.label(text="2: Bass", icon='PLAY_SOUND')
        box.label(text="3: Lead", icon='PLAY_SOUND')
        
        col.prop(self, "merge_same_name")


class NoteFilterNode(MidiPoseNode):
    """Filter specific MIDI notes"""
    bl_idname = 'NoteFilterNode'
    bl_label = "Note Filter"
    bl_icon = 'FILTER'
    
    filter_mode: EnumProperty(
        name="Mode",
        items=[
            ('ALL', "All Notes", "Use all notes"),
            ('INCLUDE', "Include", "Include specific notes"),
            ('EXCLUDE', "Exclude", "Exclude specific notes"),
            ('RANGE', "Range", "Note range"),
        ],
        default='ALL'
    )
    
    note_min: IntProperty(
        name="Min Note",
        default=0,
        min=0,
        max=127
    )
    
    note_max: IntProperty(
        name="Max Note",
        default=127,
        min=0,
        max=127
    )
    
    def init(self, context):
        self.inputs.new('MidiDataSocketType', "Track In")
        self.outputs.new('MidiDataSocketType', "Filtered")
        self.width = 200
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "filter_mode", text="")
        
        if self.filter_mode == 'RANGE':
            row = layout.row()
            row.prop(self, "note_min", text="Min")
            row.prop(self, "note_max", text="Max")
        elif self.filter_mode == 'INCLUDE':
            col = layout.column()
            col.label(text="Select Notes:")
            box = col.box()
            # Dynamic note list would go here
            row = box.row()
            row.label(text="C3 (60)")
            row.label(text="12x", icon='INFO')
            row = box.row()
            row.label(text="D3 (62)")
            row.label(text="8x", icon='INFO')
        elif self.filter_mode == 'EXCLUDE':
            col = layout.column()
            col.label(text="Exclude Notes:")
            box = col.box()
            box.label(text="(Click to select)")


class PoseSequenceNode(MidiPoseNode):
    """Define pose sequence and cycling"""
    bl_idname = 'PoseSequenceNode'
    bl_label = "Pose Sequence"
    bl_icon = 'ARMATURE_DATA'
    
    cycle_mode: EnumProperty(
        name="Cycle Mode",
        items=[
            ('LOOP', "Loop", "Cycle through poses"),
            ('RANDOM', "Random", "Random pose selection"),
            ('PINGPONG', "Ping Pong", "Forward then backward"),
        ],
        default='LOOP'
    )
    
    def init(self, context):
        self.inputs.new('PoseDataSocketType', "Poses")
        self.outputs.new('PoseDataSocketType', "Sequence")
        self.width = 250
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "cycle_mode", text="")
        
        col = layout.column()
        col.label(text="Pose Order:")
        box = col.box()
        
        # Mock pose list
        poses = ["neck-left", "neck-right", "head-up", "head-down"]
        for i, pose in enumerate(poses, 1):
            row = box.row()
            row.label(text=f"{i}. {pose}")
            sub = row.row(align=True)
            sub.operator("midipose.move_pose_up", text="", icon='TRIA_UP')
            sub.operator("midipose.move_pose_down", text="", icon='TRIA_DOWN')


class PoseInputNode(MidiPoseNode):
    """Input poses from project"""
    bl_idname = 'PoseInputNode'
    bl_label = "Pose Input"
    bl_icon = 'ARMATURE_DATA'
    
    filter_prefix: StringProperty(
        name="Filter",
        description="Filter pose names",
        default=""
    )
    
    def init(self, context):
        self.outputs.new('PoseDataSocketType', "Poses")
        self.width = 200
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        row = col.row()
        row.prop(self, "filter_prefix", text="", icon='VIEWZOOM')
        row.operator("midipose.refresh_poses", text="", icon='FILE_REFRESH')
        
        col.label(text="Available Poses:")
        box = col.box()
        # Would list actual poses
        box.label(text="• neck-left", icon='BONE_DATA')
        box.label(text="• neck-right", icon='BONE_DATA')
        box.label(text="• head-up", icon='BONE_DATA')
        box.label(text="• head-down", icon='BONE_DATA')


class TimingNode(MidiPoseNode):
    """Configure timing and interpolation"""
    bl_idname = 'TimingNode'
    bl_label = "Timing"
    bl_icon = 'TIME'
    
    frames_to_hold: IntProperty(
        name="Hold Frames",
        description="Frames to hold each pose",
        default=3,
        min=1,
        max=60
    )
    
    interpolation_type: EnumProperty(
        name="Interpolation",
        items=[
            ('CONSTANT', "Constant", "No interpolation"),
            ('LINEAR', "Linear", "Linear interpolation"),
            ('BEZIER', "Bezier", "Smooth bezier"),
            ('EXPO', "Exponential", "Exponential easing"),
        ],
        default='EXPO'
    )
    
    bpm: FloatProperty(
        name="BPM",
        description="Beats per minute",
        default=120.0,
        min=1.0,
        max=300.0
    )
    
    def init(self, context):
        self.inputs.new('MidiDataSocketType', "MIDI")
        self.inputs.new('PoseDataSocketType', "Poses")
        self.outputs.new('AnimationSocketType', "Animation")
        self.width = 200
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "bpm")
        col.prop(self, "frames_to_hold")
        col.prop(self, "interpolation_type", text="")


class AnimationOutputNode(MidiPoseNode):
    """Output animation to action"""
    bl_idname = 'AnimationOutputNode'
    bl_label = "Animation Output"
    bl_icon = 'OUTPUT'
    
    action_name: StringProperty(
        name="Action",
        description="Output action name",
        default="MidiPoseAnimation"
    )
    
    start_frame: IntProperty(
        name="Start Frame",
        default=1,
        min=1
    )
    
    clear_existing: BoolProperty(
        name="Clear Existing",
        description="Clear existing keyframes",
        default=True
    )
    
    def init(self, context):
        self.inputs.new('AnimationSocketType', "Animation")
        self.width = 250
        self.use_custom_color = True
        self.color = (0.2, 0.3, 0.2)
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        col.prop(self, "action_name", text="")
        col.prop(self, "start_frame")
        col.prop(self, "clear_existing")
        
        col.separator()
        
        # Big generate button
        row = col.row()
        row.scale_y = 2.0
        op = row.operator("midipose.generate_from_nodes", 
                         text="GENERATE ANIMATION",
                         icon='PLAY')
        
        col.separator()
        col.label(text="Target: " + (context.active_object.name 
                                     if context.active_object else "None"),
                 icon='OBJECT_DATA')


# Node categories for add menu
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MidiPoseNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MidiPoseNodeTree'

node_categories = [
    MidiPoseNodeCategory("INPUTS", "Input", items=[
        NodeItem("MidiInputNode"),
        NodeItem("PoseInputNode"),
    ]),
    MidiPoseNodeCategory("PROCESSING", "Processing", items=[
        NodeItem("TrackSelectorNode"),
        NodeItem("NoteFilterNode"),
        NodeItem("PoseSequenceNode"),
        NodeItem("TimingNode"),
    ]),
    MidiPoseNodeCategory("OUTPUT", "Output", items=[
        NodeItem("AnimationOutputNode"),
    ]),
]


classes = [
    # Sockets
    MidiDataSocket,
    PoseDataSocket,
    AnimationSocket,
    # Tree
    MidiPoseNodeTree,
    # Nodes
    MidiInputNode,
    TrackSelectorNode,
    NoteFilterNode,
    PoseSequenceNode,
    PoseInputNode,
    TimingNode,
    AnimationOutputNode,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    nodeitems_utils.register_node_categories("MIDIPOSE_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("MIDIPOSE_NODES")
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)