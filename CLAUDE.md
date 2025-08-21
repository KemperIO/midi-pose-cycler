# MIDI Pose Cycler - Blender Extension

**Public Repository** | Blender 4.5+ | GPL-3.0 | **WSL**: C:\→/mnt/c/

**Developer Note**: Reference `bpyref.md` for Blender API patterns. Update it when learning from https://docs.blender.org/api/4.5/

## Overview
Opinionated Blender extension for synchronizing pose/action animations to MIDI events. Provides both node-based visual workflow and traditional panel interface.

**Dev Rules**: Be pithy. Multi-task format: `** task1` `** task2` = complete all.

## CRITICAL TESTING RULES - ALWAYS FOLLOW

### 1. NEVER RUN BLENDER DIRECTLY
**WRONG**: 
```bash
/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe --background --factory-startup --python test/test.py
```

**CORRECT**: Use Python wrapper scripts:
```bash
python test/run_test_wrapper.py test_name
```

### 2. ALWAYS RUN TESTS AFTER EVERY CODE CHANGE
- Run `test_no_errors.py` after EVERY code modification
- Run `test_midi_simple.py` after ANY MIDI-related changes
- Run `test_midi_operator.py` to test ACTUAL USER EXPERIENCE (not just core functions!)
- Check console logs for errors BEFORE responding to user
- NEVER commit or finish without running tests
- CRITICAL: Test the OPERATORS that users actually use, not just backend functions!

### 3. TEST WRAPPER PATTERN
Create wrapper scripts that handle Blender execution:
```python
# run_test_wrapper.py
import subprocess
import sys

def run_blender_test(test_file):
    cmd = [
        "/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe",
        "--background", 
        "--factory-startup",
        "--python", test_file
    ]
    return subprocess.run(cmd, capture_output=True, text=True)
```

### 4. MIDO RELOAD ERROR FIX
The "ERROR: mido library not available" on reload is a known issue. Always check and fix:
- Ensure mido is checked in sys.modules before reimporting
- Add vendor path to sys.path before any imports
- Test with script reload to verify no errors

**Bash Permissions**: Only use wrappers: `Bash("python test/run_test_wrapper.py test_name")`

### Architecture
- **Node-Based System**: Visual node tree for MIDI animation pipeline
- **Custom Node Types**: MIDI input, filtering, pose sequencing, timing control
- **Dual Interface**: Node editor workflow or traditional properties panels
- **Workspace Layouts**: Optimized layouts for both approaches

## Features

| Feature            | Description                                          |
|--------------------|------------------------------------------------------|
| **MIDI Analysis**  | Multi-track support, automatic track merging by name|
| **Animation Modes**| POSE (single frame) or ACTION (full animation)      |
| **Pose Management**| Reorderable selection with drag handles             |
| **Cycle Modes**    | LOOP, BOOMERANG, RANDOM                             |
| **Timing Controls**| Smart (bars/beats) or dumb (frames)                 |
| **Note Filtering** | Target specific MIDI notes with nicknames           |
| **Interpolation**  | 13 types (CONSTANT, LINEAR, BEZIER, EXPO, etc.)     |

## Installation

### Quick Install
1. Zip `midi-pose-cycler` folder
2. Blender: Edit → Preferences → Add-ons → Install
3. Enable "Animation: MIDI Pose Cycler"

### Dev Install
Copy to: `[BLENDER]/4.5/extensions/midi-pose-cycler/`

## Usage Workflows

### Panel-Based UI (N-Pane)

#### Access
In 3D Viewport, press **N** to open sidebar → Three tabs available:
- **MPC-Run**: Main execution and settings
- **MPC-Pose**: Pose selection and ordering
- **MPC-MIDI**: MIDI file and track management

**Available in**: Object Mode & Pose Mode

#### Tab Layout

| Tab Name | Panels | Features |
|----------|--------|----------|
| **MPC-Run** | • Run Animation<br>• Action Settings<br>• Timing<br>• Preview<br>• Configurations | Generate button, action dropdown selector, timing settings, preview of selections, save/load configs |
| **MPC-Pose** | • Pose Selection<br>• Pose Order<br>• Cycle Settings | Grid-based pose selection, drag-and-drop ordering with large arrows, cycle mode settings |
| **MPC-MIDI** | • MIDI File<br>• Track Selection<br>• Note Filter | MIDI file loading, track selection with radio buttons, note filtering with nicknames |

#### Workflow
1. **Load MIDI**: Click "Load MIDI File" or drag from File Browser
2. **Select Track**: Click track name in MIDI Data panel
3. **Choose Poses**: Select poses in Poses panel, reorder with arrows
4. **Configure**: Set animation mode, timing, interpolation
5. **Generate**: Click "GENERATE ANIMATION" button

#### Prepare Content
- Create pose actions (frame 0)
- Name descriptively (avoid "Midi" prefix)

#### Key Settings

| Step         | Action                                    |
|--------------|-------------------------------------------|
| Load MIDI    | Drag from File Browser or use Load button|
| Select Track | Click track name (auto-analyzes)         |
| Choose Poses | Select & reorder with arrows             |
| Set Mode     | POSE (single frame) or ACTION (full)     |
| Config Timing| BPM, bars/beats or frame numbers         |

#### Generate Animation
Click "GENERATE ANIMATION" → Creates/updates action with keyframes

### Legacy Workflows (Deprecated)

