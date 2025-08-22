#!/usr/bin/env python3
"""Setup Docker for MIDI Pose Cycler development."""

import subprocess
import sys
import shutil
import os

def run_command(cmd, capture=True):
    """Run a command and return success status."""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0, "", ""
    except FileNotFoundError:
        return False, "", "Command not found"

def main():
    print("🔧 Setting up Docker for MIDI Pose Cycler...")
    print()
    
    # Check if Docker is installed
    if not shutil.which("docker"):
        print("❌ Docker is not installed!")
        print("   Please install Docker Desktop for Windows or Docker Engine for Linux")
        print("   Visit: https://docs.docker.com/get-docker/")
        return 1
    
    # Check if Docker daemon is running
    success, _, _ = run_command(["docker", "info"])
    if not success:
        print("⚠️  Docker daemon is not running or not accessible")
        print()
        print("Trying to start Docker service...")
        
        # Try to start Docker
        started = False
        if shutil.which("systemctl"):
            success, _, _ = run_command(["sudo", "systemctl", "start", "docker"])
            started = success
        elif shutil.which("service"):
            success, _, _ = run_command(["sudo", "service", "docker", "start"])
            started = success
        else:
            print("❌ Could not start Docker automatically")
            print("   Please start Docker Desktop manually")
            return 1
        
        # Check again
        success, _, _ = run_command(["docker", "info"])
        if not success:
            print()
            print("❌ Docker still not accessible. This might be a permissions issue.")
            print()
            print("To fix Docker permissions on WSL/Linux:")
            print(f"  1. Add your user to the docker group:")
            print(f"     sudo usermod -aG docker {os.environ.get('USER', '$USER')}")
            print()
            print("  2. Log out and log back in (or run: newgrp docker)")
            print()
            print("  3. Verify with: docker run hello-world")
            return 1
    
    print("✅ Docker is installed and running")
    print()
    
    # Check docker compose
    compose_v2 = False
    compose_v1 = False
    
    success, _, _ = run_command(["docker", "compose", "version"])
    if success:
        print("✅ Docker Compose V2 is available")
        compose_v2 = True
    else:
        success, _, _ = run_command(["docker-compose", "--version"])
        if success:
            print("⚠️  You have Docker Compose V1 (docker-compose)")
            print("   Consider upgrading to V2 for better performance")
            print("   The Python scripts will handle both versions...")
            compose_v1 = True
    
    if not compose_v2 and not compose_v1:
        print("❌ Docker Compose not found")
        print("   Please install Docker Compose")
        return 1
    
    print()
    print("🎉 Docker setup complete!")
    print()
    print("Next steps:")
    if compose_v2:
        print("  1. Build the Docker image: docker compose build")
    else:
        print("  1. Build the Docker image: docker-compose build")
    print("  2. Launch interactive shell: python scripts/docker_shell.py")
    print("  3. Or run tests: python scripts/test_in_docker.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())