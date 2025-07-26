#!/bin/bash

# Chapter Agent Docker Launcher
# This script makes it easy to run the Chapter Agent with proper workspace access

set -e

echo "🤖 Chapter Agent Docker Launcher"
echo "================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ No .env file found!"
    echo "Please create a .env file with your GEMINI_API_KEY"
    echo "You can copy .env.example as a starting point:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Environment file found"
echo ""

# Build the image if it doesn't exist or if requested
if [ "$1" = "--build" ] || ! docker images | grep -q chapter-agent-chapter-agent; then
    echo "🔨 Building Docker image..."
    docker-compose build
    echo "✅ Image built successfully"
    echo ""
fi

echo "🚀 Starting Chapter Agent..."
echo ""
echo "📁 The agent can access any project on your host machine"
echo "   Use /host/ prefix for external projects"
echo "   Example: /host/home/$(whoami)/my-project"
echo ""
echo "Press Ctrl+C to stop the agent"
echo "================================="
echo ""

# Export user ID and group ID for proper permissions
# UID is readonly in bash, so we'll use different variable names
export DOCKER_UID=$(id -u)
export DOCKER_GID=$(id -g)

# Run the agent
docker-compose run --rm chapter-agent
