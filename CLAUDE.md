# MIDI Pose Cycler - Blender Extension

**This is a public repository**

## Overview
An opinionated Blender 4.5+ extension for creating pose-cycling animations synchronized to MIDI events. This plugin provides a dedicated workspace and editor-style interface for animating character poses in rhythm with musical tracks.

### Workspace Approach
Since Blender addons cannot create true new editor types (SpaceTypes are hardcoded in C++), this extension provides:
1. **Custom Workspace**: A dedicated "MIDI Pose Cycler" workspace with optimized layout
2. **Three-Column Layout**: Main controls, Poses, and MIDI data panels
3. **Responsive Design**: Automatically stacks columns vertically in narrow windows
4. **Editor-Style UI**: Full-space utilization similar to Shader Editor or Compositor

## Features
- **MIDI File Analysis**: Load and analyze MIDI files to extract track and note information
- **Track Selection**: Choose specific MIDI tracks for animation timing (tracks with same name are automatically merged)
- **Note Filtering**: Optionally filter specific notes from tracks
- **Pose Management**: Select and order poses from your project's action library
- **Interpolation Control**: Choose from 13 different interpolation types for smooth transitions
- **Frame Hold Control**: Configure how long each pose is held before transitioning
- **Real-time FPS Integration**: Automatically uses project FPS settings

## Installation

### Method 1: Manual Installation
1. Zip the `midi-pose-cycler` folder
2. In Blender: Edit → Preferences → Add-ons
3. Click "Install..." and select the zip file
4. Enable "Animation: MIDI Pose Cycler"

### Method 2: Development Installation
1. Copy the `midi-pose-cycler` folder to Blender's extensions directory:
   - Windows: `%APPDATA%\Blender Foundation\Blender\4.5\extensions\`
   - macOS: `~/Library/Application Support/Blender/4.5/extensions/`
   - Linux: `~/.config/blender/4.5/extensions/`
2. Restart Blender
3. Enable the extension in Preferences

## Usage

### 0. Setup Workspace (Recommended)
- Go to Window menu → MIDI Pose Cycler
- Or manually create workspace with operator: `bpy.ops.midipose.create_workspace()`
- This creates a comprehensive workspace with 8 specialized panes:
  - **File Browser** (left top) - Browse and drag MIDI files
  - **Asset Browser** (left bottom) - Browse and drag pose actions
  - **3D Viewport** (center) - Preview animation
  - **Action Editor** (bottom center) - View generated keyframes
  - **Sequencer** (very bottom) - Audio timeline reference
  - **Properties - Main** (right top) - Main controls and settings
  - **Properties - Poses** (right middle) - Pose selection and ordering
  - **Properties - MIDI** (right bottom) - MIDI tracks and notes

### 1. Prepare Your Poses
- Create pose actions in your project (e.g., "neck-left", "neck-right", "pose-up", etc.)
- Ensure poses are defined at frame 0 of their respective actions
- Name poses descriptively (avoid starting with "Midi" as these are filtered out)

### 2. Access the Plugin
- Open the 3D Viewport
- Press N to open the sidebar
- Navigate to the "MIDI Pose" tab

### 3. Load MIDI File
- Click the folder icon to browse for a MIDI file
- The plugin will automatically analyze and display available tracks

### 4. Select and Analyze Track
- Click on a track name to select it
- The track analysis will show:
  - Note counts
  - Time range
  - Individual notes with frequencies

### 5. Configure Poses
- Click "Refresh Poses" to load available poses from your project
- Select poses in the order you want them to cycle
- The animation will cycle through selected poses sequentially

### 6. Configure Settings
- **Hold Frames**: Number of frames to hold each pose (default: 3)
- **Interpolation**: Transition type between poses (default: EXPO)
  - CONSTANT: No interpolation (hard cuts)
  - LINEAR: Linear interpolation
  - EXPO: Exponential easing (recommended for organic motion)
  - And 10 more options for different effects
- **Total Frames**: Maximum animation length (default: 240)

### 7. Optional: Filter Notes
- Enable "Filter Notes" to animate only on specific MIDI notes
- Select which notes to include in the animation

### 8. Render Animation
- Select the object to animate (must be active)
- Click "RENDER ANIMATION"
- The plugin will:
  - Create/update an action called "MidiPoseCyclingAnimation"
  - Insert keyframes at MIDI note timings
  - Apply hold and interpolation settings
  - Update scene frame range

## Technical Details

### MIDI Processing
- Uses `mido` library for MIDI parsing (auto-installed if missing)
- Supports standard MIDI files (.mid, .midi)
- Processes note_on events with velocity > 0
- Converts MIDI timing to Blender frames using project FPS

### Animation System
- Creates keyframes on the active object's action
- Pose at note timing: CONSTANT interpolation (holds the pose)
- Pose at hold end: User-selected interpolation (transition)
- Automatically handles overlapping notes

### File Structure
```
midi-pose-cycler/
├── __init__.py           # Plugin registration
├── blender_manifest.toml # Extension metadata
├── midi_core.py          # MIDI analysis functions
├── animation_renderer.py # Animation generation
├── ui_operators.py       # Blender operators
├── ui_panel.py          # UI panels
└── CLAUDE.md            # This documentation
```

## Opinionated Defaults
- **FPS**: Uses project settings (typically 24)
- **BPM**: Extracted from MIDI file
- **Hold Frames**: 3 frames (1/8 second at 24fps)
- **Interpolation**: EXPO (smooth, organic transitions)
- **Total Frames**: 240 (10 seconds at 24fps)

## Tips
1. **Pose Order Matters**: Poses cycle in the order selected
2. **Test with Few Poses First**: Start with 2-3 poses to verify timing
3. **Use EXPO for Organic Motion**: Best for character animation
4. **Use CONSTANT for Robotic Effects**: Creates stop-motion style
5. **Preview Before Final Render**: Scrub timeline to check animation

## Troubleshooting

### "No poses found"
- Click "Refresh Poses" to scan project actions
- Ensure poses are saved as actions in the project
- Check that pose names don't start with "Midi"

### "No matching notes found"
- Verify the correct track is selected
- Check if note filtering is too restrictive
- Ensure MIDI file contains note_on events

### Animation looks wrong
- Verify poses are defined at frame 0 of their actions
- Check interpolation settings
- Ensure active object is the intended target

## Future Enhancements (Potential)
- [ ] Drag-and-drop MIDI file support
- [ ] Visual note timeline preview
- [ ] Pose preview thumbnails
- [ ] MIDI tempo changes support
- [ ] Multi-object animation support
- [ ] Export/import animation presets

## Dependencies
- Blender 4.5+
- Python 3.11+ (included with Blender)
- mido (bundled with extension)

## License
GPL-3.0

## Blender Extension Guidelines Compliance

This extension adheres to Blender's official addon guidelines:

### Critical Compliance Points
1. **Online Access**: Respects `bpy.app.online_access` - no internet connections made
2. **Add-on Isolation**: Self-contained, does not interfere with other add-ons
3. **Module Management**: mido library is bundled within the extension namespace (vendor/)
4. **File System**: Supports read-only "System" installation, no writes to own directory
5. **No External Dependencies**: Does not install Python modules or use pip

### Code Standards
- Follows PEP 8 style guidelines
- Compatible with Blender 4.5+ API
- Uses proper Blender property registration
- Implements standard operator patterns

### Version Guidelines
- Version format: MAJOR.MINOR.PATCH (semantic versioning)
- Current version: 1.0.0 (initial release)
- Development versions use 0.x.x numbering
- Version updates follow Blender's extension versioning conventions