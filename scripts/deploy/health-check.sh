#!/bin/bash
# Health Check Script for Symphainy Platform
#
# Usage:
#   source health-check.sh [environment] [compose-file-suffix]
#
# Checks health of all services after deployment

ENVIRONMENT=${1:-development}
COMPOSE_SUFFIX=${2:-""}  # "option-c" for docker-compose.option-c.yml

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "${PROJECT_ROOT}"

ENV_FILE=".env.${ENVIRONMENT}"
COMPOSE_FILE="docker-compose.yml"
if [ "${COMPOSE_SUFFIX}" = "option-c" ]; then
    COMPOSE_FILE="docker-compose.option-c.yml"
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🏥 Running health checks...${NC}"

# Check backend health
echo -n "Checking backend health... "
BACKEND_HEALTH=$(docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T backend curl -s http://localhost:8000/health 2>/dev/null || echo "FAILED")
if echo "${BACKEND_HEALTH}" | grep -q "healthy\|ok\|status"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "   Backend health check failed"
fi

# Check frontend health
echo -n "Checking frontend health... "
FRONTEND_HEALTH=$(docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T frontend wget -q -O - http://localhost:3000 2>/dev/null || echo "FAILED")
if [ "${FRONTEND_HEALTH}" != "FAILED" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "   Frontend health check failed"
fi

# Check Traefik
echo -n "Checking Traefik... "
TRAEFIK_HEALTH=$(docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T traefik wget -q -O - http://localhost:8080/ping 2>/dev/null || echo "FAILED")
if [ "${TRAEFIK_HEALTH}" != "FAILED" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "   Traefik health check failed"
fi

# Check Consul
echo -n "Checking Consul... "
CONSUL_HEALTH=$(docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T consul curl -s http://localhost:8500/v1/status/leader 2>/dev/null || echo "FAILED")
if [ "${CONSUL_HEALTH}" != "FAILED" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "   Consul health check failed"
fi

# Check Redis (if not Option C)
if [ "${COMPOSE_SUFFIX}" != "option-c" ]; then
    echo -n "Checking Redis... "
    REDIS_HEALTH=$(docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T redis redis-cli ping 2>/dev/null || echo "FAILED")
    if [ "${REDIS_HEALTH}" = "PONG" ]; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        echo "   Redis health check failed"
    fi
fi

# Check ArangoDB (if not Option C)
if [ "${COMPOSE_SUFFIX}" != "option-c" ]; then
    echo -n "Checking ArangoDB... "
    ARANGO_HEALTH=$(docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T arangodb wget -q -O - http://localhost:8529/_api/version 2>/dev/null || echo "FAILED")
    if [ "${ARANGO_HEALTH}" != "FAILED" ]; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        echo "   ArangoDB health check failed"
    fi
fi

echo -e "${GREEN}✅ Health checks complete${NC}"




