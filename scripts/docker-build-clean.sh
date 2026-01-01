#!/bin/bash
# Docker Build and Clean Script
# Builds Docker images, restarts containers, and cleans up dangling build cache to prevent disk space issues

set -e

echo "🔨 Building Docker images..."
echo "============================"

# Build the images
docker-compose -f docker-compose.prod.yml build "$@"

echo ""
echo "🔄 Starting infrastructure containers..."
echo "======================================="

# Create network if it doesn't exist (for external networks)
docker network create symphainy-platform_smart_city_net 2>/dev/null || true

# Start infrastructure services first (required for backend)
cd symphainy-platform
docker-compose -f docker-compose.infrastructure.yml up -d 2>/dev/null || echo "⚠️  Infrastructure containers may already be running"
cd ..

echo ""
echo "🔄 Restarting application containers..."
echo "======================================="

# Stop and remove existing containers, then start fresh
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "🧹 Cleaning up Docker build cache..."
echo "===================================="

# Prune build cache (dangling images, unused build cache)
# -a: Remove all unused images, not just dangling ones
# -f: Force removal without confirmation
docker builder prune -af

echo ""
echo "✅ Build, restart, and cleanup complete!"
echo ""
echo "📊 Current Docker disk usage:"
docker system df

echo ""
echo "📋 Container status:"
docker-compose -f docker-compose.prod.yml ps

