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
- **Panel-Based System**: N-pane sidebar interface with three tabs
- **Multi-Track Support**: Select and filter multiple MIDI tracks simultaneously
- **Smart Controls**: Linked controls that update each other (frames ↔ bars/beats)
- **Dynamic Tracks**: Generate events at regular intervals without MIDI data

## UX Components Overview

| Component               | Blender Name         | Description                   | Example Usage                |
|-------------------------|----------------------|-------------------------------|------------------------------|
| **N-Pane Tabs**         | `bl_category`        | Sidebar tabs in 3D Viewport  | MPC-Run, MPC-Pose, MPC-MIDI |
| **Panels**              | `Panel` class        | Grouped UI sections           | Track Selection, Pose Order  |
| **Collapsible Regions** | Box with toggle      | Expandable UI sections        | Note filters per track       |
| **Grid Flow**           | `grid_flow()`        | Multi-column checkbox layout  | Track/pose selection         |
| **Property Fields**     | `prop()`             | Input fields and checkboxes   | Hold Frames, BPM             |
| **Operators**           | `Operator` class     | Action buttons                | Generate Animation, Load MIDI|
| **Tooltips**            | `description` property| Hover text explanations      | Interpolation types          |

## Features

| Feature             | Description                                          |
|---------------------|------------------------------------------------------|
| **MIDI Analysis**   | Multi-track support, automatic track merging by name|
| **Animation Modes** | POSE (single frame) or ACTION (full animation)      |
| **Pose Management** | Reorderable selection with drag handles             |
| **Cycle Modes**     | LOOP, BOOMERANG, RANDOM, PITCH_FOLLOW              |
| **Timing Controls** | Smart (bars/beats) or dumb (frames)                 |
| **Note Filtering**  | Per-track collapsible filters with checkboxes       |
| **Interpolation**   | 13 types with hover explanations                    |
| **Dynamic Tracks**  | Generate events at intervals (Every X beats/bars)   |
| **Smart Controls**  | Linked frame ↔ bar/beat conversion                  |

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

| Tab Name     | Panels                                                                    | Features                                                                               |
|--------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| **MPC-Run**  | • Run Animation<br>• Action Settings<br>• Timing<br>• Preview<br>• Configurations | Generate button, action dropdown selector, timing settings, preview of selections, save/load configs |
| **MPC-Pose** | • Pose Selection<br>• Pose Order<br>• Cycle Settings                             | Grid-based pose selection, drag-and-drop ordering with large arrows, cycle mode settings             |
| **MPC-MIDI** | • MIDI File<br>• Track Selection<br>• Note Filter                                | MIDI file loading, track selection with radio buttons, note filtering with nicknames                 |

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

| Step          | Action                                    |
|---------------|-------------------------------------------|
| Load MIDI     | Drag from File Browser or use Load button|
| Select Track  | Click track name (auto-analyzes)         |
| Choose Poses  | Select & reorder with arrows             |
| Set Mode      | POSE (single frame) or ACTION (full)     |
| Config Timing | BPM, bars/beats or frame numbers         |

#### Generate Animation
Click "GENERATE ANIMATION" → Creates/updates action with keyframes

### Legacy Workflows (Deprecated)

**Note**: Node-based workflow and workspace generation have been removed. Use the N-pane UI instead.

## Node Types Reference

### Input Nodes

| Node                | Purpose                           | Inputs       | Outputs       |
|---------------------|-----------------------------------|--------------|---------------|
| **MIDI Input**      | Load & analyze MIDI file         | -            | MIDI Data     |
| **Pose Input**      | Select poses from project        | -            | Pose Data     |

### Processing Nodes

| Node                | Purpose                           | Inputs       | Outputs       |
|---------------------|-----------------------------------|--------------|---------------|
| **Track Selector**  | Choose MIDI track                         | MIDI Data    | Track Data    |
| **Note Filter**     | Filter notes (ALL/Include/Exclude/Range)  | Track Data   | Filtered Data |
| **Pose Sequence**   | Order & cycle poses                       | Pose Data    | Sequence      |
| **Timing**          | Configure hold, interpolation, BPM        | MIDI + Poses | Animation     |

