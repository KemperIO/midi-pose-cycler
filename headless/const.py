"""Constants and default values for headless MIDI pose cycler."""

from typing import Final

# Animation defaults
DEFAULT_INTERPOLATION: Final[str] = "cubic"
DEFAULT_CYCLE_MODE: Final[str] = "loop"
DEFAULT_PRE_HOLD: Final[int] = 8
DEFAULT_POST_HOLD: Final[int] = 2
DEFAULT_BPM: Final[float] = 120.0
DEFAULT_BEATS_PER_BAR: Final[int] = 4

# Timing constants
MIN_FORCED_TRANSITION_FRAMES: Final[int] = 1
DEFAULT_FPS: Final[int] = 24

# Valid options for enums
VALID_INTERPOLATIONS: Final[set[str]] = {
    "linear", "constant", "bezier", "sine", "quad", "cubic", 
    "quart", "quint", "expo", "circ", "back", "bounce", "elastic", "quartic"
}

VALID_CYCLE_MODES: Final[set[str]] = {
    "loop", "random", "pitch_follow", "boomerang"
}

# File format constants
VIDEO_CODEC: Final[str] = "H264"
VIDEO_CONTAINER: Final[str] = "MPEG4"  # Blender uses MPEG4 for MP4 container
VIDEO_QUALITY: Final[str] = "MEDIUM"

# Render settings
RENDER_RESOLUTION_X: Final[int] = 1920
RENDER_RESOLUTION_Y: Final[int] = 1080
RENDER_RESOLUTION_PERCENTAGE: Final[int] = 100