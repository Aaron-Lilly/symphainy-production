#!/bin/bash
# Test Environment Startup Script
# Similar to production-startup.sh but tailored for testing
# Handles Celery separately without modifying main.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="${SCRIPT_DIR}/../../symphainy-platform"
COMPOSE_FILE="${PLATFORM_DIR}/docker-compose.infrastructure.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🧪 SymphAIny Platform - Test Environment Startup"
echo "=================================================="
echo ""

# Check if we're in the right location
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "docker-compose.infrastructure.yml not found at $COMPOSE_FILE"
    exit 1
fi

# ============================================================================
# PHASE 1: START INFRASTRUCTURE CONTAINERS
# ============================================================================

print_status "Phase 1: Starting infrastructure containers..."

cd "$PLATFORM_DIR"

# Start infrastructure containers
if timeout 60 docker-compose -f docker-compose.infrastructure.yml up -d 2>&1 | grep -E "(Starting|Started|healthy|unhealthy)" | head -20; then
    print_success "Infrastructure containers started"
else
    print_warning "Some containers may have issues - check status manually"
fi

# Wait for critical containers to be healthy
print_status "Waiting for critical containers to stabilize..."
sleep 10

# Check container health
print_status "Checking container health..."
timeout 10 docker ps --format "{{.Names}}: {{.Status}}" \
    --filter name=symphainy-consul \
    --filter name=symphainy-arangodb \
    --filter name=symphainy-redis \
    --filter name=symphainy-tempo \
    --filter name=symphainy-opa 2>&1 | head -10

echo ""

# ============================================================================
# PHASE 2: START CELERY WORKER (IF NEEDED)
# ============================================================================

print_status "Phase 2: Checking Celery configuration..."

# Check if Celery containers are configured
if docker ps --format "{{.Names}}" | grep -q "symphainy-celery"; then
    print_status "Celery containers found in docker-compose"
    print_status "Celery will be managed by Docker Compose"
    print_warning "Note: Celery containers may need Celery app instance in code"
    print_warning "For now, they may restart until Celery app is configured"
else
    print_status "No Celery containers found - skipping Celery startup"
fi

echo ""

# ============================================================================
# PHASE 3: VERIFY INFRASTRUCTURE
# ============================================================================

print_status "Phase 3: Verifying infrastructure availability..."

# Check Consul
if timeout 5 curl -s http://localhost:8500/v1/status/leader > /dev/null 2>&1; then
    print_success "Consul is available"
else
    print_warning "Consul may not be ready yet"
fi

# Check ArangoDB
if timeout 5 curl -s http://localhost:8529/_api/version > /dev/null 2>&1; then
    print_success "ArangoDB is available"
else
    print_warning "ArangoDB may not be ready yet"
fi

# Check Redis
if timeout 5 redis-cli -h localhost ping > /dev/null 2>&1; then
    print_success "Redis is available"
else
    print_warning "Redis may not be ready yet"
fi

# Check Tempo
if timeout 5 curl -s http://localhost:3200/status > /dev/null 2>&1; then
    print_success "Tempo is available"
else
    print_warning "Tempo may not be ready yet"
fi

# Check OPA
if timeout 5 curl -s http://localhost:8181/health > /dev/null 2>&1; then
    print_success "OPA is available"
else
    print_warning "OPA may not be ready yet"
fi

echo ""

# ============================================================================
# FINAL STATUS REPORT
# ============================================================================

print_success "Test environment startup complete!"
echo ""
echo "📊 Infrastructure Status:"
echo "  - Docker Compose: Started ✅"
echo "  - Consul: Checked ✅"
echo "  - ArangoDB: Checked ✅"
echo "  - Redis: Checked ✅"
echo "  - Tempo: Checked ✅"
echo "  - OPA: Checked ✅"
echo ""
echo "🧪 Ready for testing!"
echo ""
echo "💡 To start backend server for tests that need it:"
echo "   cd $PLATFORM_DIR"
echo "   python3 main.py --port 8000 &"
echo ""
echo "💡 To check container status:"
echo "   docker ps --filter name=symphainy"
echo ""
echo "💡 To view container logs:"
echo "   docker logs symphainy-<container-name>"
echo ""

