#!/bin/bash
# Safe script to test container fixes
# All commands have timeouts to prevent hanging

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/../../symphainy-platform/docker-compose.infrastructure.yml"
SAFE_INSPECT="${SCRIPT_DIR}/safe_docker_inspect.py"

echo "============================================================"
echo "🧪 Testing Container Fixes"
echo "============================================================"
echo ""

# Function to run command with timeout
run_with_timeout() {
    timeout 10 "$@" 2>&1 || {
        echo "⚠️  Command timed out or failed: $*"
        return 1
    }
}

# Step 1: Check current container status
echo "📊 Step 1: Current Container Status"
echo "-----------------------------------"
run_with_timeout docker ps --format "table {{.Names}}\t{{.Status}}" \
    --filter name=symphainy-tempo \
    --filter name=symphainy-opa \
    --filter name=symphainy-celery-worker \
    --filter name=symphainy-celery-beat || true
echo ""

# Step 2: Restart containers one at a time (safely)
echo "🔄 Step 2: Restarting Containers (with timeouts)"
echo "-----------------------------------"

containers=("symphainy-tempo" "symphainy-opa" "symphainy-celery-worker" "symphainy-celery-beat")

for container in "${containers[@]}"; do
    echo "  🔄 Restarting $container..."
    if run_with_timeout docker restart "$container" > /dev/null 2>&1; then
        echo "    ✅ $container restarted"
        sleep 2  # Give container time to start
    else
        echo "    ⚠️  Failed to restart $container (may not be running)"
    fi
done
echo ""

# Step 3: Wait for containers to stabilize
echo "⏳ Step 3: Waiting for containers to stabilize (10 seconds)"
echo "-----------------------------------"
sleep 10
echo ""

# Step 4: Check health status using safe inspection script
echo "🏥 Step 4: Checking Health Status"
echo "-----------------------------------"

for container in "${containers[@]}"; do
    echo "  📦 Checking $container..."
    if [ -f "$SAFE_INSPECT" ]; then
        run_with_timeout python3 "$SAFE_INSPECT" "$container" --health --no-logs 2>&1 | \
            grep -E "(status|health|failing_streak)" | head -5 || true
    else
        echo "    ⚠️  Safe inspection script not found, using docker inspect..."
        run_with_timeout docker inspect "$container" --format='{{.State.Status}}/{{.State.Health.Status}}' 2>&1 || true
    fi
    echo ""
done

# Step 5: Check for restart loops
echo "🔄 Step 5: Checking for Restart Loops"
echo "-----------------------------------"
run_with_timeout docker ps --format "table {{.Names}}\t{{.Status}}\t{{.RestartCount}}" \
    --filter name=symphainy-tempo \
    --filter name=symphainy-opa \
    --filter name=symphainy-celery-worker \
    --filter name=symphainy-celery-beat || true
echo ""

# Step 6: Summary
echo "============================================================"
echo "📋 Summary"
echo "============================================================"
echo "✅ Container restart test completed"
echo "📝 Check the output above for health status"
echo "⚠️  If containers show 'unhealthy' or high restart counts, investigate further"
echo ""

