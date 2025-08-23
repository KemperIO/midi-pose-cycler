# MIDI Pose Cycler


A Blender 4.5+ extension for synchronizing pose/action animations to MIDI events. Generate complex character animations driven by musical timing.

## 🐳 Docker Development Environment

### Prerequisites

#### Docker Desktop on Windows (for WSL2)
https://docs.docker.com/desktop/features/wsl/

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd midi-pose-cycler

# 2. Authenticate Claude CLI on your WSL host (one-time setup)
claude  # Run this in WSL to login with your Claude account

# 3. Build and launch interactive Docker shell
./scripts/docker-shell.sh

# 4. Inside container, Claude CLI is already authenticated!
claude  # Uses your WSL ~/.claude config automatically

# 5. You also have access to:
#    - blender (Blender 4.5 for testing)
#    - python3 (for running tests)

# Example: Run headless animation generation
blender --background --python mpc_headless.py -- test/example_input.md
```

### 🔐 Claude CLI Authentication

**Simple & Secure Setup**:

1. **Authenticate Claude CLI on your WSL host** (one-time setup):
   ```bash
   # In WSL (outside Docker), run:
   claude
   # Follow the prompts to login with your Claude account
   ```

2. **That's it!** Docker will automatically mount your `~/.claude` config directory

**How it works**:
- Your Claude credentials stay in WSL `~/.claude` directory
- Docker mounts this directory read-write into the container
- Claude CLI in the container uses `CLAUDE_CONFIG_DIR` environment variable
- No API keys or tokens in code, no `.env` file needed!

**Security benefits**:
- ✅ No credentials in Docker image
- ✅ No credentials in git repository  
- ✅ Uses your existing Claude authentication
- ✅ Automatically stays in sync with your WSL Claude config

### Docker Setup Details

The Docker environment includes:
- **Claude CLI** - Full Claude Code installation for isolated development
- **Blender 4.5** - Full installation with Python API
- **Node.js 20** - Required for Claude CLI
- **Python 3.11** - Matching Blender's Python version
- **Development tools** - git, vim, testing frameworks
- **Volume mapping** - Bidirectional file sync with host

### How Docker Volume Mapping Works

```yaml
volumes:
  - .:/workspace:rw  # Maps your local directory to container
```

**File Synchronization:**
- ✅ **Bidirectional sync** - Changes in either location are reflected immediately
- ✅ **VSCode (WSL)** ↔️ **Docker Container** ↔️ **Claude CLI (in container)** - All see the same files
- ✅ Real-time updates - No manual sync needed
- ✅ **Claude CLI in Docker** - Isolated environment with full access to project files

**Example workflow:**
1. Launch Docker container with `./scripts/docker-shell.sh`
2. Run `claude` inside container to start Claude CLI
3. Claude makes changes to files in `/workspace` 
4. Changes immediately visible in your WSL/Windows filesystem
5. VSCode (running on host) sees updates in real-time
6. Test changes with Blender (also in container)

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
# Start Claude CLI for development
claude

# Check available tools
blender --version
node --version
claude --version

# Run headless tests
python3 test/test_headless_all.py

# Generate animation from markdown
blender --background --python mpc_headless.py -- input.md

# Validate input without generating
blender --background --python mpc_headless.py -- input.md --validate-only
```

### Using Claude CLI in Docker

The container includes a full Claude CLI installation:

```bash
# Inside the container
claude  # Start Claude CLI

# Claude can now:
# - Edit files in /workspace (synced to your host)
# - Run Blender tests directly
# - Execute Python scripts
# - All changes are immediately visible on host
```

**Note**: Your Claude API key is stored in the persistent volume `claude-config`, so you only need to authenticate once.

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
