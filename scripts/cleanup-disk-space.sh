#!/bin/bash
# Safe Disk Space Cleanup Script
# Removes non-critical files to free up disk space
# Safe to run - only removes regenerable artifacts

set -e

echo "🧹 Starting safe disk space cleanup..."
echo ""

# Track space freed
SPACE_FREED=0

# 1. Remove dangling Docker images (safe - can be rebuilt)
echo "1. Cleaning dangling Docker images..."
DANGLING_IMAGES=$(docker images --filter "dangling=true" -q)
if [ -n "$DANGLING_IMAGES" ]; then
    BEFORE=$(docker system df --format "{{.Size}}" | head -1)
    docker rmi $DANGLING_IMAGES 2>/dev/null || echo "  Some images may be in use (skipping)"
    AFTER=$(docker system df --format "{{.Size}}" | head -1)
    echo "  ✅ Cleaned dangling images"
else
    echo "  ℹ️  No dangling images found"
fi

# 2. Clean Docker build cache (safe - can be rebuilt)
echo "2. Cleaning Docker build cache..."
BEFORE_CACHE=$(docker system df | grep "Build Cache" | awk '{print $4}')
docker builder prune -f --filter "until=24h" 2>/dev/null || true
AFTER_CACHE=$(docker system df | grep "Build Cache" | awk '{print $4}')
echo "  ✅ Cleaned build cache (older than 24h)"

# 3. Remove old log files (keep last 7 days)
echo "3. Cleaning old log files..."
if [ -d "/home/founders/demoversion/symphainy_source/logs" ]; then
    LOG_SIZE_BEFORE=$(du -sh /home/founders/demoversion/symphainy_source/logs 2>/dev/null | cut -f1)
    find /home/founders/demoversion/symphainy_source/logs -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    LOG_SIZE_AFTER=$(du -sh /home/founders/demoversion/symphainy_source/logs 2>/dev/null | cut -f1)
    echo "  ✅ Cleaned log files older than 7 days"
    echo "    Before: $LOG_SIZE_BEFORE, After: $LOG_SIZE_AFTER"
fi

# 4. Remove coverage reports (safe - can be regenerated)
echo "4. Cleaning coverage reports..."
if [ -d "/home/founders/demoversion/symphainy_source/htmlcov" ]; then
    COV_SIZE=$(du -sh /home/founders/demoversion/symphainy_source/htmlcov 2>/dev/null | cut -f1)
    rm -rf /home/founders/demoversion/symphainy_source/htmlcov
    echo "  ✅ Removed coverage reports ($COV_SIZE)"
fi

if [ -d "/home/founders/demoversion/symphainy_source/symphainy-platform/htmlcov" ]; then
    COV_SIZE=$(du -sh /home/founders/demoversion/symphainy_source/symphainy-platform/htmlcov 2>/dev/null | cut -f1)
    rm -rf /home/founders/demoversion/symphainy_source/symphainy-platform/htmlcov
    echo "  ✅ Removed platform coverage reports ($COV_SIZE)"
fi

# 5. Remove frontend .next build directory (safe - can be regenerated)
echo "5. Cleaning frontend build artifacts..."
if [ -d "/home/founders/demoversion/symphainy_source/symphainy-frontend/.next" ]; then
    NEXT_SIZE=$(du -sh /home/founders/demoversion/symphainy_source/symphainy-frontend/.next 2>/dev/null | cut -f1)
    rm -rf /home/founders/demoversion/symphainy_source/symphainy-frontend/.next
    echo "  ✅ Removed .next build directory ($NEXT_SIZE)"
fi

# 6. Remove Python cache (safe - can be regenerated)
echo "6. Cleaning Python cache..."
PYCACHE_COUNT=$(find /home/founders/demoversion/symphainy_source -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find /home/founders/demoversion/symphainy_source -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "  ✅ Removed $PYCACHE_COUNT __pycache__ directories"
fi

# 7. Remove pytest cache (safe - can be regenerated)
echo "7. Cleaning pytest cache..."
if [ -d "/home/founders/demoversion/symphainy_source/tests/.pytest_cache" ]; then
    rm -rf /home/founders/demoversion/symphainy_source/tests/.pytest_cache
    echo "  ✅ Removed pytest cache"
fi

# 8. Remove old Docker images (keep only last 3 versions)
echo "8. Cleaning old Docker images (keeping last 3 versions)..."
# Get all images, sort by date, keep last 3, remove rest
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedAt}}" | \
    grep -E "symphainy_source|symphainy-platform" | \
    sort -k3 -r | \
    tail -n +4 | \
    awk '{print $2}' | \
    xargs -r docker rmi 2>/dev/null || echo "  ℹ️  No old images to remove"

# Summary
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Current disk usage:"
df -h / | tail -1
echo ""
echo "Docker system usage:"
docker system df
echo ""
echo "⚠️  Note: These files can be regenerated:"
echo "  - Coverage reports: Run 'pytest --cov --cov-report=html'"
echo "  - Frontend build: Run 'npm run build'"
echo "  - Docker images: Will rebuild on next deployment"






