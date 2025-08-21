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


class TrackDataSocket(NodeSocket):
    """Socket type for track data flow"""
    bl_idname = 'TrackDataSocketType'
    bl_label = "Track Data"
    
    def draw_color(self, context, node):
        return (0.6, 0.4, 0.8, 1.0)  # Purple
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)


class FilteredDataSocket(NodeSocket):
    """Socket type for filtered MIDI data"""
    bl_idname = 'FilteredDataSocketType'
    bl_label = "Filtered Data"
    
    def draw_color(self, context, node):
        return (0.8, 0.4, 0.6, 1.0)  # Pink
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)


class SequenceSocket(NodeSocket):
    """Socket type for pose sequence"""
    bl_idname = 'SequenceSocketType'
    bl_label = "Sequence"
    
    def draw_color(self, context, node):
        return (0.8, 0.8, 0.2, 1.0)  # Yellow
    
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
    
    track_count: IntProperty(
        name="Tracks",
        default=0
    )
    
    duration: StringProperty(
        name="Duration",
        default="0:00"
    )
    
    bpm: FloatProperty(
        name="BPM",
        default=120.0
    )
    
    def init(self, context):
        self.outputs.new('MidiDataSocketType', "MIDI Data")
        self.width = 200
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "midi_file", text="")
        row = layout.row()
        row.operator("midipose.load_midi_node", text="Load MIDI", icon='FILE_FOLDER')
        
        if self.midi_file:
            # Show analysis info
            col = layout.column()
            col.label(text=f"Tracks: {self.track_count}", icon='OUTLINER_DATA_SPEAKER')
            col.label(text=f"Duration: {self.duration}", icon='TIME')
            col.label(text=f"BPM: {self.bpm:.1f}", icon='SNAP_INCREMENT')
    
    def draw_label(self):
        return "MIDI Input"
    
    def load_midi(self, context):
        """Load and analyze MIDI file"""
        if not self.midi_file:
            return
        
        # Import midi_core for analysis
        try:
            from . import midi_core
            analysis = midi_core.analyze_midi_file(self.midi_file)
            if analysis:
                self.track_count = len(analysis.get('tracks', []))
                # Calculate duration
                total_ticks = analysis.get('total_ticks', 0)
                ticks_per_beat = analysis.get('ticks_per_beat', 480)
                tempo = analysis.get('tempo', 500000)  # microseconds per beat
                bpm = 60000000 / tempo
                self.bpm = bpm
                duration_seconds = (total_ticks / ticks_per_beat) * (tempo / 1000000)
                mins = int(duration_seconds // 60)
                secs = int(duration_seconds % 60)
                self.duration = f"{mins}:{secs:02d}"
        except:
            pass


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
        self.inputs.new('MidiDataSocketType', "MIDI Data")
        self.outputs.new('TrackDataSocketType', "Track Data")
        self.width = 200
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        # Get input node if connected
        midi_data = self.get_input_data()
        
        col.label(text="Select Track:")
        box = col.box()
        
        if midi_data and 'tracks' in midi_data:
            for i, track in enumerate(midi_data['tracks']):
                row = box.row()
                icon = 'RADIOBUT_ON' if i == self.selected_track else 'RADIOBUT_OFF'
                op = row.operator("midipose.select_track_node", text=f"{i}: {track['name']}", icon=icon)
                op.track_index = i
                row.label(text=f"{track['note_count']} notes")
        else:
            box.label(text="Connect MIDI Input", icon='INFO')
        
        col.prop(self, "merge_same_name")
    
    def get_input_data(self):
        """Get data from connected input node"""
        if self.inputs[0].is_linked:
            link = self.inputs[0].links[0]
            from_node = link.from_node
            if hasattr(from_node, 'midi_file'):
                # Return mock data for now
                return {
                    'tracks': [
                        {'name': 'Drums', 'note_count': 128},
                        {'name': 'Bass', 'note_count': 64},
                        {'name': 'Lead', 'note_count': 32}
                    ]
                }
        return None


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
        self.inputs.new('TrackDataSocketType', "Track Data")
        self.outputs.new('FilteredDataSocketType', "Filtered Data")
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
            ('BOOMERANG', "Boomerang", "Forward then backward"),
        ],
        default='LOOP'
    )
    
    def init(self, context):
        self.inputs.new('PoseDataSocketType', "Pose Data")
        self.outputs.new('SequenceSocketType', "Sequence")
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
        self.outputs.new('PoseDataSocketType', "Pose Data")
        self.width = 250
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        row = col.row()
        row.prop(self, "filter_prefix", text="", icon='VIEWZOOM')
        row.operator("midipose.refresh_poses_node", text="", icon='FILE_REFRESH')
        
        col.label(text="Available Poses:")
        box = col.box()
        
        # Get actual actions from project
        actions = self.get_available_poses()
        if actions:
            for action in actions[:10]:  # Limit display
                row = box.row()
                row.operator("midipose.select_pose_node", text=action.name, icon='BONE_DATA').action_name = action.name
        else:
            box.label(text="No poses found", icon='INFO')
            box.label(text="Create actions first")
    
    def get_available_poses(self):
        """Get available pose actions from project"""
        import bpy
        actions = []
        for action in bpy.data.actions:
            # Filter out generated actions
            if not action.name.startswith("MidiPose"):
                if not self.filter_prefix or self.filter_prefix.lower() in action.name.lower():
                    actions.append(action)
        return sorted(actions, key=lambda a: a.name)
    
    def refresh_poses(self):
        """Refresh pose list"""
        pass


