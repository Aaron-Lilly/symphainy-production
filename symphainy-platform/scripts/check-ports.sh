#!/bin/bash

# Symphainy Platform - Port Availability Checker
# Checks if all required ports are available before starting infrastructure

set -e

echo "🔍 Symphainy Platform - Port Availability Check"
echo "==============================================="

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

# Port configuration - Updated with correct port mappings
PORT_SERVICES=(
    "8501:Consul API/UI"
    "6379:Redis"
    "8529:ArangoDB"
    "3200:Tempo UI"
    "4317:OTLP gRPC (OpenTelemetry Collector)"
    "4318:OTLP HTTP (OpenTelemetry Collector)"
    "8889:OTel Collector Metrics"
    "3100:Grafana"
)

# Function to check if a port is available
check_port_available() {
    local port=$1
    local service_name=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        print_error "Port $port is already in use"
        print_error "Service: $service_name"
        
        # Show what's using the port
        print_status "Process using port $port:"
        lsof -i :$port | head -2
        
        return 1
    fi
    return 0
}

# Function to check all required ports
check_all_ports() {
    print_status "Checking port availability..."
    
    local port_conflicts=0
    local available_ports=0
    
    for port_info in "${PORT_SERVICES[@]}"; do
        IFS=':' read -r port service <<< "$port_info"
        if check_port_available $port "$service"; then
            print_success "Port $port ($service) is available"
            available_ports=$((available_ports + 1))
        else
            port_conflicts=$((port_conflicts + 1))
        fi
    done
    
    echo ""
    print_status "Port Check Summary:"
    print_status "  Available: $available_ports"
    print_status "  Conflicts: $port_conflicts"
    
    if [ $port_conflicts -gt 0 ]; then
        print_error "Found $port_conflicts port conflicts. Cannot start infrastructure."
        echo ""
        print_status "To resolve conflicts:"
        print_status "1. Stop conflicting services:"
        print_status "   sudo systemctl stop redis-server  # Stop system Redis"
        print_status "   sudo systemctl disable redis-server"
        print_status "2. Or modify docker-compose.infrastructure.yml to use different ports"
        print_status "3. Or run: ./scripts/stop-infrastructure.sh to clean up existing containers"
        return 1
    fi
    
    print_success "All required ports are available! ✅"
    return 0
}

# Check if lsof is available
if ! command -v lsof &> /dev/null; then
    print_error "lsof is not installed. Cannot check port availability."
    print_status "Install lsof: sudo apt-get install lsof"
    exit 1
fi

# Run port check
if check_all_ports; then
    print_success "Port check passed! Infrastructure can be started safely."
    exit 0
else
    print_error "Port check failed! Please resolve conflicts before starting infrastructure."
    exit 1
fi
