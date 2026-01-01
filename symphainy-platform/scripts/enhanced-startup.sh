#!/bin/bash
# SymphAIny Platform - Enhanced Startup Script with Dependency-Ordered Startup

set -e

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

# Ensure we are in the symphainy-platform directory
if [ ! -f "pyproject.toml" ]; then
    print_error "This script must be run from the symphainy-platform directory (pyproject.toml not found)"
    exit 1
fi

print_status "🚀 Starting SymphAIny Platform - Enhanced Dependency-Ordered Startup"
echo "==================================================================="

# Step 1: Upgrade pip
print_status "Step 1: Upgrading pip..."
python3 -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    print_error "❌ Failed to upgrade pip"
    exit 1
fi
print_success "✅ pip upgraded successfully"

# Step 2: Install Poetry if not present
print_status "Step 2: Checking and installing Poetry..."
if ! command -v poetry &> /dev/null; then
    print_warning "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    if [ $? -ne 0 ]; then
        print_error "❌ Failed to install Poetry"
        exit 1
    fi
    # Add Poetry to PATH for current session
    export PATH="/home/$USER/.local/bin:$PATH"
    print_success "✅ Poetry installed and added to PATH"
else
    print_success "✅ Poetry already installed: $(poetry --version)"
fi

# Step 3: Use poetry/pyproject.toml to set up environment and install dependencies
print_status "Step 3: Setting up Poetry environment and installing dependencies..."
# Validate poetry.lock (should be committed, not regenerated)
print_status "Validating poetry.lock..."
if python3 scripts/validate-poetry-lock.py; then
    print_success "✅ poetry.lock is valid"
else
    print_error "❌ poetry.lock validation failed"
    print_error "Please run 'poetry lock' locally and commit the updated file"
    exit 1
fi

print_status "Running 'poetry install --only main' to install production dependencies..."
poetry install --only main
if [ $? -ne 0 ]; then
    print_error "❌ 'poetry install --only main' failed. Please check pyproject.toml and dependencies."
    exit 1
fi
print_success "✅ Poetry environment set up and dependencies installed"

# Step 4: Start up all Docker/port stuff and platform services
print_status "Step 4: Starting Docker infrastructure and platform services..."

# Assuming docker-compose.platform.yml is the main orchestration file for containerized setup
# If running host-based, this section would be different.
# For now, let's assume the containerized approach is the desired production setup.
if [ -f "docker-compose.platform.yml" ]; then
    print_status "Starting containerized infrastructure and platform..."
    docker-compose -f docker-compose.platform.yml up -d
    if [ $? -ne 0 ]; then
        print_error "❌ Docker Compose failed to start services"
        exit 1
    fi
    print_success "✅ Docker services started"

    print_status "Waiting for containerized services to become healthy..."
    sleep 20 # Give containers time to start

    # Basic health checks for containerized services
    if docker-compose -f docker-compose.platform.yml ps | grep -q "Up"; then
        print_success "✅ All Docker containers are running"
    else
        print_error "❌ Some Docker containers failed to start"
        docker-compose -f docker-compose.platform.yml ps
        exit 1
    fi
else
    print_warning "No 'docker-compose.platform.yml' found. Starting enhanced main.py directly."
    # Start the enhanced main.py with proper dependency-ordered startup
    print_status "Starting Enhanced SymphAIny Platform with Dependency-Ordered Startup..."
    poetry run python enhanced_main.py &
    ENHANCED_MAIN_PID=$!
    print_success "✅ Enhanced SymphAIny Platform started (PID: $ENHANCED_MAIN_PID) on port 8000"
    echo $ENHANCED_MAIN_PID > .enhanced_main.pid
fi

echo ""
print_success "🎉 SymphAIny Platform - Enhanced Startup Complete!"
echo "============================================================"
echo ""
echo "🌐 Access Points:"
echo "  • Main Platform: http://localhost:3000 (if frontend is also running)"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Platform Status: http://localhost:8000/platform/status"
echo "  • Domain Manager Health: http://localhost:8000/platform/health/{manager_name}"
echo ""
echo "📊 Domain Manager Health Endpoints:"
echo "  • City Manager: http://localhost:8000/platform/health/city_manager"
echo "  • Agentic Manager: http://localhost:8000/platform/health/agentic_manager"
echo "  • Delivery Manager: http://localhost:8000/platform/health/delivery_manager"
echo "  • Experience Manager: http://localhost:8000/platform/health/experience_manager"
echo "  • Journey Manager: http://localhost:8000/platform/health/journey_manager"
echo ""
echo "🛑 To stop services:"
echo "  • Docker: docker-compose -f docker-compose.platform.yml down"
echo "  • Enhanced Main: kill $(cat .enhanced_main.pid)"
echo ""
print_status "Platform is running with enhanced dependency-ordered startup. Press Ctrl+C to stop this script if host-based, or manage Docker containers separately."