**Note**: Node-based workflow and workspace generation have been removed. Use the N-pane UI instead.

## Node Types Reference

### Input Nodes

| Node | Purpose | Inputs | Outputs |
|------|---------|--------|---------|
| **MIDI Input** | Load & analyze MIDI file | - | MIDI Data |
| **Pose Input** | Select poses from project | - | Pose Data |

### Processing Nodes

| Node | Purpose | Inputs | Outputs |
|------|---------|--------|---------|
| **Track Selector** | Choose MIDI track | MIDI Data | Track Data |
| **Note Filter** | Filter notes (ALL/Include/Exclude/Range) | Track Data | Filtered Data |
| **Pose Sequence** | Order & cycle poses | Pose Data | Sequence |
| **Timing** | Configure hold, interpolation, BPM | MIDI + Poses | Animation |

### Output Node

| Node | Purpose | Inputs | Outputs |
|------|---------|--------|---------|
| **Animation Output** | Generate keyframes | Animation | Action |

### Node Properties

#### Note Filter Modes
- **ALL**: Use all notes (default)
- **Include**: Only specified notes
- **Exclude**: All except specified notes  
- **Range**: Note range (min/max)

#### Pose Cycle Modes
- **Loop**: Sequential cycling
- **Random**: Random selection
- **Ping Pong**: Forward then backward

## Technical Implementation

### File Structure
```
midi-pose-cycler/
├── src/                     # Source code
│   ├── __init__.py          # Registration
│   ├── animation_renderer.py # Core animation engine
│   ├── midi_core.py         # MIDI processing (mido)
│   ├── node_tree.py         # Custom node tree & nodes
│   ├── node_operators.py    # Node-related operators
│   ├── ui_operators.py      # Panel operators & properties
│   ├── ui_properties_panels.py # Workspace-specific panels
│   ├── workspace_creator.py # Panel workspace setup
│   ├── workspace_node_based.py # Node workspace setup
│   ├── config_manager.py    # Save/load configs
│   └── blender_manifest.toml # Addon metadata
├── test/                    # Test suite
│   ├── run_tests.py         # Test runner
│   ├── test_addon_load.py   # Addon registration tests
│   └── test_workspace.py    # Workspace creation tests
├── docs/                    # Documentation
│   ├── CLAUDE.md            # This documentation
│   ├── bpyref.md            # Blender API reference (UPDATE!)
│   ├── cli.md               # CLI testing reference
│   └── README.md            # User documentation
└── vendor/mido/             # Bundled MIDI library
```

### Data Flow
```
MIDI File → Track Analysis → Note Events → Frame Timing → Keyframe Generation
                                ↓                              ↑
                          Note Filtering               Pose/Action Selection
```

### Key Properties

| Property              | Type  | Default | Description                      |
|-----------------------|-------|---------|----------------------------------|
| `animation_mode`      | Enum  | POSE    | POSE or ACTION mode              |
| `pose_cycle_mode`     | Enum  | LOOP    | LOOP/BOOMERANG/RANDOM            |
| `frames_to_hold`      | Int   | 3       | Hold duration per pose           |
| `interpolation_type`  | Enum  | EXPO    | Transition type                  |
| `bpm`                 | Float | 120     | Beats per minute                 |
| `beats_per_bar`       | Int   | 4       | Time signature numerator         |
| `use_smart_timing`    | Bool  | False   | Musical vs frame timing          |
| `midi_start_frame`    | Int   | 1       | Animation start frame            |
| `skip_keyframe_warning`| Bool  | False   | Suppress overwrite dialog        |

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

| Operator          | ID                          | Function             |
|-------------------|-----------------------------|----------------------|
| Load MIDI         | `midipose.load_midi`        | Import & analyze MIDI|
| Select Track      | `midipose.select_track`     | Choose & analyze track|
| Refresh Poses     | `midipose.refresh_poses`    | Scan project actions |
| Move Pose         | `midipose.move_pose`        | Reorder selection    |
| Render Animation  | `midipose.render_animation` | Generate keyframes   |
| Create Workspace  | `midipose.create_workspace` | Setup UI workspace   |

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

| Panel            | Content                                   |
|------------------|-------------------------------------------|
| **Main**         | MIDI file, action settings, timing, configs|
| **Poses**        | Selection, ordering, cycle mode          |
| **MIDI**         | Tracks, notes, filtering                 |

## Blender Compliance
- **No External Dependencies**: mido bundled in vendor/
- **Read-Only Support**: Works from system directories
- **Workspace Isolation**: Panels only in custom workspace
- **No Internet Access**: Respects `bpy.app.online_access`

## Testing

### Running Tests
```bash
# Run all tests
python test/run_tests.py

# Run specific test
python test/run_tests.py workspace
python test/run_tests.py addon_load
```

### Test Coverage
- **test_no_errors**: Verifies addon loads without console errors (RUN THIS ALWAYS!)
- **addon_load**: Verifies registration of operators, panels, properties
- **workspace**: Tests workspace creation and layout validation

### Writing New Tests
1. Create `test/test_yourtest.py` with a `main()` function
2. Import and run in Blender context
3. Use stdout for test output
4. Return True/False or exit with 0/1

## Development Notes

**IMPORTANT**: Always run `test_no_errors.py` on EVERY code change to ensure no console errors.
**IMPORTANT**: Always run tests when changing workspace setup logic to verify workspace generation works without crashes.

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