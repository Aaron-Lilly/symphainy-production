#!/bin/bash

# SymphAIny Platform - View Logs Script
# This script shows logs for all running services

echo "📋 SymphAIny Platform - Service Logs"
echo "===================================="

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

# Function to show logs for a service
show_service_logs() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat $pid_file)
        if kill -0 $pid 2>/dev/null; then
            print_status "Showing logs for $service_name (PID: $pid)..."
            echo "----------------------------------------"
            # Note: For background processes, we can't easily tail their logs
            # This would need to be enhanced with proper log file handling
            echo "Service $service_name is running (PID: $pid)"
            echo "Logs would be shown here if configured with proper log files"
            echo ""
        else
            print_warning "$service_name is not running"
        fi
    else
        print_warning "No PID file found for $service_name"
    fi
}

# Show service status
print_status "Service Status:"
echo ""

# Check FastAPI Backend
if [ -f ".uvicorn.pid" ]; then
    UVICORN_PID=$(cat .uvicorn.pid)
    if kill -0 $UVICORN_PID 2>/dev/null; then
        print_success "FastAPI Backend: Running (PID: $UVICORN_PID)"
        if [ -f ".backend_port" ]; then
            BACKEND_PORT=$(cat .backend_port)
            echo "  - Port: $BACKEND_PORT"
            echo "  - URL: http://localhost:$BACKEND_PORT"
            echo "  - Health: http://localhost:$BACKEND_PORT/health"
        fi
    else
        print_warning "FastAPI Backend: Not running"
    fi
else
    print_warning "FastAPI Backend: No PID file found"
fi

# Check Celery Worker
if [ -f ".celery.pid" ]; then
    CELERY_PID=$(cat .celery.pid)
    if kill -0 $CELERY_PID 2>/dev/null; then
        print_success "Celery Worker: Running (PID: $CELERY_PID)"
    else
        print_warning "Celery Worker: Not running"
    fi
else
    print_warning "Celery Worker: No PID file found"
fi

# Check Platform MCP Server
if [ -f ".mcp_platform.pid" ]; then
    PLATFORM_PID=$(cat .mcp_platform.pid)
    if kill -0 $PLATFORM_PID 2>/dev/null; then
        print_success "Platform MCP Server: Running (PID: $PLATFORM_PID)"
        if [ -f ".mcp_platform_port" ]; then
            PLATFORM_PORT=$(cat .mcp_platform_port)
            echo "  - Port: $PLATFORM_PORT"
            echo "  - URL: http://localhost:$PLATFORM_PORT"
        fi
    else
        print_warning "Platform MCP Server: Not running"
    fi
else
    print_warning "Platform MCP Server: No PID file found"
fi

# Check Business MCP Server
if [ -f ".mcp_business.pid" ]; then
    BUSINESS_PID=$(cat .mcp_business.pid)
    if kill -0 $BUSINESS_PID 2>/dev/null; then
        print_success "Business MCP Server: Running (PID: $BUSINESS_PID)"
        if [ -f ".mcp_business_port" ]; then
            BUSINESS_PORT=$(cat .mcp_business_port)
            echo "  - Port: $BUSINESS_PORT"
            echo "  - URL: http://localhost:$BUSINESS_PORT"
        fi
    else
        print_warning "Business MCP Server: Not running"
    fi
else
    print_warning "Business MCP Server: No PID file found"
fi

# Check Redis
if pgrep -x "redis-server" > /dev/null; then
    print_success "Redis: Running"
else
    print_warning "Redis: Not running"
fi

# Check Docker services
if [ -f "../docker-compose.prod.yml" ]; then
    print_status "Docker Compose Services:"
    cd ..
    docker-compose -f docker-compose.prod.yml ps
    cd symphainy-platform
fi

echo ""
print_status "To view real-time logs, you can:"
echo "  - Use 'tail -f' on log files (if configured)"
echo "  - Use 'docker-compose logs -f' for Docker services"
echo "  - Use 'journalctl -f' for systemd services"
echo ""
print_status "To restart services, run: ./startup.sh"
print_status "To stop services, run: ./stop.sh"




















