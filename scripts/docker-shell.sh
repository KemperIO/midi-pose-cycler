#!/bin/bash
# Launch interactive Docker shell for MIDI Pose Cycler development

echo "🚀 Starting MIDI Pose Cycler Docker environment..."

# Check if docker is accessible
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon not accessible. Try:"
    echo "   1. sudo usermod -aG docker $USER"
    echo "   2. `wsl --shutdown`, reopen, try again"
    exit 1
fi

# Build the image if needed
docker compose build

# Start the container in interactive mode
docker compose run --rm midi-pose-cycler bash
