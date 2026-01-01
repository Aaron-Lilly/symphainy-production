#!/bin/bash

# Symphainy Platform - Infrastructure Startup Script
# Starts all infrastructure services using Docker Compose with port checking and cleanup

set -e

echo "🐳 Symphainy Platform - Starting Infrastructure Services"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Port configuration - Updated with correct port mappings
REQUIRED_PORTS=(8501 6379 8529 3200 4317 4318 8889 3100)
PORT_SERVICES=(
    "8501:Consul API (UI accessible via 8501)"
    "6379:Redis"
    "8529:ArangoDB"
    "3200:Tempo UI"
    "4317:OTLP gRPC (OpenTelemetry Collector)"
    "4318:OTLP HTTP (OpenTelemetry Collector)"
    "8889:OTel Collector Metrics"
    "3100:Grafana"
)

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

# Function to check if a port is available
check_port_available() {
    local port=$1
    local service_name=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        print_error "Port $port is already in use by another process"
        print_error "Service: $service_name"
        print_error "Please stop the conflicting service or choose different ports"
        return 1
    fi
    return 0
}

# Function to check all required ports
check_all_ports() {
    print_status "Checking port availability..."
    
    local port_conflicts=0
    
    for port_info in "${PORT_SERVICES[@]}"; do
        IFS=':' read -r port service <<< "$port_info"
        if ! check_port_available $port "$service"; then
            port_conflicts=$((port_conflicts + 1))
        fi
    done
    
    if [ $port_conflicts -gt 0 ]; then
        print_error "Found $port_conflicts port conflicts. Cannot start infrastructure."
        print_status "To resolve conflicts:"
        print_status "1. Stop conflicting services"
        print_status "2. Or modify docker-compose.infrastructure.yml to use different ports"
        print_status "3. Or run: ./scripts/stop-infrastructure.sh to clean up existing containers"
        exit 1
    fi
    
    print_success "All required ports are available"
}

# Function to cleanup on failure
cleanup_on_failure() {
    print_error "Infrastructure startup failed. Cleaning up..."
    print_status "Stopping all containers..."
    docker-compose -f docker-compose.infrastructure.yml down -v 2>/dev/null || true
    print_status "Removing orphaned containers..."
    docker container prune -f 2>/dev/null || true
    print_error "Cleanup complete. Please resolve issues and try again."
    exit 1
}

# Set up trap for cleanup on failure
trap cleanup_on_failure ERR

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Check if infrastructure compose file exists
if [ ! -f "docker-compose.infrastructure.yml" ]; then
    print_error "docker-compose.infrastructure.yml not found"
    exit 1
fi

# Check if lsof is available for port checking
if ! command -v lsof &> /dev/null; then
    print_warning "lsof not found, skipping port availability check"
    print_warning "Install lsof for better port conflict detection: sudo apt-get install lsof"
else
    # Check all required ports before starting
    check_all_ports
fi

# Clean up any existing containers first
print_status "Cleaning up any existing infrastructure containers..."
docker-compose -f docker-compose.infrastructure.yml down -v 2>/dev/null || true

# Load environment variables
if [ -f "platform_env_file_for_cursor.md" ]; then
    print_status "Loading environment variables from platform_env_file_for_cursor.md..."
    # Extract environment variables from the markdown file
    grep "^[A-Z_][A-Z0-9_]*=" platform_env_file_for_cursor.md | while read line; do
        export "$line"
    done
    print_success "Environment variables loaded"
else
    print_warning "platform_env_file_for_cursor.md not found, using defaults"
fi

# Start infrastructure services
print_status "Starting infrastructure services..."

# Start services in dependency order
print_status "Starting Consul (Service Discovery)..."
docker-compose -f docker-compose.infrastructure.yml up -d consul

print_status "Starting Redis (Cache & Message Broker)..."
docker-compose -f docker-compose.infrastructure.yml up -d redis

print_status "Starting ArangoDB (Metadata Storage)..."
docker-compose -f docker-compose.infrastructure.yml up -d arangodb

print_status "Starting Tempo (Distributed Tracing)..."
docker-compose -f docker-compose.infrastructure.yml up -d tempo

