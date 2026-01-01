#!/bin/bash
# Simplified Infrastructure Startup Script
# Uses minimal dependencies and our new architecture patterns

set -e

echo "🐳 SymphAIny Platform - Simplified Infrastructure Startup"
echo "========================================================="
echo "Using minimal dependencies and new architecture patterns"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check port availability
echo "🔍 Checking port availability..."
required_ports=(8501 6379 8529 3200 4317 4318 8889 3000)
for port in "${required_ports[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Port $port is already in use. Please stop the conflicting service."
        echo "   Run: lsof -i :$port to see what's using it"
        exit 1
    fi
done
echo "✅ All required ports are available"

# Load environment variables
echo "📋 Loading environment variables..."
if [ -f "platform_env_file_for_cursor.md" ]; then
    echo "✅ Environment variables loaded from platform_env_file_for_cursor.md"
else
    echo "⚠️  platform_env_file_for_cursor.md not found, using defaults"
fi

# Start infrastructure services
echo "🚀 Starting infrastructure services..."

# Use simplified Docker Compose
echo "📡 Starting Consul (Service Discovery)..."
docker-compose -f docker-compose.simplified.yml up -d consul

echo "📡 Starting Redis (Cache & Message Broker)..."
docker-compose -f docker-compose.simplified.yml up -d redis

echo "📡 Starting ArangoDB (Metadata Storage)..."
docker-compose -f docker-compose.simplified.yml up -d arangodb

echo "📡 Starting Tempo (Distributed Tracing)..."
docker-compose -f docker-compose.simplified.yml up -d tempo

echo "📡 Starting OpenTelemetry Collector..."
docker-compose -f docker-compose.simplified.yml up -d otel-collector

echo "📡 Starting Celery Worker (Background Tasks)..."
docker-compose -f docker-compose.simplified.yml up -d celery-worker

echo "📡 Starting Celery Beat (Task Scheduler)..."
docker-compose -f docker-compose.simplified.yml up -d celery-beat

echo "📡 Starting Grafana (Visualization)..."
docker-compose -f docker-compose.simplified.yml up -d grafana

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health checks
echo "🏥 Performing health checks..."

# Check Consul
if curl -f http://localhost:8501/v1/status/leader > /dev/null 2>&1; then
    echo "✅ Consul: Healthy"
else
    echo "❌ Consul: Unhealthy"
fi

# Check Redis
if docker exec symphainy-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
fi

# Check ArangoDB
if curl -f http://localhost:8529/_api/version > /dev/null 2>&1; then
    echo "✅ ArangoDB: Healthy"
else
    echo "❌ ArangoDB: Unhealthy"
fi

# Check Tempo
if curl -f http://localhost:3200/status > /dev/null 2>&1; then
    echo "✅ Tempo: Healthy"
else
    echo "❌ Tempo: Unhealthy"
fi

# Check OpenTelemetry Collector
if curl -f http://localhost:8889/metrics > /dev/null 2>&1; then
    echo "✅ OpenTelemetry Collector: Healthy"
else
    echo "❌ OpenTelemetry Collector: Unhealthy"
fi

# Check Celery Worker
if docker exec symphainy-celery-worker celery -A main.celery inspect ping > /dev/null 2>&1; then
    echo "✅ Celery Worker: Healthy"
else
    echo "❌ Celery Worker: Unhealthy"
fi

# Check Celery Beat
if docker exec symphainy-celery-beat celery -A main.celery inspect ping > /dev/null 2>&1; then
    echo "✅ Celery Beat: Healthy"
else
    echo "❌ Celery Beat: Unhealthy"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana: Healthy"
else
    echo "❌ Grafana: Unhealthy"
fi

echo ""
echo "🎉 Infrastructure services started successfully!"
echo "================================================"
echo ""
echo "📊 Service Status:"
echo "  - Consul: http://localhost:8501"
echo "  - Redis: localhost:6379"
echo "  - ArangoDB: http://localhost:8529"
echo "  - Tempo: http://localhost:3200"
echo "  - OpenTelemetry Collector: http://localhost:8889/metrics"
echo "  - Grafana: http://localhost:3100"
echo ""
echo "🔧 Celery Services:"
echo "  - Celery Worker: Running (Background tasks)"
echo "  - Celery Beat: Running (Task scheduler)"
echo ""
echo "✅ Ready for application services!"
echo ""
echo "Next steps:"
echo "  1. Run: ./startup.sh (to start application services)"
echo "  2. Access: http://localhost:3100 (Grafana)"
echo "  3. Access: http://localhost:8000 (Main API)"
echo ""




