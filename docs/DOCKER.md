# Docker Development Environment - Detailed Guide

## How Volume Mapping Works

### The Key Line in docker-compose.yml
```yaml
volumes:
  - .:/workspace:rw  # THIS is the magic
```

This creates a **bind mount** that directly maps your local project directory to `/workspace` in the container.

### What This Means

| Location | Path | Description |
|----------|------|-------------|
| **Your Computer (Windows/WSL)** | `C:\...\midi-pose-cycler\` or `/mnt/c/.../midi-pose-cycler/` | Original project files |
| **Docker Container** | `/workspace/` | Same files, live mounted |
| **VSCode (WSL)** | `/mnt/c/.../midi-pose-cycler/` | Same files |
| **Claude Code** | Whatever path you opened | Same files |

### File Sync Behavior

**✅ IMMEDIATE SYNC - No copying needed!**

1. **Edit in VSCode** → File changes on disk → Instantly visible in Docker
2. **Run Blender in Docker** → Creates output file → Instantly visible in VSCode
3. **Claude Code edits** → Changes files → Both Docker and VSCode see it

### Example Workflow

```bash
# Terminal 1: VSCode integrated terminal (WSL)
$ pwd
/mnt/c/Users/words/OneDrive/Desktop/code/midi-pose-cycler
$ echo "test" > test.txt

# Terminal 2: Docker container
docker-compose run --rm midi-pose-cycler bash
developer@container:/workspace$ cat test.txt
test  # <-- Same file, instantly available!

developer@container:/workspace$ blender --background --python mpc_headless.py -- input.md
# Creates output.blend

# Back in Terminal 1: VSCode (WSL)
$ ls *.blend
output.blend  # <-- Output immediately visible!
```

## Understanding Bind Mounts vs Volumes

### Bind Mount (What we use)
```yaml
volumes:
  - .:/workspace:rw  # Bind mount - maps directory directly
```
- **Direct mapping** of host directory to container
- **Real-time bidirectional** sync
- **Same inode** - it's literally the same file
- Changes are instant in both directions

### Named Volume (For cache/config)
```yaml
volumes:
  - blender-cache:/home/developer/.cache  # Named volume
```
- Docker-managed storage
- Persists between container runs
- Isolated from host filesystem
- Good for cache/temporary data

## File Permissions

### Default Setup
```dockerfile
ARG USER_UID=1000  # Standard Linux first user
ARG USER_GID=1000
```

### If You Get Permission Errors

1. **Check your host UID/GID:**
```bash
# On WSL/Linux
id -u  # Your UID (probably 1000)
id -g  # Your GID (probably 1000)
```

2. **Update docker-compose.yml if different:**
```yaml
build:
  args:
    USER_UID: 1001  # Match your actual UID
    USER_GID: 1001  # Match your actual GID
```

3. **Rebuild container:**
```bash
docker-compose build --no-cache
```

## Performance Considerations

### WSL2 File System Performance

| File Location | Performance | Use For |
|---------------|------------|---------|
| `/mnt/c/...` (Windows drive) | Slower | Source code (needs Windows access) |
| `/home/username/...` (WSL drive) | Faster | Build artifacts, cache |
| Docker container `/workspace` | Same as host | Mirrors wherever you mounted from |

### Optimization Tips

1. **Keep source on Windows** if you need Windows tool access
2. **Use WSL2 native filesystem** for better performance:
   ```bash
   # Copy project to WSL filesystem
   cp -r /mnt/c/path/to/project ~/projects/
   cd ~/projects/midi-pose-cycler
   docker-compose up
   ```

3. **Cache heavy operations** in named volumes:
   ```yaml
   volumes:
     - pip-cache:/home/developer/.cache/pip
   ```

## Troubleshooting

### Files not syncing?
```bash
# Verify mount in container
docker-compose run --rm midi-pose-cycler bash -c "mount | grep workspace"
# Should show: /dev/sdc on /workspace type ext4 (rw,...)
```

### Permission denied?
```bash
# Check file ownership in container
docker-compose run --rm midi-pose-cycler ls -la /workspace
# Files should be owned by 'developer' user
```

### Container can't find files?
```bash
# Ensure you're in the right directory
docker-compose run --rm midi-pose-cycler pwd
# Should output: /workspace
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Host Machine (Windows)                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │                    WSL2                          │  │
│  │                                                  │  │
│  │  ┌────────────────┐    ┌──────────────────┐    │  │
│  │  │    VSCode      │───▶│  Project Files   │◀───│──│───▶ Claude Code
│  │  │                │    │  /mnt/c/.../     │    │  │
│  │  └────────────────┘    └──────────────────┘    │  │
│  │                              ▲                  │  │
│  │                              │                  │  │
│  │                         Bind Mount              │  │
│  │                              │                  │  │
│  │                              ▼                  │  │
│  │                   ┌──────────────────┐         │  │
│  │                   │  Docker Container│         │  │
│  │                   │                  │         │  │
│  │                   │  /workspace/ ────┼─────────│──│───▶ Same Files!
│  │                   │                  │         │  │
│  │                   │  Blender 4.5     │         │  │
│  │                   └──────────────────┘         │  │
│  │                                                 │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **It's the SAME files** - not copies, not synced, literally the same
2. **Changes are instant** - no sync delay, no refresh needed
3. **Bidirectional** - edit anywhere, see everywhere
4. **Persistent** - files remain after container stops
5. **Performance** - as fast as your host filesystem

## Common Commands

```bash
# See what's mounted in container
docker-compose run --rm midi-pose-cycler findmnt /workspace

# Watch files change in real-time (host)
watch -n 1 ls -la

# Watch files change in container
docker-compose run --rm midi-pose-cycler watch -n 1 ls -la /workspace

# Test file creation from container
docker-compose run --rm midi-pose-cycler touch /workspace/from-docker.txt
ls from-docker.txt  # Should exist on host immediately
```