### Output Node

| Node                | Purpose                           | Inputs       | Outputs       |
|---------------------|-----------------------------------|--------------|---------------|
| **Animation Output**| Generate keyframes                        | Animation    | Action        |

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

| Property                | Type  | Default | Description                      |
|-------------------------|-------|---------|----------------------------------|
| `animation_mode`        | Enum  | POSE    | POSE or ACTION mode                 |
| `pose_cycle_mode`       | Enum  | LOOP    | LOOP/BOOMERANG/RANDOM/PITCH_FOLLOW  |
| `frames_to_hold`        | Int   | 3       | Hold duration per pose              |
| `interpolation_type`    | Enum  | EXPO    | Transition type                      |
| `bpm`                   | Float | 120     | Beats per minute                     |
| `beats_per_bar`         | Int   | 4       | Time signature numerator            |
| `use_smart_timing`      | Bool  | False   | Musical vs frame timing             |
| `midi_start_frame`      | Int   | 1       | Animation start frame                |
| `skip_keyframe_warning` | Bool  | False   | Suppress overwrite dialog           |

### BPM Usage

BPM is **ONLY** used in these specific cases:

| Use Case                 | Description                   | Formula                                                                              |
|--------------------------|-------------------------------|--------------------------------------------------------------------------------------|
| **Smart Timing Start**   | Convert bar/beat to frame    | `frame = (bar-1) * beats_per_bar * frames_per_beat + (beat-1) * frames_per_beat + 1` |
| **Smart Timing Duration**| Convert bars/beats to frames | `frames = bars * beats_per_bar * frames_per_beat + beats * frames_per_beat`          |
| **Dynamic Track**        | Generate events at intervals | `frame = beat_number * frames_per_beat`                                              |

Where: `frames_per_beat = (60.0 / bpm) * fps`

### Smart Controls

Bi-directional controls that update each other:

| Frame Control    | Musical Control      | Conversion                              |
|------------------|----------------------|-----------------------------------------|
| Start Frame      | Start Bar/Beat       | `bar = floor(frame / frames_per_bar) + 1` |
| Duration Frames  | Duration Bars/Beats  | `bars = floor(frames / frames_per_bar)`   |
| Hold Frames      | Hold Beats           | `beats = frames / frames_per_beat`        |

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

| Operator          | ID                          | Function               |
|-------------------|-----------------------------|------------------------|
| Load MIDI         | `midipose.load_midi`        | Import & analyze MIDI  |
| Select Track      | `midipose.select_track`     | Choose & analyze track |
| Refresh Poses     | `midipose.refresh_poses`    | Scan project actions   |
| Move Pose         | `midipose.move_pose`        | Reorder selection      |
| Render Animation  | `midipose.render_animation` | Generate keyframes     |
| Create Workspace  | `midipose.create_workspace` | Setup UI workspace     |

## Configuration Management

### ConfigData Type
Saved configurations use the `ConfigData` TypedDict structure defined in `config_manager.py`:

```python
class ConfigData(TypedDict):
    version: str                    # Config format version
    
    # Core settings
    midi_file: str                  # Path to MIDI file
    action_name: str                # Output action name
    animation_mode: str             # POSE or ACTION
    pose_cycle_mode: str            # LOOP, BOOMERANG, RANDOM, PITCH_FOLLOW
    
    # Timing settings
    frames_to_hold: int
    interpolation_type: str
    bpm: float
    beats_per_bar: int
    use_smart_timing: bool
    midi_start_frame: int
    midi_start_bar: int
    midi_start_beat: int
    midi_length_bars: int
    midi_length_beats: int
    use_frame_limit: bool
    frame_limit: int
    
    # Multi-track support
    selected_tracks: List[Dict]     # Track selections with note filters
    
    # Pose selection
    selected_poses: List[str]       # Ordered pose names
    pose_order: Dict[str, int]      # Pose name -> order index
    
    # Dynamic track
    dynamic_interval_beats: float
    dynamic_interval_type: str
```

