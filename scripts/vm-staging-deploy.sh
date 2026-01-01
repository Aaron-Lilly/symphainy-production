#!/bin/bash
# VM Staging Deployment Script
# This script is called by GitHub Actions to deploy to your GCP VM
# Location: /home/founders/demoversion/symphainy_source/scripts/vm-staging-deploy.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SymphAIny VM Staging Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
PROJECT_DIR="/home/founders/demoversion/symphainy_source"
COMPOSE_FILE="docker-compose.prod.yml"

# Navigate to project directory
echo -e "\n${YELLOW}📁 Navigating to project directory...${NC}"
cd $PROJECT_DIR || exit 1
pwd

# Pull latest code
echo -e "\n${YELLOW}📥 Pulling latest code from main branch...${NC}"
git fetch origin
git checkout main
git pull origin main

# Show current commit
echo -e "\n${YELLOW}📝 Current commit:${NC}"
git log -1 --oneline

# Step 1: Start Infrastructure Services (ArangoDB, Redis, Consul, Meilisearch, Celery, etc.)
echo -e "\n${YELLOW}🐳 Step 1: Starting infrastructure services...${NC}"
cd $PROJECT_DIR/symphainy-platform

if [ -f "docker-compose.infrastructure.yml" ]; then
    echo -e "${YELLOW}Starting: ArangoDB, Redis, Consul, Meilisearch, Celery Worker, Celery Beat, Tempo, OTel Collector, Grafana, OPA...${NC}"
    docker-compose -f docker-compose.infrastructure.yml up -d
    
    # Wait for infrastructure to be ready
    echo -e "${YELLOW}⏳ Waiting for infrastructure services to be healthy (20 seconds)...${NC}"
    sleep 20
    
    # Verify infrastructure
    echo -e "${YELLOW}📊 Infrastructure services status:${NC}"
    docker-compose -f docker-compose.infrastructure.yml ps
else
    echo -e "${RED}❌ docker-compose.infrastructure.yml not found!${NC}"
    exit 1
fi

# Step 2: Stop existing application containers
echo -e "\n${YELLOW}🛑 Step 2: Stopping existing application containers...${NC}"
cd $PROJECT_DIR
docker-compose -f $COMPOSE_FILE down || true

# Step 3: Remove dangling images to save space
echo -e "\n${YELLOW}🧹 Step 3: Cleaning up old Docker images...${NC}"
docker system prune -f

# Step 4: Build new application containers
echo -e "\n${YELLOW}🏗️  Step 4: Building new application containers...${NC}"
docker-compose -f $COMPOSE_FILE build --no-cache

# Step 5: Start application containers
echo -e "\n${YELLOW}▶️  Step 5: Starting application containers...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for containers to start
echo -e "\n${YELLOW}⏳ Waiting for containers to be healthy (30 seconds)...${NC}"
sleep 30

# Health checks
echo -e "\n${YELLOW}🏥 Running health checks...${NC}"

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo -e "${YELLOW}Backend logs:${NC}"
    docker-compose -f $COMPOSE_FILE logs backend | tail -20
fi

# Check frontend health
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is healthy${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
    echo -e "${YELLOW}Frontend logs:${NC}"
    docker-compose -f $COMPOSE_FILE logs frontend | tail -20
fi

# Show container status
echo -e "\n${YELLOW}📊 Container status:${NC}"
docker-compose -f $COMPOSE_FILE ps

# Show resource usage
echo -e "\n${YELLOW}💻 Resource usage:${NC}"
docker stats --no-stream

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Access staging environment:${NC}"
echo -e "  Backend:  http://localhost:8000"
echo -e "  Frontend: http://localhost:3000"
echo -e "\n${YELLOW}View logs:${NC}"
echo -e "  docker-compose -f $COMPOSE_FILE logs -f"
echo -e "\n${YELLOW}Stop staging:${NC}"
echo -e "  docker-compose -f $COMPOSE_FILE down"

exit 0




