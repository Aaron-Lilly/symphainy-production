#!/bin/bash
# Essential Services Startup Script
# Starts only the most critical services for C-suite testing

set -e

echo "🎯 SymphAIny Platform - Essential Services Startup"
echo "=================================================="
echo "Starting only the most critical services for C-suite testing"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start only essential services (no complex dependencies)
echo "🚀 Starting essential services..."

# Start Redis (for caching and sessions)
echo "📡 Starting Redis..."
docker run -d --name symphainy-redis-essential \
    -p 6379:6379 \
    --restart unless-stopped \
    redis:7-alpine

# Start Consul (for service discovery)
echo "📡 Starting Consul..."
docker run -d --name symphainy-consul-essential \
    -p 8501:8500 \
    -p 8601:8600/udp \
    -p 8601:8600/tcp \
    -p 8301:8300 \
    --restart unless-stopped \
    hashicorp/consul:latest \
    agent -server -bootstrap-expect=1 -ui -client=0.0.0.0

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Health checks
echo "🏥 Performing health checks..."

# Check Redis
if docker exec symphainy-redis-essential redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
fi

# Check Consul
if curl -f http://localhost:8501/v1/status/leader > /dev/null 2>&1; then
    echo "✅ Consul: Healthy"
else
    echo "❌ Consul: Unhealthy"
fi

echo ""
echo "🎉 Essential services started successfully!"
echo "=========================================="
echo ""
echo "📊 Service Status:"
echo "  - Redis: localhost:6379"
echo "  - Consul: http://localhost:8501"
echo ""
echo "✅ Ready for application services!"
echo ""
echo "Next steps:"
echo "  1. Run: ./startup.sh (to start application services)"
echo "  2. Access: http://localhost:8000 (Main API)"
echo "  3. Access: http://localhost:3000 (Frontend)"
echo ""




