#!/bin/bash
# Launch interactive Docker shell for MIDI Pose Cycler development

echo "🚀 Starting MIDI Pose Cycler Docker environment..."

# Build the image if needed
docker-compose build

# Start the container in interactive mode
docker-compose run --rm midi-pose-cycler bash