#!/bin/bash
# SymphAIny Platform - Canonical Startup Script
# Combines best practices: Poetry, infrastructure orchestration, proper startup sequence
# 
# Usage:
#   ./startup.sh              # Start in foreground (development)
#   ./startup.sh --background  # Start in background (production)
#   ./startup.sh --minimal     # Skip infrastructure (assumes already running)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
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

log_header() {
    echo -e "${PURPLE}🎯 $1${NC}"
}

# Parse arguments
BACKGROUND=false
MINIMAL_MODE=false
for arg in "$@"; do
    case $arg in
        --background)
            BACKGROUND=true
            shift
            ;;
        --minimal)
            MINIMAL_MODE=true
            shift
            ;;
        *)
            ;;
    esac
done

# Configuration
PLATFORM_DIR="/home/founders/demoversion/symphainy_source/symphainy-platform"
cd "$PLATFORM_DIR"

PORT=${PORT:-8000}
HOST=${HOST:-"0.0.0.0"}
LOG_LEVEL=${LOG_LEVEL:-"info"}
RELOAD=${RELOAD:-"true"}

log_header "SymphAIny Platform Startup Orchestration"
echo "=============================================="
echo ""

# ============================================================================
# PHASE 0: VALIDATION
# ============================================================================

log_info "Phase 0: Validating environment..."

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "pyproject.toml" ]; then
    log_error "main.py or pyproject.toml not found. Are you in the correct directory?"
    exit 1
fi

# Ensure Poetry is in PATH
export PATH="/home/$USER/.local/bin:$PATH"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    log_error "Poetry not found. Please install Poetry first:"
    log_info "  curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi
log_success "Poetry found: $(poetry --version)"

# Check Python version
log_info "Checking Python version..."
python_version=$(python3 --version 2>&1)
log_success "Python version: $python_version"

# Check if Poetry environment is set up
log_info "Checking Poetry environment..."
if ! poetry env info &> /dev/null; then
    log_warning "Poetry environment not found. Installing dependencies..."
    poetry install
else
    log_success "Poetry environment ready"
fi

# Validate platform structure
log_info "Validating platform structure..."