### Features
- **Save/Load**: Store complete setup as scene data
- **Active Config**: Track current configuration
- **Delete**: Remove saved configs
- **Auto-reload**: MIDI file automatically reloaded when config is loaded
- **Multi-track support**: Saves all selected tracks with their note filters
- **Pose order preservation**: Maintains pose selection and ordering

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

| Panel            | Content                                      |
|------------------|----------------------------------------------|
| **Main**         | MIDI file, action settings, timing, configs |
| **Poses**        | Selection, ordering, cycle mode             |
| **MIDI**         | Tracks, notes, filtering                    |

## Blender Compliance
- **No External Dependencies**: mido bundled in vendor/
- **Read-Only Support**: Works from system directories
- **Workspace Isolation**: Panels only in custom workspace
- **No Internet Access**: Respects `bpy.app.online_access`

## Testing

### ALWAYS RUN TESTS AFTER CODE CHANGES
When making changes, write straightforward tests to verify functionality and prevent regressions.

### Running Tests (Use Wrapper!)
```bash
# CORRECT - Use the wrapper
python test/run_test_wrapper.py test_name

# Examples:
python test/run_test_wrapper.py test_no_errors
python test/run_test_wrapper.py test_3tab_layout
python test/run_test_wrapper.py test_multitrack
python test/run_test_wrapper.py test_midi_operator
```

### Current Test Coverage

| Test                     | Purpose                | What it Verifies                                                                                    |
|--------------------------|------------------------|------------------------------------------------------------------------------------------------------|
| **test_no_errors**       | Core addon health      | ✓ Addon loads without console errors<br>✓ All panels registered<br>✓ Properties initialized         |
| **test_3tab_layout**     | UI structure           | ✓ All 3 tabs exist (MPC-Run, MPC-Pose, MPC-MIDI)<br>✓ All panels in correct tabs<br>✓ bl_category set correctly |
| **test_multitrack**      | Multi-track selection  | ✓ Multiple tracks can be selected<br>✓ Per-track note filters work<br>✓ Filter operators function  |
| **test_midi_operator**   | User workflow          | ✓ MIDI file loads via operator<br>✓ Tracks populate correctly<br>✓ Note selection works            |
| **test_midi_simple**     | Core MIDI              | ✓ mido library imports<br>✓ MIDI file analysis<br>✓ Track detection                                |
| **test_dynamic_track**   | Dynamic track events   | ✓ Dynamic track properties<br>✓ Event generation at intervals<br>✓ Correct timing calculations     |
| **test_pitch_follow**    | PITCH_FOLLOW mode      | ✓ Tone class functionality<br>✓ PitchFollowMapper logic<br>✓ Bounce_out behavior<br>✓ Integration with renderer |

### Writing New Tests
1. Create `test/test_NAME.py` with `main()` function
2. Return True for pass, False for fail
3. Use print statements for feedback
4. Test one specific feature per file
5. Keep tests fast and non-flaky

### Deprecated Code (No Longer Used)

| File/Feature                | Status     | Reason                         |
|-----------------------------|------------|---------------------------------|
| **node_tree.py**            | DEPRECATED | Switched to 3-tab N-panel UI   |
| **node_operators.py**       | DEPRECATED | Node workflow removed           |
| **workspace_node_based.py** | DEPRECATED | No node workspace needed        |
| **ui_properties_panels.py** | REPLACED   | Replaced by ui_panels_*.py     |
| **Single track selection**  | REMOVED    | Now supports multi-track       |
| **Global note filtering**   | REMOVED    | Per-track filtering instead    |

### Active Core Components

| Component                   | Purpose                             |
|-----------------------------|-------------------------------------|
| **ui_panels_run.py**        | MPC-Run tab - main execution        |
| **ui_panels_pose.py**       | MPC-Pose tab - pose management      |
| **ui_panels_midi.py**       | MPC-MIDI tab - MIDI/track handling  |
| **ui_operators.py**         | All operators and properties        |
| **midi_core.py**            | MIDI file analysis with mido        |
| **animation_renderer.py**   | Keyframe generation                 |
| **tone.py**                 | MIDI tone representation with names |
| **pitch_follow_mapper.py**  | Pitch-to-pose mapping logic         |

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

