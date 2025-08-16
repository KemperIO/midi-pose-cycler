# MIDI Pose Cycler - Blender Extension

**Public Repository** | Blender 4.5+ | GPL-3.0

## Overview
Opinionated Blender extension for synchronizing pose/action animations to MIDI events. Provides dedicated workspace with editor-style interface.

### Architecture
- **Workspace-Specific UI**: Properties panels only appear in "MIDI Pose Cycler" workspace
- **Three-Column Layout**: Main controls | Poses | MIDI data
- **8-Pane Workspace**: File Browser, Asset Browser, 3D Viewport, Action Editor, Sequencer, 3x Properties

## Features

| Feature | Description |
|---------|------------|
| **MIDI Analysis** | Multi-track support, automatic track merging by name |
| **Animation Modes** | POSE (single frame) or ACTION (full animation) |
| **Pose Management** | Reorderable selection with drag handles |
| **Cycle Modes** | LOOP, BOOMERANG, RANDOM |
| **Timing Controls** | Smart (bars/beats) or dumb (frames) |
| **Note Filtering** | Target specific MIDI notes with nicknames |
| **Interpolation** | 13 types (CONSTANT, LINEAR, BEZIER, EXPO, etc.) |

## Installation

### Quick Install
1. Zip `midi-pose-cycler` folder
2. Blender: Edit → Preferences → Add-ons → Install
3. Enable "Animation: MIDI Pose Cycler"

### Dev Install
Copy to: `[BLENDER]/4.5/extensions/midi-pose-cycler/`

## Usage Workflow

### 1. Setup Workspace
```
Window menu → MIDI Pose Cycler
```
Creates comprehensive 8-pane workspace

### 2. Prepare Content
- Create pose actions (frame 0)
- Name descriptively (avoid "Midi" prefix)

### 3. Load & Configure

| Step | Action |
|------|--------|
| Load MIDI | Drag from File Browser or use Load button |
| Select Track | Click track name (auto-analyzes) |
| Choose Poses | Select & reorder with arrows |
| Set Mode | POSE (single frame) or ACTION (full) |
| Configure Timing | BPM, bars/beats or frame numbers |

### 4. Generate
Click "GENERATE ANIMATION" → Creates/updates action with keyframes

## Technical Implementation

### File Structure
```
midi-pose-cycler/
├── __init__.py              # Registration
├── animation_renderer.py    # Core animation engine
├── midi_core.py            # MIDI processing (mido)
├── ui_operators.py         # All operators & properties
├── ui_properties_panels.py # Workspace-specific panels
├── workspace_creator.py    # Workspace setup
├── config_manager.py       # Save/load configs
└── vendor/mido/           # Bundled MIDI library
```

### Data Flow
```
MIDI File → Track Analysis → Note Events → Frame Timing → Keyframe Generation
                                ↓                              ↑
                          Note Filtering               Pose/Action Selection
```

### Key Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `animation_mode` | Enum | POSE | POSE or ACTION mode |
| `pose_cycle_mode` | Enum | LOOP | LOOP/BOOMERANG/RANDOM |
| `frames_to_hold` | Int | 3 | Hold duration per pose |
| `interpolation_type` | Enum | EXPO | Transition type |
| `bpm` | Float | 120 | Beats per minute |
| `beats_per_bar` | Int | 4 | Time signature numerator |
| `use_smart_timing` | Bool | False | Musical vs frame timing |
| `midi_start_frame` | Int | 1 | Animation start frame |
| `skip_keyframe_warning` | Bool | False | Suppress overwrite dialog |

### Timing Calculation
```python
# Smart timing (musical)
frames_per_beat = (60.0 / bpm) * fps
start_frame = (bar-1) * beats_per_bar * frames_per_beat + (beat-1) * frames_per_beat + 1
duration = bars * beats_per_bar * frames_per_beat + beats * frames_per_beat

# Dumb timing (frames)
start_frame = midi_start_frame
duration = frame_limit if use_frame_limit else total_frames
```

## Operators Reference

| Operator | ID | Function |
|----------|-----|----------|
| Load MIDI | `midipose.load_midi` | Import & analyze MIDI |
| Select Track | `midipose.select_track` | Choose & analyze track |
| Refresh Poses | `midipose.refresh_poses` | Scan project actions |
| Move Pose | `midipose.move_pose` | Reorder selection |
| Render Animation | `midipose.render_animation` | Generate keyframes |
| Create Workspace | `midipose.create_workspace` | Setup UI workspace |

## Configuration Management
- **Save/Load**: Store complete setup as scene data
- **Active Config**: Track current configuration
- **Delete**: Remove saved configs

## Animation Modes Detail

### POSE Mode
- Extracts frame 0 from each action
- Inserts single keyframe per MIDI event
- Holds pose for `frames_to_hold`
- Transitions with selected interpolation

### ACTION Mode
- Copies entire action at MIDI event
- Preserves all keyframes & curves
- Offsets to event timing
- Maintains original interpolation

## Note Filtering
- **Selection**: Choose specific MIDI notes
- **Nicknames**: Label notes (e.g., "kick", "snare")
- **Display**: Shows note name, nickname, count

## Workspace Panel Organization

| Panel | Content |
|-------|---------|
| **Main** | MIDI file, action settings, timing, configs |
| **Poses** | Selection, ordering, cycle mode |
| **MIDI** | Tracks, notes, filtering |

## Blender Compliance
- **No External Dependencies**: mido bundled in vendor/
- **Read-Only Support**: Works from system directories
- **Workspace Isolation**: Panels only in custom workspace
- **No Internet Access**: Respects `bpy.app.online_access`

## Development Notes

### Workspace-Specific Panels
```python
class MidiPoseWorkspacePanel:
    bl_space_type = 'PROPERTIES'
    bl_context = "scene"
    
    @classmethod
    def poll(cls, context):
        return context.workspace.name == "MIDI Pose Cycler"
```

### Pose Ordering
```python
selected_poses = [p for p in props.pose_items if p.selected]
selected_poses.sort(key=lambda p: p.order_index)
```

### Warning Dialog Pattern
```python
def invoke(self, context, event):
    if needs_warning:
        return context.window_manager.invoke_props_dialog(self)
    return self.execute(context)
```

## Version History
- **0.5.0**: ACTION mode, BPM timing, pose reordering
- **0.4.0**: Workspace panels, config management
- **0.3.0**: Note filtering, cycle modes
- **0.2.0**: Multi-track support
- **0.1.0**: Initial release