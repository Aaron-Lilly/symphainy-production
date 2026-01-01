#!/bin/bash
# Stop all SymphAIny development services

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🛑 Stopping SymphAIny Development Environment${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""

# Stop backend
echo -e "${YELLOW}Stopping backend...${NC}"
pkill -f "python3 main.py" && echo -e "${GREEN}  ✅ Backend stopped${NC}" || echo -e "${YELLOW}  ℹ️  No backend process found${NC}"

# Stop frontend
echo -e "${YELLOW}Stopping frontend...${NC}"
pkill -f "npm run dev" && echo -e "${GREEN}  ✅ Frontend stopped${NC}" || echo -e "${YELLOW}  ℹ️  No frontend process found${NC}"
pkill -f "next dev" 2>/dev/null

# Stop infrastructure
echo -e "${YELLOW}Stopping infrastructure services...${NC}"
cd /home/founders/demoversion/symphainy_source/symphainy-platform
docker-compose -f docker-compose.infrastructure.yml down && echo -e "${GREEN}  ✅ Infrastructure stopped${NC}"

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""



