#!/bin/bash

# SymphAIny Platform - Production Startup Script
# This script starts all required services with proper sequencing
# Now uses Manager Vision orchestration for platform coordination

set -e

echo "🚀 SymphAIny Platform - Starting All Services"
echo "=============================================="
echo "Using Manager Vision orchestration for platform coordination"
echo "This provides the missing orchestration layer for platform startup"
echo ""
echo "Usage:"
echo "  ./startup.sh                    # Standard startup"
echo "  ./startup.sh --manager-vision   # Manager Vision orchestration"
echo "  ./startup.sh -mv               # Manager Vision orchestration (short)"
echo ""

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

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "This script must be run from the symphainy-platform directory (pyproject.toml not found)"
    exit 1
fi

# Ensure Poetry is in PATH
export PATH="/home/$USER/.local/bin:$PATH"

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    print_error "Poetry is not installed or not in PATH"
    print_status "Please install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

print_success "Poetry found: $(poetry --version)"

# Check if dependencies are installed
print_status "Checking Poetry dependencies..."
if ! poetry check > /dev/null 2>&1; then
    print_warning "Poetry dependencies not installed. Installing..."
    poetry install
    print_success "Dependencies installed"
else
    print_success "Dependencies are up to date"
fi

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 20)) ]; then
            print_error "No available ports found between $start_port and $((start_port + 20))"
            exit 1
        fi
    done
    
    echo $port
}

# Function to kill any conflicting processes
kill_conflicting_processes() {
    local port=$1
    local pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
    
    if [ -n "$pids" ]; then
        print_warning "Port $port is in use by PIDs: $pids"
        print_status "Killing conflicting processes..."
        
        for pid in $pids; do
            if kill -0 $pid 2>/dev/null; then
                kill $pid
                print_status "Killed process $pid on port $port"
            fi
        done
        
        # Wait for processes to die
        sleep 2
        
        # Verify they're gone
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_error "Failed to free port $port"
            return 1
        else
            print_success "Port $port is now free"
            return 0
        fi
    fi
    
    return 0
}

# Check and clean up current port usage for ALL services
print_status "Checking current port usage for all services..."
kill_conflicting_processes 8000  # Main FastAPI backend
kill_conflicting_processes 8001  # MCP Server 1
kill_conflicting_processes 8002  # MCP Server 2
kill_conflicting_processes 6379  # Redis
kill_conflicting_processes 5555  # Celery Flower (optional)

# ============================================================================
# 🚨 CRITICAL: STARTUP SEQUENCE PATTERN
# ============================================================================
# 
# ALWAYS follow this sequence when adding new services:
# 1. Infrastructure services (Redis, databases, etc.)
# 2. Celery worker (background tasks, no ports)
# 3. MCP servers (agent tools, bind to ports)
# 4. FastAPI backend LAST (let it take its time to initialize)
#
# WHY: FastAPI startup can be slow and complex. Starting it last prevents
# blocking other services and eliminates timing/port binding issues.
# This pattern was discovered after parallel startup caused intermittent
# crashes. Sequential startup with FastAPI last is the reliable solution.
# ============================================================================

# ============================================================================
# MANAGER VISION STARTUP OPTION
# ============================================================================

# Check if Manager Vision startup is requested
if [ "$1" = "--manager-vision" ] || [ "$1" = "-mv" ]; then
    print_status "Using Manager Vision orchestration for platform startup..."
    print_status "This provides the missing orchestration layer for platform coordination"
    echo ""
    
    # Use Manager Vision startup script
    if [ -f "startup_manager_vision.sh" ]; then
        ./startup_manager_vision.sh
        exit $?
    else
        print_error "Manager Vision startup script not found"
        print_status "Falling back to standard startup..."
    fi
fi

# ============================================================================
# PHASE 1: INFRASTRUCTURE SERVICES
# ============================================================================

print_status "Phase 1: Starting infrastructure services..."

# Check if Redis is running
    if ! pgrep -x "redis-server" > /dev/null; then
        print_warning "Redis is not running. Starting Redis..."
        redis-server --daemonize yes
        sleep 2
        print_success "Redis started"
    else
        print_success "Redis already running"
    fi

