#!/bin/bash
# Emergency Recovery Script - Restores SSH access and cleans up issues

set -e

echo "🚨 Emergency Recovery - Restoring SSH Access"
echo "============================================="

# 1. Unset problematic environment variables
echo "1. Unsetting problematic environment variables..."
unset GOOGLE_APPLICATION_CREDENTIALS
unset GCLOUD_PROJECT
unset GOOGLE_CLOUD_PROJECT
unset GCLOUD_CONFIG
unset CLOUDSDK_CONFIG

# 2. Stop problematic containers (if they're in restart loops)
echo "2. Checking for problematic containers..."
CONTAINERS=$(timeout 5 docker ps -q --filter name=symphainy- 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "   Found containers. Checking restart counts..."
    for container in $CONTAINERS; do
        RESTART_COUNT=$(timeout 5 docker inspect --format '{{.RestartCount}}' "$container" 2>/dev/null || echo "0")
        if [ "$RESTART_COUNT" -gt 10 ]; then
            CONTAINER_NAME=$(timeout 5 docker inspect --format '{{.Name}}' "$container" 2>/dev/null | sed 's/\///' || echo "unknown")
            echo "   Stopping $CONTAINER_NAME (restart_count=$RESTART_COUNT)..."
            timeout 10 docker stop "$container" || true
        fi
    done
fi

# 3. Kill hanging test processes
echo "3. Checking for hanging test processes..."
pkill -9 -f "pytest.*test_file_parser" || true
pkill -9 -f "pytest.*layer_8" || true

# 4. Check VM resources
echo "4. Checking VM resources..."
df -h | head -2
free -h | head -2
echo "   CPU usage:"
timeout 2 top -bn1 | grep "Cpu(s)" | head -1 || echo "   (unable to check)"

# 5. Summary
echo ""
echo "✅ Recovery procedures completed"
echo "Try SSH access again"
echo ""
echo "If SSH still doesn't work:"
echo "  1. Check GCP console for VM status"
echo "  2. Try resetting VM from GCP console"
echo "  3. Check firewall rules"

