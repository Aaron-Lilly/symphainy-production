#!/bin/bash
# SymphAIny Development Environment Orchestration
# Starts infrastructure → backend → frontend with proper health checks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🚀 SymphAIny Development Environment${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""

# Change to symphainy_source directory
cd "$(dirname "$0")/.." || exit 1

# ============================================================================
# STEP 1: Start Infrastructure Services
# ============================================================================
echo -e "${BLUE}📦 Step 1: Starting infrastructure services...${NC}"
cd symphainy-platform

docker-compose -f docker-compose.infrastructure.yml up -d arangodb redis consul

echo ""
echo -e "${YELLOW}⏳ Waiting for infrastructure to be healthy...${NC}"

# Wait for ArangoDB
for i in {1..30}; do
  if curl -sf http://localhost:8529/_api/version > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ ArangoDB is ready${NC}"
    break
  fi
  if [ $i -eq 30 ]; then
    echo -e "${RED}  ❌ ArangoDB failed to start${NC}"
    echo -e "${YELLOW}  Check logs: docker logs symphainy-arangodb${NC}"
    exit 1
  fi
  echo -e "  ⏳ ArangoDB starting... ($i/30)"
  sleep 2
done

# Wait for Redis
for i in {1..15}; do
  if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Redis is ready${NC}"
    break
  fi
  if [ $i -eq 15 ]; then
    echo -e "${RED}  ❌ Redis failed to start${NC}"
    echo -e "${YELLOW}  Check logs: docker logs symphainy-redis${NC}"
    exit 1
  fi
  echo -e "  ⏳ Redis starting... ($i/15)"
  sleep 1
done

# Wait for Consul
for i in {1..15}; do
  if curl -sf http://localhost:8501/v1/status/leader > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Consul is ready${NC}"
    break
  fi
  if [ $i -eq 15 ]; then
    echo -e "${RED}  ❌ Consul failed to start${NC}"
    echo -e "${YELLOW}  Check logs: docker logs symphainy-consul${NC}"
    exit 1
  fi
  echo -e "  ⏳ Consul starting... ($i/15)"
  sleep 1
done

echo -e "${GREEN}✅ All infrastructure services are healthy!${NC}"
echo ""

# ============================================================================
# STEP 2: Start Backend
# ============================================================================
echo -e "${BLUE}🔧 Step 2: Starting backend...${NC}"

# Kill any existing backend process
pkill -f "python3 main.py" 2>/dev/null || true
sleep 1

# Start backend in background
cd /home/founders/demoversion/symphainy_source/symphainy-platform
nohup python3 main.py > /tmp/symphainy_backend.log 2>&1 &
BACKEND_PID=$!
echo -e "  Backend PID: ${CYAN}$BACKEND_PID${NC}"

echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
for i in {1..60}; do
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Backend is ready!${NC}"
    BACKEND_READY=true
    break
  fi
  
  # Check if process is still running
  if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}  ❌ Backend process died during startup${NC}"
    echo -e "${YELLOW}  Last 30 lines of log:${NC}"
    tail -30 /tmp/symphainy_backend.log
    exit 1
  fi
  
  if [ $i -eq 60 ]; then
    echo -e "${RED}  ❌ Backend failed to start within 120 seconds${NC}"
    echo -e "${YELLOW}  Check logs: tail -f /tmp/symphainy_backend.log${NC}"
    exit 1
  fi
  
  echo -e "  ⏳ Backend starting... ($i/60)"
  sleep 2
done

echo ""

# ============================================================================
# STEP 3: Start Frontend
# ============================================================================
echo -e "${BLUE}🎨 Step 3: Starting frontend...${NC}"

# Kill any existing frontend process
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
sleep 1

# Check if node_modules exists
cd /home/founders/demoversion/symphainy_source/symphainy-frontend
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}  ⚠️  node_modules not found, running npm install...${NC}"
  npm install
fi

# Start frontend in background
nohup npm run dev > /tmp/symphainy_frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "  Frontend PID: ${CYAN}$FRONTEND_PID${NC}"

echo -e "${YELLOW}⏳ Waiting for frontend to be ready...${NC}"
for i in {1..60}; do
  if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Frontend is ready!${NC}"
    FRONTEND_READY=true
    break
  fi
  
  # Check if process is still running
  if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}  ❌ Frontend process died during startup${NC}"
    echo -e "${YELLOW}  Last 30 lines of log:${NC}"
    tail -30 /tmp/symphainy_frontend.log
    exit 1
  fi
  
  if [ $i -eq 60 ]; then
    echo -e "${RED}  ❌ Frontend failed to start within 120 seconds${NC}"
    echo -e "${YELLOW}  Check logs: tail -f /tmp/symphainy_frontend.log${NC}"
    exit 1
  fi
  
  echo -e "  ⏳ Frontend starting... ($i/60)"
  sleep 2
done

echo ""

# ============================================================================
# SUCCESS SUMMARY
# ============================================================================
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SymphAIny Platform is READY!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📊 Services:${NC}"
echo -e "  ${GREEN}✓${NC} Backend:  http://localhost:8000"
echo -e "  ${GREEN}✓${NC} Frontend: http://localhost:3000"
echo -e "  ${GREEN}✓${NC} ArangoDB: http://localhost:8529"
echo -e "  ${GREEN}✓${NC} Redis:    localhost:6379"
echo -e "  ${GREEN}✓${NC} Consul:   http://localhost:8501"
echo ""
echo -e "${CYAN}📋 Process IDs:${NC}"
echo -e "  Backend:  ${CYAN}$BACKEND_PID${NC}"
echo -e "  Frontend: ${CYAN}$FRONTEND_PID${NC}"
echo ""
echo -e "${CYAN}📝 View Logs:${NC}"
echo -e "  ${YELLOW}tail -f /tmp/symphainy_backend.log${NC}"
echo -e "  ${YELLOW}tail -f /tmp/symphainy_frontend.log${NC}"
echo ""
echo -e "${CYAN}🧪 Run E2E Tests:${NC}"
echo -e "  ${YELLOW}cd /home/founders/demoversion/symphainy_source${NC}"
echo -e "  ${YELLOW}pytest tests/e2e/test_complete_cto_demo_journey.py -v -s${NC}"
echo ""
echo -e "${CYAN}🛑 Stop Everything:${NC}"
echo -e "  ${YELLOW}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "  ${YELLOW}docker-compose -f symphainy-platform/docker-compose.infrastructure.yml down${NC}"
echo ""



