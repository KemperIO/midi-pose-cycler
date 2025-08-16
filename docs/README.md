# MIDI Pose Cycler for Blender

A Blender 4.5+ extension for creating pose-cycling animations synchronized to MIDI events.

## Quick Start

1. **Install**: Zip this folder and install via Blender Preferences → Add-ons
2. **Access**: View3D → Sidebar (N) → MIDI Pose tab
3. **Use**:
   - Load MIDI file
   - Select track
   - Choose poses
   - Click "RENDER ANIMATION"

## Features

- MIDI file analysis with track/note breakdown
- Pose cycling with configurable order
- 13 interpolation types
- Note filtering
- Frame hold control

See CLAUDE.md for detailed documentation.

## Local addon development
Symlink mfaa

```ps1
$addonPath = "$env:APPDATA\Blender Foundation\Blender\4.5\scripts\addons\midi-pose-cycler"
$repoPath  = "...\midi-pose-cycler"
New-Item -ItemType SymbolicLink -Path $addonPath -Target $repoPath -Force
```
