# MIDI Pose Cycler

A Blender 4.5+ extension for synchronizing pose/action animations to MIDI events. Generate complex character animations driven by musical timing.

## 🐳 Docker Development Environment

### Docker Desktop on Windows to support wsl2
https://docs.docker.com/desktop/features/wsl/


### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd midi-pose-cycler

# 2. Launch interactive Docker shell
./scripts/docker-shell.sh

# 3. Inside container, run headless animation generation
blender --background --python mpc_headless.py -- test/example_input.md
```

### Docker Setup Details

The Docker environment includes:
- **Blender 4.5** - Full installation with Python API
- **Python 3.11** - Matching Blender's Python version
- **Development tools** - git, vim, testing frameworks
- **Volume mapping** - Bidirectional file sync

### How Docker Volume Mapping Works

```yaml
volumes:
  - .:/workspace:rw  # Maps your local directory to container
```

**File Synchronization:**
- ✅ **Bidirectional sync** - Changes in either location are reflected immediately
- ✅ **VSCode (WSL)** ↔️ **Docker** ↔️ **Claude Code** - All see the same files
- ✅ Real-time updates - No manual sync needed

**Example workflow:**
1. Edit files in VSCode on Windows/WSL
2. Changes immediately visible in Docker container
3. Run Blender headless in Docker
4. Output files appear in your local directory

### Docker Commands

```bash
# Build the Docker image
docker-compose build

# Launch interactive shell
docker-compose run --rm midi-pose-cycler bash

# Run tests in Docker
./scripts/test-in-docker.sh

# Run specific command
docker-compose run --rm midi-pose-cycler blender --version

# Clean up
docker-compose down
docker system prune  # Remove unused containers/images
```

### Inside the Container

Once in the Docker shell:

```bash
# Check Blender version
blender --version

# Run headless tests
python3 test/test_headless_all.py

# Generate animation from markdown
blender --background --python mpc_headless.py -- input.md

# Validate input without generating
blender --background --python mpc_headless.py -- input.md --validate-only
```

### File Permissions

The container runs as user `developer` (UID 1000) to match typical host permissions. If you encounter permission issues:

```bash
# In docker-compose.yml, adjust USER_UID/USER_GID:
args:
  USER_UID: 1000  # Change to match your user: id -u
  USER_GID: 1000  # Change to match your group: id -g
```

### Development with VSCode

**Option 1: Dev Container (Recommended)**
1. Install "Dev Containers" extension in VSCode
2. Open project folder
3. Click "Reopen in Container" when prompted
4. VSCode runs inside Docker with full Blender access

**Option 2: Local VSCode + Docker Testing**
1. Edit files locally in VSCode
2. Run `./scripts/test-in-docker.sh` to test
3. Files sync automatically via volume mapping

## 📝 Headless Mode

Generate animations from markdown table configuration without Blender GUI.

### Input Format

Create a markdown file with three tables:

```markdown
## Form Table
| Form label | value |
|------------|-------|
| actionNameToCreate | my_animation |
| bpm | 120 |
| midiFile | music.mid |
| poseBlendFile | poses.blend |

## Dance Table
| poseCatalog | track | cycle mode | interpolation | preHold | postHold |
|-------------|-------|------------|---------------|---------|----------|
| hips | drums | random | back | 2 | 5 |
| hands | melody | loop | cubic | | 3 |

## Video Table (Optional)
| Form label | value |
|------------|-------|
| shouldCreateVideo? | yes |
| audioFile | music.mp3 |
| renderDir | renders/ |
| charFile | character.blend |
```

### Usage

```bash
# Validate configuration
blender --background --python mpc_headless.py -- config.md --validate-only

# Generate animation
blender --background --python mpc_headless.py -- config.md

# With video rendering
blender --background --python mpc_headless.py -- config_with_video.md
```

## 🎵 Features

- **Multi-track MIDI** - Animate different body parts to different instruments
- **Cycle Modes** - Loop, Random, Boomerang, Pitch-Follow
- **Smart Timing** - Musical bars/beats or frame-based
- **Pose Management** - Drag-and-drop reordering
- **Note Filtering** - Per-track note selection
- **Video Export** - Render with audio synchronization

## 📁 Project Structure

```
midi-pose-cycler/
├── Dockerfile              # Docker container setup
├── docker-compose.yml      # Docker orchestration
├── mpc_headless.py        # Headless entry point
├── headless/              # Headless mode modules
│   ├── models.py          # Data models & validation
│   ├── parser.py          # Markdown parser
│   ├── animation_generator.py  # Animation logic
│   └── video_renderer.py  # Video export
├── src/                   # Blender addon source
├── test/                  # Test suite
│   ├── test_headless_*.py # Headless tests
│   └── example_input.md   # Example configuration
└── scripts/               # Helper scripts
    ├── docker-shell.sh    # Launch Docker shell
    └── test-in-docker.sh  # Run tests in Docker
```

## 🧪 Testing

### Run All Tests
```bash
# In Docker
./scripts/test-in-docker.sh

# Or directly
python test/test_headless_all.py
```

### Test Coverage
- Model validation
- Markdown parsing
- Animation generation
- Integration tests

## 📚 Documentation

- [CLAUDE.md](CLAUDE.md) - Detailed technical documentation
- [Example Input](test/example_input.md) - Sample configuration

## 📄 License

GPL-3.0 - See LICENSE file for details