# Check if we're using Docker Compose for infrastructure
if [ -f "../docker-compose.prod.yml" ]; then
    print_status "Found Docker Compose configuration. Starting infrastructure services..."
    
    # Start Redis and other infrastructure services via Docker Compose
    cd ..
    docker-compose -f docker-compose.prod.yml up -d redis
    
    # Wait for Redis to be healthy
    print_status "Waiting for Redis to become healthy..."
    max_wait=30
    wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis is healthy"
            break
        fi
        sleep 2
        wait_time=$((wait_time + 2))
        print_status "Waiting for Redis... ($wait_time/$max_wait seconds)"
    done
    
    if [ $wait_time -ge $max_wait ]; then
        print_warning "Redis health check timeout, continuing anyway..."
    fi
    
    cd symphainy-platform
else
    print_warning "No Docker Compose configuration found, using local services"
fi

# ============================================================================
# PHASE 2: CELERY WORKER (NO PORTS)
# ============================================================================

print_status "Phase 2: Starting Celery worker..."

# Check if Celery is already running
if pgrep -f "celery.*worker" > /dev/null; then
    print_warning "Celery worker already running, killing existing process..."
    pkill -f "celery.*worker"
    sleep 2
fi

# Start Celery worker using Poetry
poetry run celery -A main worker --loglevel=info --detach
CELERY_PID=$(pgrep -f "celery.*worker")
print_success "Celery worker started (PID: $CELERY_PID)"

# Wait for Celery to fully start
sleep 3

# Check Celery health
check_celery_health() {
    print_status "Checking Celery health..."
    for i in {1..30}; do
        if poetry run celery -A main.celery inspect ping >/dev/null 2>&1; then
            print_success "Celery is healthy"
            return 0
        fi
        sleep 2
    done
    print_error "Celery health check failed"
    return 1
}

# Check ArangoDB health (if running)
check_arangodb_health() {
    print_status "Checking ArangoDB health..."
    for i in {1..30}; do
        if curl -f http://localhost:8529/_api/version >/dev/null 2>&1; then
            print_success "ArangoDB is healthy"
            return 0
        fi
        sleep 2
    done
    print_error "ArangoDB health check failed"
    return 1
}

# Check OpenTelemetry Collector health (if running)
check_otel_collector_health() {
    print_status "Checking OpenTelemetry Collector health..."
    for i in {1..30}; do
        if curl -f http://localhost:8888/metrics >/dev/null 2>&1; then
            print_success "OpenTelemetry Collector is healthy"
            return 0
        fi
        sleep 2
    done
    print_error "OpenTelemetry Collector health check failed"
    return 1
}

# Check infrastructure services health
print_status "Checking infrastructure services health..."
check_celery_health || print_warning "Celery health check failed - continuing anyway"
check_arangodb_health || print_warning "ArangoDB health check failed - continuing anyway"
check_otel_collector_health || print_warning "OpenTelemetry Collector health check failed - continuing anyway"

# ============================================================================
# PHASE 3: MCP SERVERS (BIND TO PORTS)
# ============================================================================

print_status "Phase 3: Starting MCP servers..."

# Start MCP Server 1 (if exists)
if [ -d "mcp_servers" ] && [ -f "mcp_servers/platform_server/mcp_platform_server.py" ]; then
    PLATFORM_PORT=$(find_available_port 8001)
    if [ "$PLATFORM_PORT" != "8001" ]; then
        print_warning "Port 8001 is in use. Using port $PLATFORM_PORT instead."
    fi
    
    print_status "Starting Platform MCP Server on port $PLATFORM_PORT..."
    MCP_PORT=$PLATFORM_PORT poetry run python mcp_servers/platform_server/mcp_platform_server.py &
    PLATFORM_PID=$!
    print_success "Platform MCP Server started (PID: $PLATFORM_PID) on port $PLATFORM_PORT"
    
    # Wait for platform server to start and verify
    sleep 3
    if lsof -Pi :$PLATFORM_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "Platform MCP Server verified running on port $PLATFORM_PORT"
    else
        print_error "Platform MCP Server failed to start on port $PLATFORM_PORT"
        kill $PLATFORM_PID 2>/dev/null || true
        exit 1
    fi
else
    print_warning "Platform MCP Server not found, skipping..."
    PLATFORM_PORT="N/A"
    PLATFORM_PID="N/A"
fi

# Start MCP Server 2 (if exists)
if [ -d "mcp_servers" ] && [ -f "mcp_servers/business_server/mcp_business_server.py" ]; then
    BUSINESS_PORT=$(find_available_port 8002)
    if [ "$BUSINESS_PORT" != "8002" ]; then
        print_warning "Port 8002 is in use. Using port $BUSINESS_PORT instead."
    fi
    
    print_status "Starting Business MCP Server on port $BUSINESS_PORT..."
    MCP_PORT=$BUSINESS_PORT poetry run python mcp_servers/business_server/mcp_business_server.py &
    BUSINESS_PID=$!
    print_success "Business MCP Server started (PID: $BUSINESS_PID) on port $BUSINESS_PORT"
    
    # Wait for business server to start and verify
    sleep 3
    if lsof -Pi :$BUSINESS_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "Business MCP Server verified running on port $BUSINESS_PORT"
    else
        print_error "Business MCP Server failed to start on port $BUSINESS_PORT"
        kill $BUSINESS_PID 2>/dev/null || true
        exit 1
    fi
