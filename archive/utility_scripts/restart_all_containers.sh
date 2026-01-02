#!/bin/bash
# Restart All Containers Script
# 
# This script restarts all Symphainy platform containers:
# 1. Infrastructure services (ArangoDB, Redis, Consul, etc.)
# 2. Application services (Backend, Frontend, Celery)
# 3. Monitoring services (Traefik, Grafana, etc.)
#
# Usage:
#   ./restart_all_containers.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Restarting All Symphainy Containers${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
    exit 1
fi

# Step 1: Stop all containers
echo -e "${YELLOW}Step 1: Stopping all containers...${NC}"

# Stop infrastructure containers
if [ -f "symphainy-platform/docker-compose.infrastructure.yml" ]; then
    echo -e "${YELLOW}  Stopping infrastructure services...${NC}"
    docker-compose -f symphainy-platform/docker-compose.infrastructure.yml down 2>/dev/null || true
fi

# Stop production containers
if [ -f "docker-compose.prod.yml" ]; then
    echo -e "${YELLOW}  Stopping production services...${NC}"
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
fi

# Stop any remaining containers
echo -e "${YELLOW}  Stopping any remaining containers...${NC}"
docker-compose down 2>/dev/null || true

echo -e "${GREEN}✅ All containers stopped${NC}"
echo ""

# Step 2: Start infrastructure first
echo -e "${YELLOW}Step 2: Starting infrastructure services...${NC}"

if [ -f "symphainy-platform/docker-compose.infrastructure.yml" ]; then
    echo -e "${YELLOW}  Starting infrastructure stack...${NC}"
    docker-compose -f symphainy-platform/docker-compose.infrastructure.yml up -d
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to start infrastructure services${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Infrastructure services started${NC}"
else
    echo -e "${YELLOW}⚠️  Infrastructure compose file not found, skipping...${NC}"
fi

# Wait a bit for infrastructure to initialize
echo -e "${YELLOW}  Waiting 10 seconds for infrastructure to initialize...${NC}"
sleep 10

# Step 3: Start application services
echo ""
echo -e "${YELLOW}Step 3: Starting application services...${NC}"

if [ -f "docker-compose.prod.yml" ]; then
    echo -e "${YELLOW}  Starting backend and frontend...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to start application services${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Application services started${NC}"
else
    echo -e "${YELLOW}⚠️  Production compose file not found, trying default...${NC}"
    docker-compose up -d
fi

# Step 4: Wait for services to be healthy
echo ""
echo -e "${YELLOW}Step 4: Waiting for services to be healthy...${NC}"

# Wait for backend
BACKEND_URL="http://localhost:8000"
BACKEND_READY=false
ELAPSED=0
MAX_WAIT=120

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -f -s "${BACKEND_URL}/api/health" > /dev/null 2>&1; then
        BACKEND_READY=true
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo -e "${YELLOW}  Waiting for backend... (${ELAPSED}s / ${MAX_WAIT}s)${NC}"
done

if [ "$BACKEND_READY" = true ]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend not ready yet (may still be starting)${NC}"
fi

# Wait for frontend
FRONTEND_URL="http://localhost:3000"
if curl -f -s "${FRONTEND_URL}" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend not accessible yet (may still be starting)${NC}"
fi

# Check infrastructure services
echo -e "${YELLOW}  Checking infrastructure services...${NC}"

if curl -f -s "http://localhost:8500/v1/status/leader" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Consul is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Consul not accessible${NC}"
fi

if docker exec symphainy-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not accessible${NC}"
fi

if curl -f -s "http://localhost:8529/_api/version" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ArangoDB is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  ArangoDB not accessible${NC}"
fi

# Step 5: Show container status
echo ""
echo -e "${BLUE}Step 5: Container Status${NC}"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "symphainy|NAME" || docker ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All containers restarted${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Frontend: http://localhost:3000"
echo -e "  Backend:  http://localhost:8000"
echo -e "  Traefik:  http://localhost:8080"
echo ""