print_status "Starting OpenTelemetry Collector..."
docker-compose -f docker-compose.infrastructure.yml up -d otel-collector

print_status "Starting Celery Worker..."
docker-compose -f docker-compose.infrastructure.yml up -d celery-worker

print_status "Starting Celery Beat (Scheduler)..."
docker-compose -f docker-compose.infrastructure.yml up -d celery-beat

print_status "Starting Grafana (Visualization)..."
docker-compose -f docker-compose.infrastructure.yml up -d grafana

# Check if OPA service exists in docker-compose
if docker-compose -f docker-compose.infrastructure.yml config --services | grep -q "opa"; then
    print_status "Starting OPA (Open Policy Agent)..."
    docker-compose -f docker-compose.infrastructure.yml up -d opa
fi

# Function to check service health with timeout
check_service_health() {
    local service_name=$1
    local check_command=$2
    local max_attempts=${3:-30}
    local timeout=${4:-2}
    
    print_status "Checking $service_name health..."
    
    for i in $(seq 1 $max_attempts); do
        if eval "$check_command" >/dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        
        if [ $i -eq $max_attempts ]; then
            print_error "$service_name failed to become healthy after $max_attempts attempts"
            return 1
        fi
        
        print_status "Waiting for $service_name... (attempt $i/$max_attempts)"
        sleep $timeout
    done
}

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."

# Check Consul
if ! check_service_health "Consul" "curl -f http://localhost:8500/v1/status/leader"; then
    print_error "Consul health check failed"
    cleanup_on_failure
fi

# Check Redis
if ! check_service_health "Redis" "docker exec symphainy-redis redis-cli ping"; then
    print_error "Redis health check failed"
    cleanup_on_failure
fi

# Check ArangoDB
if ! check_service_health "ArangoDB" "curl -f http://localhost:8529/_api/version"; then
    print_error "ArangoDB health check failed"
    cleanup_on_failure
fi

# Check Tempo
if ! check_service_health "Tempo" "curl -f http://localhost:3200/status"; then
    print_error "Tempo health check failed"
    cleanup_on_failure
fi

# Check OpenTelemetry Collector (using port 8889 which maps to internal 8890)
# Note: OTel collector doesn't have curl/wget, so we check from host
if ! check_service_health "OpenTelemetry Collector" "curl -f http://localhost:8889/metrics"; then
    print_warning "OpenTelemetry Collector health check failed, but service may still be running"
    print_status "Checking OTel collector logs for 'Everything is ready' message..."
    if docker logs symphainy-otel-collector 2>&1 | grep -q "Everything is ready"; then
        print_success "OpenTelemetry Collector is running (verified via logs)"
    else
        print_warning "OpenTelemetry Collector may not be fully ready, but continuing..."
    fi
fi

# Check Celery Worker (if it exists)
if docker ps --format "table {{.Names}}" | grep -q "symphainy-celery-worker"; then
    if ! check_service_health "Celery Worker" "docker exec symphainy-celery-worker celery -A main.celery inspect ping"; then
        print_warning "Celery Worker health check failed (this may be expected if no application is running)"
    fi
fi

# Check Grafana
if ! check_service_health "Grafana" "curl -f http://localhost:3100/api/health"; then
    print_error "Grafana health check failed"
    cleanup_on_failure
fi

# Check OPA (if it exists) - make it non-blocking since it's optional
if docker-compose -f docker-compose.infrastructure.yml config --services | grep -q "opa"; then
    if ! check_service_health "OPA" "curl -f http://localhost:8181/health"; then
        print_warning "OPA health check failed (OPA is optional, continuing anyway)"
    fi
fi

# Show service status
print_status "Infrastructure services status:"
docker-compose -f docker-compose.infrastructure.yml ps

print_success "All infrastructure services started successfully!"
print_status "Service URLs:"
print_status "  - Consul UI: http://localhost:8500"
print_status "  - ArangoDB: http://localhost:8529"
print_status "  - Tempo UI: http://localhost:3200"
print_status "  - Grafana: http://localhost:3100 (admin/admin)"
print_status "  - OpenTelemetry Collector: http://localhost:8888/metrics"
print_status "  - Redis: localhost:6379"

print_success "Infrastructure startup complete! 🚀"