else
    print_warning "Business MCP Server not found, skipping..."
    BUSINESS_PORT="N/A"
    BUSINESS_PID="N/A"
fi

# ============================================================================
# PHASE 4: FASTAPI BACKEND (START LAST!)
# ============================================================================

print_status "Phase 4: Starting FastAPI backend LAST (critical for port binding)..."

# Find available port for backend
BACKEND_PORT=$(find_available_port 8000)
if [ "$BACKEND_PORT" != "8000" ]; then
    print_warning "Port 8000 is in use. Using port $BACKEND_PORT instead."
fi

# Start FastAPI backend LAST (let it take its time) - Critical Pattern!
print_status "Starting FastAPI backend on port $BACKEND_PORT..."
poetry run python main.py --port $BACKEND_PORT &
UVICORN_PID=$!

# Wait for uvicorn to start and bind to the port (this is the critical part!)
print_status "Waiting for FastAPI to bind to port $BACKEND_PORT..."
max_wait=30
wait_time=0

while [ $wait_time -lt $max_wait ]; do
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "FastAPI backend bound to port $BACKEND_PORT"
        break
    fi
    sleep 2
    wait_time=$((wait_time + 2))
    print_status "Waiting for FastAPI port binding... ($wait_time/$max_wait seconds)"
done

if [ $wait_time -ge $max_wait ]; then
    print_error "FastAPI failed to bind to port $BACKEND_PORT within $max_wait seconds"
    kill $UVICORN_PID 2>/dev/null || true
    exit 1
fi

# Additional health check
sleep 2
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    print_success "FastAPI backend health check passed"
else
    print_warning "FastAPI backend health check failed, but port is bound"
fi

# ============================================================================
# SAVE PIDS FOR CLEANUP
# ============================================================================

# Save PIDs for cleanup
echo $CELERY_PID > .celery.pid
echo $UVICORN_PID > .uvicorn.pid
echo $BACKEND_PORT > .backend_port

if [ "$PLATFORM_PID" != "N/A" ]; then
    echo $PLATFORM_PID > .mcp_platform.pid
    echo $PLATFORM_PORT > .mcp_platform_port
fi

if [ "$BUSINESS_PID" != "N/A" ]; then
    echo $BUSINESS_PID > .mcp_business.pid
    echo $BUSINESS_PORT > .mcp_business_port
fi

# ============================================================================
# FINAL STATUS REPORT
# ============================================================================

print_success "All services started successfully with proper sequencing!"
echo ""
echo "📊 Service Status:"
echo "  - Redis: Running"
echo "  - Celery: Running (PID: $CELERY_PID)"
echo "  - FastAPI: Running (PID: $UVICORN_PID) on port $BACKEND_PORT"

if [ "$PLATFORM_PID" != "N/A" ]; then
    echo "  - Platform MCP: Running (PID: $PLATFORM_PID) on port $PLATFORM_PORT"
fi

if [ "$BUSINESS_PID" != "N/A" ]; then
    echo "  - Business MCP: Running (PID: $BUSINESS_PID) on port $BUSINESS_PORT"
fi

echo ""
echo "🌐 Backend available at: http://localhost:$BACKEND_PORT"
echo "📚 API docs available at: http://localhost:$BACKEND_PORT/docs"
echo "🏥 Health check available at: http://localhost:$BACKEND_PORT/health"

if [ "$PLATFORM_PORT" != "N/A" ]; then
    echo "🔌 Platform MCP available at: http://localhost:$PLATFORM_PORT"
fi

if [ "$BUSINESS_PORT" != "N/A" ]; then
    echo "🔌 Business MCP available at: http://localhost:$BUSINESS_PORT"
fi

echo ""
echo "To stop all services, run: ./stop.sh"
echo "To view logs, run: ./logs.sh"
echo ""
echo "✅ Startup complete! All services are running in the background."
echo "💡 Use './stop.sh' to stop all services when you're done."
echo ""
echo "🚨 IMPORTANT: FastAPI started LAST to prevent port binding issues!"