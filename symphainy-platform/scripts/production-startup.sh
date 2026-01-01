#!/bin/bash
# SymphAIny Platform - Production Startup Script
# Includes original startup process: pip upgrade, poetry installation, pyproject.toml usage

set -e

echo "🚀 SymphAIny Platform - Production Startup"
echo "==========================================="
echo "Following original startup process:"
echo "1. Upgrade pip"
echo "2. Install Poetry" 
echo "3. Use pyproject.toml"
echo "4. Start platform services"
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

# ============================================================================
# STEP 1: UPGRADE PIP
# ============================================================================

print_status "Step 1: Upgrading pip..."
python3 -m pip install --upgrade pip
print_success "pip upgraded successfully"

# ============================================================================
# STEP 2: INSTALL POETRY
# ============================================================================

print_status "Step 2: Installing Poetry..."

# Check if Poetry is already installed
if command -v poetry &> /dev/null; then
    print_success "Poetry already installed: $(poetry --version)"
else
    print_status "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH
    export PATH="/home/$USER/.local/bin:$PATH"
    
    # Verify installation
    if command -v poetry &> /dev/null; then
        print_success "Poetry installed successfully: $(poetry --version)"
    else
        print_error "Poetry installation failed"
        exit 1
    fi
fi

# ============================================================================
# STEP 3: USE POETRY/PYPROJECT.TOML
# ============================================================================

print_status "Step 3: Using Poetry and pyproject.toml..."

# Validate poetry.lock (should be committed, not regenerated)
print_status "Validating poetry.lock..."
if python3 scripts/validate-poetry-lock.py; then
    print_success "poetry.lock is valid"
else
    print_error "❌ poetry.lock validation failed"
    print_error "Please run 'poetry lock' locally and commit the updated file"
    exit 1
fi

# Check pyproject.toml syntax
print_status "Checking pyproject.toml syntax..."
if poetry check > /dev/null 2>&1; then
    print_success "pyproject.toml syntax is valid"
else
    print_error "❌ pyproject.toml has syntax issues"
    print_error "Please fix pyproject.toml before proceeding"
    exit 1
fi

# Install dependencies
print_status "Installing dependencies with Poetry..."
poetry install --only main

if [ $? -ne 0 ]; then
    print_error "❌ Poetry install failed"
    print_error "This usually means poetry.lock is out of sync with pyproject.toml"
    print_error "Please run 'poetry lock' locally and commit the updated file"
    exit 1
fi

print_success "Dependencies installed successfully"

# ============================================================================
# STEP 4: START PLATFORM SERVICES
# ============================================================================

print_status "Step 4: Starting platform services..."

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

# Start Celery worker using Poetry (use celery_app module to avoid FastAPI app conflict)
poetry run celery -A celery_app worker --loglevel=info --detach
CELERY_PID=$(pgrep -f "celery.*worker")
print_success "Celery worker started (PID: $CELERY_PID)"

# Wait for Celery to fully start
sleep 3

# ============================================================================
# PHASE 3: FASTAPI BACKEND (START LAST!)
# ============================================================================

print_status "Phase 3: Starting FastAPI backend..."

# Find available port for backend
BACKEND_PORT=$(find_available_port 8000)
if [ "$BACKEND_PORT" != "8000" ]; then
    print_warning "Port 8000 is in use. Using port $BACKEND_PORT instead."
fi

# Start FastAPI backend using Poetry
print_status "Starting FastAPI backend on port $BACKEND_PORT..."
poetry run python main.py --port $BACKEND_PORT &
UVICORN_PID=$!

# Wait for uvicorn to start and bind to the port
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

# ============================================================================
# FINAL STATUS REPORT
# ============================================================================

print_success "All services started successfully with original startup process!"
echo ""
echo "📊 Service Status:"
echo "  - pip: Upgraded ✅"
echo "  - Poetry: Installed ✅"
echo "  - pyproject.toml: Used ✅"
echo "  - Redis: Running ✅"
echo "  - Celery: Running (PID: $CELERY_PID) ✅"
echo "  - FastAPI: Running (PID: $UVICORN_PID) on port $BACKEND_PORT ✅"
echo ""
echo "🌐 Backend available at: http://localhost:$BACKEND_PORT"
echo "📚 API docs available at: http://localhost:$BACKEND_PORT/docs"
echo "🏥 Health check available at: http://localhost:$BACKEND_PORT/health"
echo ""
echo "✅ Production startup complete! All services are running."
echo "💡 This follows the original startup process: pip upgrade → poetry install → pyproject.toml → services"
echo ""
echo "🚨 IMPORTANT: This script includes the original startup process:"
echo "   1. ✅ pip upgrade"
echo "   2. ✅ poetry installation" 
echo "   3. ✅ pyproject.toml usage"
echo "   4. ✅ platform services startup"




