#!/bin/bash
# Pre-Test Validation Script
# Runs before tests to ensure environment is safe

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔍 Pre-Test Validation"
echo "===================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Check critical environment variables
echo -e "\n${YELLOW}Checking critical environment variables...${NC}"
CRITICAL_VARS=(
    "GOOGLE_APPLICATION_CREDENTIALS"
    "GCLOUD_PROJECT"
    "GOOGLE_CLOUD_PROJECT"
)

for var in "${CRITICAL_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo -e "${GREEN}✓${NC} $var is set: ${!var}"
        # Verify file exists if it's a path
        if [[ "${!var}" == *.json ]] && [ ! -f "${!var}" ]; then
            echo -e "${RED}✗${NC} $var points to non-existent file: ${!var}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${YELLOW}⚠${NC} $var is not set (may use Application Default Credentials)"
    fi
done

# Check Docker containers
echo -e "\n${YELLOW}Checking Docker containers...${NC}"
CONTAINERS=(
    "symphainy-redis"
    "symphainy-arangodb"
    "symphainy-consul"
    "symphainy-celery-worker"
    "symphainy-celery-beat"
)

for container in "${CONTAINERS[@]}"; do
    if timeout 5 docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}$"; then
        STATUS=$(timeout 5 docker inspect --format '{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
        RESTART_COUNT=$(timeout 5 docker inspect --format '{{.RestartCount}}' "$container" 2>/dev/null || echo "0")
        
        if [ "$STATUS" = "running" ]; then
            if [ "$RESTART_COUNT" -gt 10 ]; then
                echo -e "${RED}✗${NC} $container: running but restart_count=$RESTART_COUNT (possible restart loop)"
                ERRORS=$((ERRORS + 1))
            else
                echo -e "${GREEN}✓${NC} $container: running (restarts: $RESTART_COUNT)"
            fi
        else
            echo -e "${RED}✗${NC} $container: status=$STATUS"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${RED}✗${NC} $container: not found"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check VM resources
echo -e "\n${YELLOW}Checking VM resources...${NC}"
CPU_PERCENT=$(timeout 2 top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}' || echo "0")
MEM_PERCENT=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
DISK_PERCENT=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if (( $(echo "$CPU_PERCENT > 85" | bc -l 2>/dev/null || echo "0") )); then
    echo -e "${RED}✗${NC} CPU usage: ${CPU_PERCENT}% (threshold: 85%)"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} CPU usage: ${CPU_PERCENT}%"
fi

if [ "$MEM_PERCENT" -gt 85 ]; then
    echo -e "${RED}✗${NC} Memory usage: ${MEM_PERCENT}% (threshold: 85%)"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} Memory usage: ${MEM_PERCENT}%"
fi

if [ "$DISK_PERCENT" -gt 90 ]; then
    echo -e "${RED}✗${NC} Disk usage: ${DISK_PERCENT}% (threshold: 90%)"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} Disk usage: ${DISK_PERCENT}%"
fi

# Summary
echo -e "\n${YELLOW}Validation Summary${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS issue(s)${NC}"
    echo -e "\nFix issues before running tests."
    exit 1
fi