class TimingNode(MidiPoseNode):
    """Configure timing and interpolation"""
    bl_idname = 'TimingNode'
    bl_label = "Timing"
    bl_icon = 'TIME'
    
    use_smart_timing: BoolProperty(
        name="Smart Timing",
        description="Use musical timing (bars/beats)",
        default=False
    )
    
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
            ('SINE', "Sine", "Sine wave interpolation"),
            ('QUAD', "Quadratic", "Quadratic easing"),
            ('CUBIC', "Cubic", "Cubic easing"),
            ('QUART', "Quartic", "Quartic easing"),
            ('QUINT', "Quintic", "Quintic easing"),
            ('EXPO', "Exponential", "Exponential easing"),
            ('CIRC', "Circular", "Circular easing"),
            ('BACK', "Back", "Back easing"),
            ('BOUNCE', "Bounce", "Bounce easing"),
            ('ELASTIC', "Elastic", "Elastic easing"),
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
    
    beats_per_bar: IntProperty(
        name="Beats/Bar",
        description="Time signature numerator",
        default=4,
        min=1,
        max=16
    )
    
    start_bar: IntProperty(
        name="Start Bar",
        description="Bar to start animation",
        default=1,
        min=1
    )
    
    start_beat: IntProperty(
        name="Start Beat",
        description="Beat within bar to start",
        default=1,
        min=1
    )
    
    duration_bars: IntProperty(
        name="Bars",
        description="Duration in bars",
        default=4,
        min=0
    )
    
    duration_beats: IntProperty(
        name="Beats",
        description="Additional beats",
        default=0,
        min=0
    )
    
    def init(self, context):
        self.inputs.new('FilteredDataSocketType', "MIDI")
        self.inputs.new('SequenceSocketType', "Poses")
        self.outputs.new('AnimationSocketType', "Animation")
        self.width = 250
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        # Smart timing toggle
        col.prop(self, "use_smart_timing")
        
        if self.use_smart_timing:
            # Musical timing
            col.prop(self, "bpm")
            col.prop(self, "beats_per_bar")
            
            col.separator()
            col.label(text="Start Position:")
            row = col.row()
            row.prop(self, "start_bar", text="Bar")
            row.prop(self, "start_beat", text="Beat")
            
            col.label(text="Duration:")
            row = col.row()
            row.prop(self, "duration_bars", text="Bars")
            row.prop(self, "duration_beats", text="Beats")
        else:
            # Frame-based timing
            col.prop(self, "frames_to_hold")
        
        col.separator()
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
    
    animation_mode: EnumProperty(
        name="Mode",
        items=[
            ('POSE', "Pose", "Single frame poses"),
            ('ACTION', "Action", "Full action clips")
        ],
        default='POSE'
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
        
        col.prop(self, "animation_mode", text="")
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
    TrackDataSocket,
    FilteredDataSocket,
    SequenceSocket,
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