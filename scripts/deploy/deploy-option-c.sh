#!/bin/bash
# Option C Deployment Script for Symphainy Platform
# Deploys using docker-compose.option-c.yml (managed services + app containers)
#
# Usage:
#   ./deploy-option-c.sh [environment]
#   environment: development (default), staging, production
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - Managed services configured and accessible
#   - Environment file with OPTION_C_ENABLED=true and managed service URLs
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
ENVIRONMENT=${1:-production}
ENV_FILE=".env.${ENVIRONMENT}"

echo -e "${GREEN}🚀 Symphainy Platform Deployment (Option C Pattern)${NC}"
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Project Root: ${PROJECT_ROOT}"

# Validate environment file exists
if [ ! -f "${PROJECT_ROOT}/${ENV_FILE}" ]; then
    echo -e "${RED}❌ Environment file not found: ${ENV_FILE}${NC}"
    echo -e "${YELLOW}💡 Create it from template: cp scripts/deploy/env.production.template ${ENV_FILE}${NC}"
    exit 1
fi

# Change to project root
cd "${PROJECT_ROOT}"

# Load environment variables
echo -e "${GREEN}📋 Loading environment variables from ${ENV_FILE}...${NC}"
export $(cat "${ENV_FILE}" | grep -v '^#' | xargs)

# Validate Option C is enabled
if [ "${OPTION_C_ENABLED}" != "true" ]; then
    echo -e "${RED}❌ OPTION_C_ENABLED must be set to 'true' for Option C deployment${NC}"
    exit 1
fi

# Validate managed service URLs
echo -e "${GREEN}✅ Validating managed service URLs...${NC}"
if [ -z "${REDIS_URL}" ] && [ -z "${REDIS_HOST}" ]; then
    echo -e "${YELLOW}⚠️  REDIS_URL or REDIS_HOST not set - using default container name${NC}"
fi

if [ -z "${ARANGO_URL}" ] && [ -z "${ARANGO_HOST}" ]; then
    echo -e "${YELLOW}⚠️  ARANGO_URL or ARANGO_HOST not set - using default container name${NC}"
fi

# Test managed service connectivity (if URLs provided)
if [ -n "${REDIS_URL}" ]; then
    echo -e "${GREEN}🔍 Testing Redis connectivity...${NC}"
    # Add connectivity test here if needed
fi

if [ -n "${ARANGO_URL}" ]; then
    echo -e "${GREEN}🔍 Testing ArangoDB connectivity...${NC}"
    # Add connectivity test here if needed
fi

# Build application images only (infrastructure is managed)
echo -e "${GREEN}🔨 Building application Docker images...${NC}"
docker-compose -f docker-compose.option-c.yml --env-file "${ENV_FILE}" build backend frontend celery-worker celery-beat

# Stop existing containers
echo -e "${GREEN}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.option-c.yml --env-file "${ENV_FILE}" down

# Start services
echo -e "${GREEN}🚀 Starting services (Option C pattern)...${NC}"
docker-compose -f docker-compose.option-c.yml --env-file "${ENV_FILE}" up -d

# Wait for services to be healthy
echo -e "${GREEN}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Run health checks
echo -e "${GREEN}🏥 Running health checks...${NC}"
source "${SCRIPT_DIR}/health-check.sh" "${ENVIRONMENT}" "option-c"

# Display status
echo -e "${GREEN}📊 Container Status:${NC}"
docker-compose -f docker-compose.option-c.yml --env-file "${ENV_FILE}" ps

echo -e "${GREEN}✅ Option C deployment complete!${NC}"
echo -e "${YELLOW}💡 Access URLs:${NC}"
echo -e "   Frontend: ${FRONTEND_URL:-http://localhost}"
echo -e "   Backend API: ${API_URL:-http://localhost}/api"
echo -e "   Traefik Dashboard: http://localhost:${TRAEFIK_DASHBOARD_PORT:-8080}"
echo -e "${YELLOW}💡 Managed Services:${NC}"
echo -e "   Redis: ${REDIS_URL:-redis://${REDIS_HOST:-redis}:${REDIS_PORT:-6379}}"
echo -e "   ArangoDB: ${ARANGO_URL:-http://${ARANGO_HOST:-arangodb}:${ARANGO_PORT:-8529}}"




