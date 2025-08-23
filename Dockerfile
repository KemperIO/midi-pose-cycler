# Dockerfile for MIDI Pose Cycler with Blender 4.5 and Claude CLI
# Based on Claude Code's recommended patterns from:
# https://github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile

FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    xvfb \
    libx11-6 \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxrender1 \
    libgl1-mesa-glx \
    libglu1-mesa \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    zsh \
    sudo \
    vim \
    nano \
    ca-certificates \
    gnupg \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 (required for Claude CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Blender 4.5
RUN wget https://download.blender.org/release/Blender4.5/blender-4.5.0-linux-x64.tar.xz \
    && tar -xf blender-4.5.0-linux-x64.tar.xz \
    && mv blender-4.5.0-linux-x64 /opt/blender \
    && ln -s /opt/blender/blender /usr/local/bin/blender \
    && rm blender-4.5.0-linux-x64.tar.xz

# Create non-root user (following Claude Code pattern)
ARG USERNAME=developer
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up npm global directory for the user
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH=$PATH:/usr/local/share/npm-global/bin

# Create npm global directory with proper permissions
RUN mkdir -p /usr/local/share/npm-global \
    && chown -R $USERNAME:$USERNAME /usr/local/share/npm-global

# Install Claude CLI globally
ARG CLAUDE_CODE_VERSION=latest
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

# Install Python dependencies globally
RUN pip3 install --upgrade pip \
    && pip3 install \
    numpy \
    pytest \
    black \
    mypy \
    ipython

# Set up workspace directory with proper permissions
WORKDIR /workspace
RUN chown -R $USERNAME:$USERNAME /workspace

# Switch to non-root user
USER $USERNAME

# Set up user environment
ENV HOME=/home/$USERNAME
ENV SHELL=/bin/bash

# Create directories for development
RUN mkdir -p $HOME/.cache \
    && mkdir -p $HOME/.local/share \
    && mkdir -p $HOME/.config \
    && mkdir -p $HOME/.claude

# Set Python path for Blender's Python
ENV PYTHONPATH=/opt/blender/4.5/python/lib/python3.11/site-packages:$PYTHONPATH

# Set Blender preferences for headless operation
ENV BLENDER_USER_SCRIPTS=/workspace
ENV BLENDER_USER_CONFIG=/home/$USERNAME/.config/blender/4.5

# Set Claude Code environment
ENV CLAUDE_CODE_IN_DOCKER=true
# Point Claude to config directory that will be mounted from host
ENV CLAUDE_CONFIG_DIR=/home/developer/.claude

# Create volume mount points
VOLUME ["/workspace", "/home/$USERNAME/.cache", "/home/$USERNAME/.claude"]

# Default shell
CMD ["/bin/bash"]