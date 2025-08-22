#!/bin/bash
# Run headless tests in Docker container

echo "🧪 Running headless tests in Docker..."

# Build if needed
docker-compose build

# Run tests
docker-compose run --rm midi-pose-cycler bash -c "
    echo '=== Testing Blender Installation ==='
    blender --version
    
    echo ''
    echo '=== Running Headless Tests ==='
    python3 test/test_headless_all.py
    
    echo ''
    echo '=== Testing Headless Mode (Validation Only) ==='
    blender --background --python mpc_headless.py -- test/example_input.md --validate-only
"