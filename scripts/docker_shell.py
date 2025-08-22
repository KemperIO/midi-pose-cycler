#!/usr/bin/env python3
"""Launch interactive Docker shell for MIDI Pose Cycler development."""

import subprocess
import sys
import shutil

def get_compose_command():
    """Determine whether to use 'docker compose' or 'docker-compose'."""
    # Try docker compose v2 first
    result = subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True,
        check=False
    )
    if result.returncode == 0:
        return ["docker", "compose"]
    
    # Fall back to docker-compose v1
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    
    # Default to v2 syntax and let it fail with proper error
    return ["docker", "compose"]

def main():
    print("🚀 Starting MIDI Pose Cycler Docker environment...")
    
    # Check if docker is accessible
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, ["docker", "info"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker daemon not accessible. Try:")
        print("   1. sudo usermod -aG docker $USER")
        print("   2. `wsl --shutdown`, reopen, try again")
        return 1
    
    # Get the compose command
    compose_cmd = get_compose_command()
    
    # Build the image if needed
    print("Building Docker image...")
    result = subprocess.run(compose_cmd + ["build"], check=False)
    if result.returncode != 0:
        print("❌ Docker build failed")
        return 1
    
    # Start the container in interactive mode
    print("Launching interactive shell...")
    result = subprocess.run(
        compose_cmd + ["run", "--rm", "midi-pose-cycler", "bash"],
        check=False
    )
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())