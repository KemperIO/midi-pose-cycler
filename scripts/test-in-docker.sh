#!/bin/bash
# Run headless tests in Docker container

echo "🧪 Running headless tests in Docker..."

# Check if docker is accessible
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon not accessible. Try:"
    echo "   1. sudo service docker start"
    echo "   2. sudo usermod -aG docker $USER"
    echo "   3. Log out and back in"
    exit 1
fi

# Build if needed
docker compose build

# Run tests
docker compose run --rm midi-pose-cycler bash -c "
    echo '=== Testing Blender Installation ==='
    blender --version
    
    echo ''
    echo '=== Running Headless Tests ==='
    python3 test/test_headless_all.py
    
    echo ''
    echo '=== Testing Headless Mode (Validation Only) ==='
    blender --background --python mpc_headless.py -- test/example_input.md --validate-only
"