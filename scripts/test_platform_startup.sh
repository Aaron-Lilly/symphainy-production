#!/bin/bash
# Platform Startup Test Script
# Tests Traefik health check fix and overall platform health

set -e

echo "=========================================="
echo "Platform Startup Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to wait for service health
wait_for_health() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    echo -n "Waiting for $service_name to be healthy..."
    while [ $attempt -le $max_attempts ]; do
        health=$(docker inspect --format='{{.State.Health.Status}}' "$service_name" 2>/dev/null || echo "none")
        if [ "$health" == "healthy" ]; then
            echo -e " ${GREEN}healthy${NC}"
            return 0
        elif [ "$health" == "unhealthy" ]; then
            echo -e " ${RED}unhealthy${NC}"
            return 1
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e " ${YELLOW}timeout${NC}"
    return 1
}

# Change to project directory
cd /home/founders/demoversion/symphainy_source

echo "Step 1: Starting Infrastructure Services"
echo "----------------------------------------"
docker-compose up -d consul redis arangodb meilisearch traefik 2>&1 | grep -E "(Creating|Starting|Started|Error)" || true
echo ""

echo "Step 2: Waiting for Infrastructure Services"
echo "----------------------------------------"
sleep 5

# Check Traefik health
echo "Checking Traefik health..."
if wait_for_health "symphainy-traefik"; then
    print_status 0 "Traefik is healthy"
else
    print_status 1 "Traefik health check failed"
    echo ""
    echo "Traefik logs (last 20 lines):"
    docker logs --tail 20 symphainy-traefik 2>&1 | tail -20
    echo ""
    echo "Testing Traefik ping endpoint manually:"
    docker exec symphainy-traefik wget --spider --tries=1 --no-verbose --timeout=5 http://127.0.0.1:8080/ping 2>&1 || echo "Ping test failed"
fi
echo ""

echo "Step 3: Starting Application Services"
echo "----------------------------------------"
docker-compose up -d backend frontend 2>&1 | grep -E "(Creating|Starting|Started|Error)" || true
echo ""

echo "Step 4: Waiting for Application Services"
echo "----------------------------------------"
sleep 10

# Check Backend health
echo "Checking Backend health..."
if wait_for_health "symphainy-backend-prod"; then
    print_status 0 "Backend is healthy"
else
    print_status 1 "Backend health check failed"
    echo ""
    echo "Backend logs (last 20 lines):"
    docker logs --tail 20 symphainy-backend-prod 2>&1 | tail -20
fi
echo ""

# Check Frontend health
echo "Checking Frontend health..."
if wait_for_health "symphainy-frontend-prod"; then
    print_status 0 "Frontend is healthy"
else
    print_status 1 "Frontend health check failed"
    echo ""
    echo "Frontend logs (last 20 lines):"
    docker logs --tail 20 symphainy-frontend-prod 2>&1 | tail -20
fi
echo ""

echo "Step 5: Service Status Summary"
echo "----------------------------------------"
echo ""
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "traefik|backend|frontend|consul|redis|arangodb|meilisearch|NAMES" || docker ps | grep -E "traefik|backend|frontend"
echo ""

echo "Health Check Status:"
for container in symphainy-traefik symphainy-backend-prod symphainy-frontend-prod; do
    if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-health-check")
        if [ "$health" == "healthy" ]; then
            echo -e "${GREEN}✓${NC} $container: $health"
        elif [ "$health" == "unhealthy" ]; then
            echo -e "${RED}✗${NC} $container: $health"
        else
            echo -e "${YELLOW}○${NC} $container: $health"
        fi
    fi
done
echo ""

echo "Step 6: Endpoint Verification"
echo "----------------------------------------"
echo ""

# Test Traefik ping endpoint
echo "Testing Traefik ping endpoint..."
if docker exec symphainy-traefik wget --spider --tries=1 --no-verbose --timeout=5 http://127.0.0.1:8080/ping 2>&1 > /dev/null; then
    print_status 0 "Traefik /ping endpoint is accessible"
else
    print_status 1 "Traefik /ping endpoint is not accessible"
    echo "Attempting alternative: API endpoint..."
    if docker exec symphainy-traefik wget --spider --tries=1 --no-verbose --timeout=5 http://127.0.0.1:8080/api/rawdata 2>&1 > /dev/null; then
        print_status 0 "Traefik API endpoint is accessible (alternative)"
    else
        print_status 1 "Traefik API endpoint is also not accessible"
    fi
fi
echo ""

# Test Backend health endpoint
echo "Testing Backend health endpoint..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status 0 "Backend /health endpoint is accessible"
    backend_health=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo "unknown")
    echo "  Backend status: $backend_health"
else
    print_status 1 "Backend /health endpoint is not accessible"
fi
echo ""

# Test Frontend
echo "Testing Frontend..."
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    print_status 0 "Frontend is accessible"
else
    print_status 1 "Frontend is not accessible"
fi
echo ""

# Test Traefik routing
echo "Testing Traefik routing..."
if curl -s -f http://localhost/api/health > /dev/null 2>&1 || curl -s -f http://localhost/health > /dev/null 2>&1; then
    print_status 0 "Traefik is routing requests correctly"
else
    print_status 1 "Traefik routing may have issues"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

# Count healthy services
healthy_count=0
total_count=0

for container in symphainy-traefik symphainy-backend-prod symphainy-frontend-prod; do
    if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        total_count=$((total_count + 1))
        health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
        if [ "$health" == "healthy" ]; then
            healthy_count=$((healthy_count + 1))
        fi
    fi
done

echo "Services: $healthy_count/$total_count healthy"
echo ""

if [ $healthy_count -eq $total_count ] && [ $total_count -gt 0 ]; then
    echo -e "${GREEN}✓ All services are healthy!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some services are not healthy. Check logs above.${NC}"
    exit 1
fi


