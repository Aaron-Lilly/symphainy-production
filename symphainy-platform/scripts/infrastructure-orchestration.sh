#!/bin/bash
# Infrastructure Orchestration - Layer 1
# Pure infrastructure management with Docker Compose

set -e

echo "🐳 Infrastructure Orchestration - Layer 1"
echo "=========================================="
echo "Managing Docker containers and infrastructure services"
echo ""

# Step 1: Clean up existing infrastructure
echo "🧹 Step 1: Cleaning up existing infrastructure..."
docker-compose -f docker-compose.simplified.yml down 2>/dev/null || true
docker stop $(docker ps -q --filter "name=symphainy-") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=symphainy-") 2>/dev/null || true

# Step 2: Start infrastructure services
echo ""
echo "🚀 Step 2: Starting infrastructure services..."
docker-compose -f docker-compose.simplified.yml up -d redis consul arangodb

# Step 3: Wait for infrastructure to be ready
echo ""
echo "⏳ Step 3: Waiting for infrastructure to be ready..."
sleep 15

# Step 4: Health checks
echo ""
echo "🏥 Step 4: Infrastructure health checks..."

# Check Redis
if docker exec symphainy-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
    exit 1
fi

# Check Consul
if curl -f http://localhost:8501/v1/status/leader > /dev/null 2>&1; then
    echo "✅ Consul: Healthy"
else
    echo "❌ Consul: Unhealthy"
    exit 1
fi

# Check ArangoDB
if curl -f http://localhost:8529/_api/version > /dev/null 2>&1; then
    echo "✅ ArangoDB: Healthy"
else
    echo "❌ ArangoDB: Unhealthy"
    exit 1
fi

echo ""
echo "🎉 Infrastructure Layer - Ready!"
echo "================================"
echo "Infrastructure services are running and healthy"
echo ""
echo "📊 Infrastructure Status:"
echo "  - Redis: ✅ Running (port 6379)"
echo "  - Consul: ✅ Running (port 8501)"
echo "  - ArangoDB: ✅ Running (port 8529)"
echo ""
echo "✅ Infrastructure Layer Complete - Ready for Platform Layer"