## PITCH_FOLLOW Cycle Mode

### Overview
PITCH_FOLLOW maps MIDI tone pitch to pose selection height. Higher pitch → higher pose index, with automatic "bounce_out" to prevent repetition.

### Components

#### Tone Class
Represents MIDI notes with both numeric (0-127) and human-readable names (C3, D#4):
```python
tone = Tone(60)  # Middle C
print(tone.name)  # "C3"
print(tone.value)  # 60
```

#### PitchFollowMapper
Maps tones to pose indices with intelligent repetition handling:
- **Linear mapping**: Lowest tone → pose 0, highest tone → last pose
- **Bounce_out logic**: If same pose would repeat, bounce to nearest different pose
  - At lowest (0): bounce to 1
  - At highest (max): bounce to max-1
  - In middle: bounce to closer edge (prefer up if equidistant)

### Usage Example
```python
mapper = PitchFollowMapper(Tone(48), Tone(72))  # C2 to C4 range
poses = ["Low", "Mid", "High"]
tones = [Tone(48), Tone(48), Tone(60), Tone(72)]
indices = mapper.map(tones, len(poses))
# Results: [0, 1, 1, 2] - second 48 bounces from 0 to 1
```

### Animation Integration
When PITCH_FOLLOW is selected:
1. Analyzes MIDI track tone range
2. Creates PitchFollowMapper with min/max tones
3. Maps each note event to pose based on pitch
4. Applies bounce_out for consecutive same poses
5. Generates animation with pitch-driven pose selection

## Headless Mode

**Progress Tracking**: See `headless/headless-progress.md` for current status, known issues, and future work.

### Overview
Generate animations from markdown table input without GUI. Object-oriented, typed, modular design.

**Vision**: Create beautiful animation-to-music tool - art for humanity. Enable creators to generate reusable animations across different characters from simple markdown input.

### Usage
```bash
blender --background --python mpc_headless.py -- input.md
blender --background --python mpc_headless.py -- --input "markdown string"
blender --background --python mpc_headless.py -- input.md --validate-only
```

### Input Format
Markdown tables with three sections:

#### Form Table
| Field                       | Description                | Default  |
|-----------------------------|----------------------------|----------|
| actionNameToCreate          | Output action name         | Required |
| bpm                         | Beats per minute           | 120      |
| beatsPerBar                 | Time signature             | 4        |
| blendFileToOutputAction     | Output blend file          | Required |
| poseBlendFile               | Source poses file          | Required |
| poseCatalog                 | Root catalog name          | Required |
| midiFile                    | MIDI input file            | Required |

#### Dance Table  
| Field                       | Description                | Default  |
|-----------------------------|----------------------------|----------|
| poseCatalog                 | Pose folder/catalog        | Required |
| track                       | MIDI track name            | Required |
| cycleMode                   | loop/random/pitch_follow/boomerang | loop     |
| interpolation               | Blender interpolation type | cubic    |
| preHold                     | Frames before transition   | 8        |
| postHold                    | Frames to hold pose        | 2        |

#### Video Table (Optional)
| Field                       | Description                | Default  |
|-----------------------------|----------------------------|----------|
| shouldCreateVideo?          | yes/no                     | no               |
| audioFile                   | Audio sync file            | Required if video|
| renderDir                   | Output directory           | Required if video|
| charFile                    | Character rig file         | Required if video|

### Example Input
```markdown
## Form Table
| Form label | value |
|------------|-------|
| actionNameToCreate | dance_01 |
| bpm | 120 |
| midiFile | music.mid |
| poseBlendFile | poses.blend |

## Dance Table
| poseCatalog | track | cycle mode | interpolation | preHold | postHold |
|-------------|-------|------------|---------------|---------|----------|
| hips | drums | random | back | 2 | 5 |
| hands | melody | loop | | | 3 |

## Video Table
| Form label | value |
|------------|-------|
| shouldCreateVideo? | yes |
| audioFile | music.mp3 |
| renderDir | renders/ |
| charFile | character.blend |
```

### Architecture

#### Modules
| Module                             | Purpose                      |
|------------------------------------|------------------------------|
| `headless/const.py`                | Default values and constants |
| `headless/models.py`               | Data models with validation  |
| `headless/parser.py`               | Markdown table parser        |
| `headless/pose_finder.py`          | Pose catalog discovery       |
| `headless/animation_generator.py`  | Animation creation           |
| `headless/video_renderer.py`       | Video export with audio      |
| `mpc_headless.py`                  | Main entry point             |

#### Key Classes
- **FormTable**: Form configuration with validation
- **DanceTable**: Dance rows configuration
- **HeadlessConfig**: Complete configuration container
- **MarkdownTableParser**: Parse markdown to config
- **AnimationGenerator**: Create Blender animations
- **VideoRenderer**: Render with audio sync

### Validation
Comprehensive validation with tabular output:
```
| Field                | Status | Message                    |
|----------------------|--------|----------------------------|
| actionNameToCreate   | ✓      | Action name provided       |
| midiFile             | ✗      | File not found: test.mid  |
| poseCatalog          | ✓      | Catalog: hips              |
```

### Pre/Post Hold Logic
- **preHold**: Don't start transitioning until X frames before
- **postHold**: Hold pose for X frames before transitioning out
- **MIN_FORCED_TRANSITION_FRAMES**: Always allow transition (default: 1)

### Testing
```bash
# Run all headless tests
python test/test_headless_all.py

# Individual test suites
python test/test_headless_models.py     # Data models
python test/test_headless_parser.py     # Parser logic
python test/test_headless_integration.py # Integration
python test/test_video_length.py        # Video duration validation

# Direct invocation tests
python3 mpc_headless.py headless_test/example_input.md --validate-only
python3 mpc_headless.py headless_test/example_input.md  # Full run with video
```

### Pose Catalog Resolution
1. Search for catalog by name in poseBlendFile
2. Find as subfolder (child or grandchild)
3. Error if multiple conflicts found
4. Poses ordered alphabetically by filename

### Bone Conflict Detection
✅ **Implemented**: Validates that different poseCatalogs don't use overlapping bones to prevent animation conflicts.
- Extracts bone names from FCurves in pose actions
- Compares bone sets between catalogs
- Reports specific conflicts and aborts if found

### Video Rendering
✅ **Working**: Successfully renders video with audio
1. Creates working copy of character file (POC shortcut)
2. Loads character from charFile
3. Applies generated action
4. Adds audio to sequencer
5. Renders MP4 with H.264 codec (320x240 POC resolution)
6. Output: `renders/test_YYMMDD_HHMMSS.mp4` (POC format)

**POC Limitations**:
- Resolution: 320x240 (for speed)
- Frame limit: 48 frames max
- Render samples: 1 (minimum quality)
- File copy instead of proper linking

## Headless Mode Status

### ✅ Completed Features
- Markdown table parsing (Form, Dance, Video tables)
- Pose catalog detection from Blender asset catalogs
- MIDI file loading and track analysis
- Animation generation with keyframes
- Bone conflict detection between catalogs
- Video rendering with audio (POC quality)
- Direct script invocation with `-s` flag
- Docker environment support
- Integration tests for video length

### 🚧 Future Work
- Increase render quality from 320x240 POC
- Remove 48-frame limit for production
- Implement proper asset linking (not file copying)
- Add "head" pose catalog support when available
- Output filename format: `YY-MM-DD-HH-MM-SS-charName-actionName.mp4`

## Version History
- **0.7.1**: Headless video rendering working, bone conflict detection
- **0.7.0**: Headless mode with markdown input
- **0.6.0**: PITCH_FOLLOW mode, Tone filtering, smart controls
- **0.5.0**: ACTION mode, BPM timing, pose reordering
- **0.4.0**: Workspace panels, config management
- **0.3.0**: Note filtering, cycle modes
- **0.2.0**: Multi-track support
- **0.1.0**: Initial release