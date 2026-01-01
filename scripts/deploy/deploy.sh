#!/bin/bash
# Standard Deployment Script for Symphainy Platform
# Deploys using docker-compose.yml (all services in containers)
#
# Usage:
#   ./deploy.sh [environment]
#   environment: development (default), staging, production
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - Environment file (.env.development, .env.staging, or .env.production) in project root
#   - .env.secrets file in symphainy-platform/ directory

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Parse arguments
ENVIRONMENT=${1:-development}
ENV_FILE=".env.${ENVIRONMENT}"

echo -e "${GREEN}🚀 Symphainy Platform Deployment${NC}"
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Project Root: ${PROJECT_ROOT}"

# Validate environment file exists
if [ ! -f "${PROJECT_ROOT}/${ENV_FILE}" ]; then
    echo -e "${RED}❌ Environment file not found: ${ENV_FILE}${NC}"
    echo -e "${YELLOW}💡 Create it from template: cp scripts/deploy/env.${ENVIRONMENT}.template ${ENV_FILE}${NC}"
    exit 1
fi

# Validate secrets file exists
if [ ! -f "${PROJECT_ROOT}/symphainy-platform/.env.secrets" ]; then
    echo -e "${YELLOW}⚠️  Secrets file not found: symphainy-platform/.env.secrets${NC}"
    echo -e "${YELLOW}💡 Some services may fail without proper secrets${NC}"
fi

# Change to project root
cd "${PROJECT_ROOT}"

# Load environment variables
echo -e "${GREEN}📋 Loading environment variables from ${ENV_FILE}...${NC}"
export $(cat "${ENV_FILE}" | grep -v '^#' | xargs)

# Validate required variables
echo -e "${GREEN}✅ Validating required environment variables...${NC}"
source "${SCRIPT_DIR}/validate-env.sh" "${ENVIRONMENT}"

# Build images (if needed)
echo -e "${GREEN}🔨 Building Docker images...${NC}"
docker-compose --env-file "${ENV_FILE}" build --parallel

# Stop existing containers
echo -e "${GREEN}🛑 Stopping existing containers...${NC}"
docker-compose --env-file "${ENV_FILE}" down

# Start services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker-compose --env-file "${ENV_FILE}" up -d

# Wait for services to be healthy
echo -e "${GREEN}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Run health checks
echo -e "${GREEN}🏥 Running health checks...${NC}"
source "${SCRIPT_DIR}/health-check.sh" "${ENVIRONMENT}"

# Display status
echo -e "${GREEN}📊 Container Status:${NC}"
docker-compose --env-file "${ENV_FILE}" ps

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${YELLOW}💡 Access URLs:${NC}"
echo -e "   Frontend: ${FRONTEND_URL:-http://localhost}"
echo -e "   Backend API: ${API_URL:-http://localhost}/api"
echo -e "   Traefik Dashboard: http://localhost:${TRAEFIK_DASHBOARD_PORT:-8080}"



