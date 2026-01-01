#!/bin/bash

# Symphainy Platform - Infrastructure Shutdown Script
# Stops all infrastructure services with cleanup

set -e

echo "🛑 Symphainy Platform - Stopping Infrastructure Services"
echo "======================================================="

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

# Function to force cleanup if normal shutdown fails
force_cleanup() {
    print_warning "Normal shutdown failed, forcing cleanup..."
    
    # Force stop all containers
    print_status "Force stopping all infrastructure containers..."
    docker stop $(docker ps -q --filter "name=symphainy-") 2>/dev/null || true
    
    # Remove all infrastructure containers
    print_status "Removing all infrastructure containers..."
    docker rm $(docker ps -aq --filter "name=symphainy-") 2>/dev/null || true
    
    # Remove volumes
    print_status "Removing infrastructure volumes..."
    docker volume rm $(docker volume ls -q --filter "name=symphainy-platform_") 2>/dev/null || true
    
    # Remove networks
    print_status "Removing infrastructure networks..."
    docker network rm symphainy-platform_smart_city_net 2>/dev/null || true
    
    print_success "Force cleanup completed"
}

# Function to check if containers are running
check_containers_running() {
    local running_containers=$(docker ps --format "table {{.Names}}" | grep "symphainy-" | wc -l)
    if [ $running_containers -eq 0 ]; then
        print_status "No infrastructure containers are currently running"
        return 1
    fi
    return 0
}

# Check if infrastructure compose file exists
if [ ! -f "docker-compose.infrastructure.yml" ]; then
    print_error "docker-compose.infrastructure.yml not found"
    exit 1
fi

# Check if any containers are running
if ! check_containers_running; then
    print_status "No infrastructure containers to stop"
    exit 0
fi

# Stop infrastructure services
print_status "Stopping infrastructure services..."

# Try graceful shutdown first
if docker-compose -f docker-compose.infrastructure.yml down; then
    print_success "Graceful shutdown completed"
else
    print_warning "Graceful shutdown failed, attempting force cleanup..."
    force_cleanup
fi

# Verify cleanup
print_status "Verifying cleanup..."
if check_containers_running; then
    print_warning "Some containers are still running, attempting force cleanup..."
    force_cleanup
fi

# Final verification
if check_containers_running; then
    print_error "Failed to stop all containers. Manual cleanup may be required."
    print_status "Run the following commands manually:"
    print_status "  docker stop \$(docker ps -q --filter 'name=symphainy-')"
    print_status "  docker rm \$(docker ps -aq --filter 'name=symphainy-')"
    print_status "  docker volume rm \$(docker volume ls -q --filter 'name=symphainy-platform_')"
    exit 1
fi

# Show final status
print_status "Infrastructure services status:"
docker-compose -f docker-compose.infrastructure.yml ps 2>/dev/null || print_status "No containers found"

print_success "All infrastructure services stopped successfully!"
print_status "To start services again, run: ./scripts/start-infrastructure.sh"
print_status "To remove all containers and volumes, run: docker-compose -f docker-compose.infrastructure.yml down -v"

print_success "Infrastructure shutdown complete! 🛑"
