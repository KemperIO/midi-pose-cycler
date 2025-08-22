#!/bin/bash
# Setup Docker for MIDI Pose Cycler development

echo "🔧 Setting up Docker for MIDI Pose Cycler..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "   Please install Docker Desktop for Windows or Docker Engine for Linux"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker daemon is not running or not accessible"
    echo ""
    echo "Trying to start Docker service..."
    
    # Try to start Docker
    if command -v systemctl &> /dev/null; then
        sudo systemctl start docker
    elif command -v service &> /dev/null; then
        sudo service docker start
    else
        echo "❌ Could not start Docker automatically"
        echo "   Please start Docker Desktop manually"
        exit 1
    fi
    
    # Check again
    if ! docker info > /dev/null 2>&1; then
        echo ""
        echo "❌ Docker still not accessible. This might be a permissions issue."
        echo ""
        echo "To fix Docker permissions on WSL/Linux:"
        echo "  1. Add your user to the docker group:"
        echo "     sudo usermod -aG docker $USER"
        echo ""
        echo "  2. Log out and log back in (or run: newgrp docker)"
        echo ""
        echo "  3. Verify with: docker run hello-world"
        exit 1
    fi
fi

echo "✅ Docker is installed and running"
echo ""

# Check docker compose
if docker compose version > /dev/null 2>&1; then
    echo "✅ Docker Compose V2 is available"
elif docker-compose --version > /dev/null 2>&1; then
    echo "⚠️  You have Docker Compose V1 (docker-compose)"
    echo "   Consider upgrading to V2 for better performance"
    echo "   The scripts will be updated to use docker-compose instead..."
    
    # Update scripts to use docker-compose
    sed -i 's/docker compose/docker-compose/g' scripts/docker-shell.sh
    sed -i 's/docker compose/docker-compose/g' scripts/test-in-docker.sh
    echo "   Scripts updated to use docker-compose"
else
    echo "❌ Docker Compose not found"
    echo "   Please install Docker Compose"
    exit 1
fi

echo ""
echo "🎉 Docker setup complete!"
echo ""
echo "Next steps:"
echo "  1. Build the Docker image: docker compose build"
echo "  2. Launch interactive shell: ./scripts/docker-shell.sh"
echo "  3. Or run tests: ./scripts/test-in-docker.sh"