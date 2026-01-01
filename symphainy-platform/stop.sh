#!/bin/bash

# SymphAIny Platform - Stop All Services Script
# This script stops all services started by startup.sh

set -e

echo "🛑 SymphAIny Platform - Stopping All Services"
echo "=============================================="

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

# Function to stop process by PID
stop_process() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && [ "$pid" != "N/A" ]; then
        if kill -0 $pid 2>/dev/null; then
            print_status "Stopping $name (PID: $pid)..."
            kill $pid
            sleep 2
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                print_warning "Force killing $name (PID: $pid)..."
                kill -9 $pid
                sleep 1
            fi
            
            if kill -0 $pid 2>/dev/null; then
                print_error "Failed to stop $name (PID: $pid)"
                return 1
            else
                print_success "$name stopped"
                return 0
            fi
        else
            print_warning "$name (PID: $pid) is not running"
            return 0
        fi
    else
        print_warning "No PID found for $name"
        return 0
    fi
}

# Stop services in reverse order of startup
print_status "Stopping services in reverse startup order..."

# Stop FastAPI backend
if [ -f ".uvicorn.pid" ]; then
    UVICORN_PID=$(cat .uvicorn.pid)
    stop_process $UVICORN_PID "FastAPI Backend"
    rm -f .uvicorn.pid
else
    print_warning "No FastAPI PID file found"
fi

# Stop MCP servers
if [ -f ".mcp_platform.pid" ]; then
    PLATFORM_PID=$(cat .mcp_platform.pid)
    stop_process $PLATFORM_PID "Platform MCP Server"
    rm -f .mcp_platform.pid .mcp_platform_port
else
    print_warning "No Platform MCP PID file found"
fi

if [ -f ".mcp_business.pid" ]; then
    BUSINESS_PID=$(cat .mcp_business.pid)
    stop_process $BUSINESS_PID "Business MCP Server"
    rm -f .mcp_business.pid .mcp_business_port
else
    print_warning "No Business MCP PID file found"
fi

# Stop Celery worker
if [ -f ".celery.pid" ]; then
    CELERY_PID=$(cat .celery.pid)
    stop_process $CELERY_PID "Celery Worker"
    rm -f .celery.pid
else
    print_warning "No Celery PID file found"
fi

# Stop any remaining Celery processes
print_status "Stopping any remaining Celery processes..."
pkill -f "celery.*worker" 2>/dev/null || true
pkill -f "poetry.*celery" 2>/dev/null || true

# Stop Redis if we started it locally
if pgrep -x "redis-server" > /dev/null; then
    print_status "Stopping Redis..."
    redis-cli shutdown 2>/dev/null || true
    sleep 2
    
    if pgrep -x "redis-server" > /dev/null; then
        print_warning "Force stopping Redis..."
        pkill -9 redis-server 2>/dev/null || true
    fi
    
    print_success "Redis stopped"
fi

# Stop Docker Compose services if running
if [ -f "../docker-compose.prod.yml" ]; then
    print_status "Stopping Docker Compose services..."
    cd ..
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    cd symphainy-platform
    print_success "Docker Compose services stopped"
fi

# Clean up PID files
rm -f .backend_port

# Final cleanup - kill any remaining processes on our ports
print_status "Cleaning up any remaining processes on our ports..."
for port in 8000 8001 8002 6379; do
    pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
    if [ -n "$pids" ]; then
        print_warning "Killing remaining processes on port $port: $pids"
        for pid in $pids; do
            kill $pid 2>/dev/null || true
        done
    fi
done

# Clean up any remaining Poetry processes
print_status "Cleaning up any remaining Poetry processes..."
pkill -f "poetry.*python" 2>/dev/null || true
pkill -f "poetry.*uvicorn" 2>/dev/null || true

print_success "All services stopped successfully!"
echo ""
echo "📊 Cleanup Summary:"
echo "  - FastAPI Backend: Stopped"
echo "  - MCP Servers: Stopped"
echo "  - Celery Worker: Stopped"
echo "  - Redis: Stopped"
echo "  - Docker Services: Stopped"
echo "  - PID files: Cleaned up"
echo ""
echo "✅ Shutdown complete!"