required_dirs=(
    "foundations"
    "backend"
    "bases"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        log_success "Found $dir/"
    else
        log_error "Missing required directory: $dir/"
        exit 1
    fi
done

# ============================================================================
# PHASE 1: INFRASTRUCTURE (Docker)
# ============================================================================

INFRASTRUCTURE_AVAILABLE=false

if [ "$MINIMAL_MODE" = false ]; then
    log_header "Phase 1: Starting Infrastructure Services"
    echo "=============================================="
    
    if [ -f "docker-compose.infrastructure.yml" ]; then
        # Check for docker-compose or docker compose
        if command -v docker-compose &> /dev/null; then
            DOCKER_COMPOSE_CMD="docker-compose"
        elif docker compose version &> /dev/null; then
            DOCKER_COMPOSE_CMD="docker compose"
        else
            log_warning "Docker Compose not available - running in minimal mode"
            INFRASTRUCTURE_AVAILABLE=false
        fi
        
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            log_info "Starting Docker infrastructure services..."
            
            if $DOCKER_COMPOSE_CMD -f docker-compose.infrastructure.yml up -d; then
                log_success "Infrastructure started successfully"
                
                # Wait for infrastructure to be ready
                log_info "Waiting for infrastructure services to be healthy..."
                sleep 15
                
                # Check infrastructure health
                log_info "Checking infrastructure health..."
                if $DOCKER_COMPOSE_CMD -f docker-compose.infrastructure.yml ps | grep -q "Up"; then
                    log_success "Infrastructure services are healthy"
                    INFRASTRUCTURE_AVAILABLE=true
                else
                    log_warning "Some infrastructure services may not be fully ready"
                    INFRASTRUCTURE_AVAILABLE=false
                fi
            else
                log_error "Failed to start infrastructure"
                log_warning "Continuing with minimal mode..."
                INFRASTRUCTURE_AVAILABLE=false
            fi
        fi
    else
        log_warning "No docker-compose.infrastructure.yml found - running in minimal mode"
        INFRASTRUCTURE_AVAILABLE=false
    fi
else
    log_info "Minimal mode: Assuming infrastructure is already running"
    INFRASTRUCTURE_AVAILABLE=true  # Assume it's available
fi

# ============================================================================
# PHASE 2: FASTAPI BACKEND (START LAST!)
# ============================================================================

log_header "Phase 2: Starting FastAPI Backend (LAST in sequence)"
echo "========================================================"

# Set environment variables
export PLATFORM_MODE=$([ "$INFRASTRUCTURE_AVAILABLE" = true ] && echo "full" || echo "minimal")
export INFRASTRUCTURE_AVAILABLE=$INFRASTRUCTURE_AVAILABLE
export PYTHONPATH="$PLATFORM_DIR:$PYTHONPATH"

log_info "Platform configuration:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Log Level: $LOG_LEVEL"
echo "  Auto-reload: $RELOAD"
echo "  Infrastructure: $([ "$INFRASTRUCTURE_AVAILABLE" = true ] && echo "Full" || echo "Minimal")"
echo "  Mode: $([ "$BACKGROUND" = true ] && echo "Background" || echo "Foreground")"
echo ""

# Find available port if needed
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port $PORT is in use"
    # Try to find another port
    for port in $(seq 8001 8010); do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            PORT=$port
            log_info "Using port $PORT instead"
            break
        fi
    done
fi

# Start FastAPI backend using Poetry (CRITICAL: Start LAST!)
log_info "Starting FastAPI backend on port $PORT using Poetry..."

if [ "$BACKGROUND" = true ]; then
    # Background mode
    log_info "Starting in background mode..."
    poetry run python main.py --host "$HOST" --port "$PORT" --log-level "$LOG_LEVEL" > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    
    log_success "FastAPI backend process started (PID: $BACKEND_PID)"
    
    # Wait for port binding (CRITICAL - FastAPI takes time to bind)
    log_info "Waiting for FastAPI to bind to port $PORT..."
    max_wait=30
    wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_success "FastAPI backend bound to port $PORT"
            break
        fi
        sleep 2
        wait_time=$((wait_time + 2))
        if [ $((wait_time % 6)) -eq 0 ]; then
            log_info "Still waiting for port binding... ($wait_time/$max_wait seconds)"
        fi
    done
    
    if [ $wait_time -ge $max_wait ]; then
        log_error "FastAPI failed to bind to port $PORT within $max_wait seconds"
        log_error "Check logs: tail -50 /tmp/backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # Additional health check
    sleep 3
    if curl -s http://localhost:$PORT/api/auth/health > /dev/null 2>&1; then
        log_success "FastAPI backend health check passed"
    else
        log_warning "FastAPI backend health check failed, but port is bound"
        log_info "Backend may still be initializing. Check logs: tail -50 /tmp/backend.log"
    fi
    
    # Save PID for cleanup
    echo $BACKEND_PID > /tmp/backend.pid
    echo $PORT > /tmp/backend.port
    
    # Summary
    echo ""
    log_success "Backend startup complete!"
    echo ""
    echo "📊 Service Status:"
    echo "  - Backend: Running (PID: $BACKEND_PID) on port $PORT"
    echo "  - Logs: /tmp/backend.log"
    echo ""
    echo "🌐 Backend URL: http://localhost:$PORT"
    echo "📚 API Docs: http://localhost:$PORT/docs"
    echo "🔍 Health Check: http://localhost:$PORT/api/auth/health"
    echo ""
    echo "💡 To stop: kill $BACKEND_PID"
    echo "💡 To view logs: tail -f /tmp/backend.log"
    echo ""
    
else
    # Foreground mode (development)
    log_info "Starting in foreground mode (development)..."
    log_info "Press Ctrl+C to stop"
    echo ""
    
    if [ "$RELOAD" = "true" ]; then
        poetry run python main.py --host "$HOST" --port "$PORT" --reload --log-level "$LOG_LEVEL"
    else
        poetry run python main.py --host "$HOST" --port "$PORT" --log-level "$LOG_LEVEL"
    fi
fi

