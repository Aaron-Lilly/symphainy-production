#!/bin/bash
# SymphAIny Platform - Proper Backend Startup Script
# Uses Poetry, follows proper startup sequence, handles Docker infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
PLATFORM_DIR="/home/founders/demoversion/symphainy_source/symphainy-platform"
cd "$PLATFORM_DIR"

log_info "SymphAIny Platform - Proper Backend Startup"
echo "=============================================="
echo ""

# Check Poetry
if ! command -v poetry &> /dev/null; then
    log_error "Poetry not found. Please install Poetry first."
    exit 1
fi
log_success "Poetry found: $(poetry --version)"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    log_error "pyproject.toml not found. Are you in the correct directory?"
    exit 1
fi

# Check if Poetry environment is set up
if ! poetry env info &> /dev/null; then
    log_warning "Poetry environment not found. Installing dependencies..."
    poetry install
fi

# ============================================================================
# PHASE 1: INFRASTRUCTURE (Docker)
# ============================================================================

log_info "Phase 1: Starting Infrastructure Services..."

if [ -f "docker-compose.infrastructure.yml" ]; then
    if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
        log_info "Starting Docker infrastructure services..."
        
        # Use docker-compose or docker compose (depending on version)
        if command -v docker-compose &> /dev/null; then
            DOCKER_COMPOSE_CMD="docker-compose"
        else
            DOCKER_COMPOSE_CMD="docker compose"
        fi
        
        # Start infrastructure
        $DOCKER_COMPOSE_CMD -f docker-compose.infrastructure.yml up -d
        
        log_info "Waiting for infrastructure services to be healthy..."
        sleep 15
        
        # Check infrastructure health
        if $DOCKER_COMPOSE_CMD -f docker-compose.infrastructure.yml ps | grep -q "Up"; then
            log_success "Infrastructure services are running"
        else
            log_warning "Some infrastructure services may not be fully ready"
        fi
    else
        log_warning "Docker not available - assuming infrastructure is running externally"
    fi
else
    log_warning "No docker-compose.infrastructure.yml found - assuming infrastructure is running externally"
fi

# ============================================================================
# PHASE 2: FASTAPI BACKEND (START LAST!)
# ============================================================================

log_info "Phase 2: Starting FastAPI Backend (LAST in sequence)..."

# Set PYTHONPATH for Poetry environment
export PYTHONPATH="$PLATFORM_DIR:$PYTHONPATH"

# Find available port
BACKEND_PORT=${PORT:-8000}
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port $BACKEND_PORT is in use"
    # Try to find another port
    for port in $(seq 8001 8010); do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            BACKEND_PORT=$port
            log_info "Using port $BACKEND_PORT instead"
            break
        fi
    done
fi

# Start FastAPI backend using Poetry
log_info "Starting FastAPI backend on port $BACKEND_PORT using Poetry..."
poetry run python main.py --port $BACKEND_PORT > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

log_success "FastAPI backend process started (PID: $BACKEND_PID)"

# Wait for port binding (CRITICAL - FastAPI takes time to bind)
log_info "Waiting for FastAPI to bind to port $BACKEND_PORT..."
max_wait=30
wait_time=0

while [ $wait_time -lt $max_wait ]; do
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "FastAPI backend bound to port $BACKEND_PORT"
        break
    fi
    sleep 2
    wait_time=$((wait_time + 2))
    if [ $((wait_time % 6)) -eq 0 ]; then
        log_info "Still waiting for port binding... ($wait_time/$max_wait seconds)"
    fi
done

if [ $wait_time -ge $max_wait ]; then
    log_error "FastAPI failed to bind to port $BACKEND_PORT within $max_wait seconds"
    log_error "Check logs: tail -50 /tmp/backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Additional health check
sleep 3
if curl -s http://localhost:$BACKEND_PORT/api/auth/health > /dev/null 2>&1; then
    log_success "FastAPI backend health check passed"
else
    log_warning "FastAPI backend health check failed, but port is bound"
    log_info "Backend may still be initializing. Check logs: tail -50 /tmp/backend.log"
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
log_success "Backend startup complete!"
echo ""
echo "📊 Service Status:"
echo "  - Backend: Running (PID: $BACKEND_PID) on port $BACKEND_PORT"
echo "  - Logs: /tmp/backend.log"
echo ""
echo "🌐 Backend URL: http://localhost:$BACKEND_PORT"
echo "📚 API Docs: http://localhost:$BACKEND_PORT/docs"
echo "🔍 Health Check: http://localhost:$BACKEND_PORT/api/auth/health"
echo ""
echo "💡 To stop: kill $BACKEND_PID"
echo "💡 To view logs: tail -f /tmp/backend.log"
echo ""


