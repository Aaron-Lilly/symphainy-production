#!/bin/bash
# Frontend and Traefik Status Check Script
# Updated: Test edit to verify permissions

echo "=========================================="
echo "Frontend & Traefik Status Check"
echo "=========================================="
echo ""

# 1. Check if Traefik is running
echo "1. Checking Traefik container status..."
echo "----------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "traefik|NAMES" || echo "No Traefik container found in running containers"
echo ""

# 2. Check if Frontend is running
echo "2. Checking Frontend container status..."
echo "----------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "frontend|NAMES" || echo "No Frontend container found in running containers"
echo ""

# 3. Check all containers (including stopped)
echo "3. Checking all containers (including stopped)..."
echo "----------------------------------------"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "traefik|frontend|NAMES" || echo "No Traefik or Frontend containers found"
echo ""

# 4. Check Traefik logs (last 30 lines)
echo "4. Traefik logs (last 30 lines)..."
echo "----------------------------------------"
docker logs --tail 30 symphainy-traefik 2>&1 || echo "Could not retrieve Traefik logs (container may not exist)"
echo ""

# 5. Check Frontend logs (last 30 lines)
echo "5. Frontend logs (last 30 lines)..."
echo "----------------------------------------"
docker logs --tail 30 symphainy-frontend-prod 2>&1 || echo "Could not retrieve Frontend logs (container may not exist)"
echo ""

# 6. Check docker-compose status
echo "6. Docker Compose service status..."
echo "----------------------------------------"
cd /home/founders/demoversion/symphainy_source
docker-compose -f docker-compose.prod.yml ps 2>&1 || docker-compose ps 2>&1 || echo "Could not check docker-compose status"
echo ""

# 7. Check network
echo "7. Checking Docker network..."
echo "----------------------------------------"
docker network ls | grep smart_city_net || echo "smart_city_net network not found"
echo ""

# 8. Test port 80
echo "8. Testing port 80 accessibility..."
echo "----------------------------------------"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:80 2>&1 || echo "Port 80 not accessible"
echo ""

# 9. Test port 3000 (should fail if not exposed)
echo "9. Testing port 3000 (should fail if not exposed)..."
echo "----------------------------------------"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000 2>&1 || echo "Port 3000 not accessible (expected if not exposed)"
echo ""

echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Expected Configuration:"
echo "- Frontend accessible via: http://35.215.64.103 (port 80, via Traefik)"
echo "- Frontend NOT accessible via: http://35.215.64.103:3000 (port not exposed)"
echo "- Traefik should be running on port 80"
echo ""
echo "If containers are not running, start them with:"
echo "  cd /home/founders/demoversion/symphainy_source"
echo "  docker-compose -f docker-compose.prod.yml up -d"
echo ""




