#!/bin/bash
#
# Focused Docker Cleanup Script
# 
# This script focuses ONLY on Docker cleanup, nothing else.
# It's safe to run and won't affect running containers.
#

set -e

echo "🐳 Docker Cleanup - Focused"
echo "=========================="
echo ""

# Show current state
echo "📊 Current Docker Usage:"
docker system df
echo ""

# Show what's reclaimable
RECLAIMABLE=$(docker system df --format "{{.Reclaimable}}" | head -1)
echo "💾 Reclaimable Space: $RECLAIMABLE"
echo ""

# Check for dangling images
DANGLING=$(docker images --filter "dangling=true" -q | wc -l)
echo "🔍 Dangling Images: $DANGLING"
if [ "$DANGLING" -gt 0 ]; then
    echo "   Removing dangling images..."
    docker image prune -f
else
    echo "   ✅ No dangling images to remove"
fi
echo ""

# Check for stopped containers
STOPPED=$(docker ps -a --filter "status=exited" -q | wc -l)
echo "🔍 Stopped Containers: $STOPPED"
if [ "$STOPPED" -gt 0 ]; then
    echo "   Removing stopped containers..."
    docker container prune -f
else
    echo "   ✅ No stopped containers to remove"
fi
echo ""

# Check for unused volumes
UNUSED_VOLUMES=$(docker volume ls --filter "dangling=true" -q | wc -l)
echo "🔍 Unused Volumes: $UNUSED_VOLUMES"
if [ "$UNUSED_VOLUMES" -gt 0 ]; then
    echo "   Removing unused volumes..."
    docker volume prune -f
else
    echo "   ✅ No unused volumes to remove"
fi
echo ""

# Clean build cache
echo "🧹 Cleaning build cache..."
docker builder prune -af
echo ""

# Final state
echo "📊 Final Docker Usage:"
docker system df
echo ""

# Disk space
echo "💾 Disk Space:"
df -h /home/founders/demoversion | tail -1
echo ""

echo "✅ Docker cleanup complete!"
echo ""
echo "💡 Note: If 'Reclaimable' space still shows, it's likely from:"
echo "   - Shared image layers (can't be removed while images are in use)"
echo "   - Images that are currently running (can't be removed)"
echo ""
echo "   To free more space, you would need to:"
echo "   - Stop and remove old container versions"
echo "   - Remove unused legacy directories"
echo "   - Clean up other non-Docker files"





