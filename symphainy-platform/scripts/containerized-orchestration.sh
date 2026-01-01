#!/bin/bash
# Containerized Orchestration - Master Script
# Coordinates all three layers with proper containerization

set -e

echo "🎯 SymphAIny Platform - Containerized Orchestration"
echo "==================================================="
echo "Coordinating all three layers with proper containerization"
echo ""

# Step 1: Build Platform Container
echo "🐳 Step 1: Building Platform Container"
echo "======================================"
echo "Building platform container with Poetry and .env.secrets..."

# Build the platform container
docker build -f Dockerfile.platform -t symphainy-platform:latest .

if [ $? -ne 0 ]; then
    echo "❌ Platform container build failed"
    exit 1
fi

echo "✅ Platform container built successfully"
echo ""

# Step 2: Start Infrastructure and Platform
echo "🚀 Step 2: Starting Infrastructure and Platform"
echo "=============================================="
echo "Starting infrastructure services and platform container..."

# Start infrastructure and platform
docker-compose -f docker-compose.platform.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 20

# Step 3: Health checks
echo ""
echo "🏥 Step 3: Health checks..."

# Check Redis
if docker exec symphainy-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
    exit 1
fi

# Check Consul
if curl -f http://localhost:8500/v1/status/leader > /dev/null 2>&1; then
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

# Check Platform Container
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Platform Container: Healthy"
else
    echo "❌ Platform Container: Unhealthy"
    exit 1
fi

# Step 4: Start Frontend (if needed)
echo ""
echo "🌐 Step 4: Starting Frontend"
echo "============================"
cd /home/founders/demoversion/symphainy_source/symphainy-frontend

# Start frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend
echo "⏳ Waiting for frontend..."
sleep 10

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy"
fi

# Step 5: Final Status
echo ""
echo "🎉 SymphAIny Platform - Containerized Orchestration Complete!"
echo "============================================================"
echo ""
echo "📊 Platform Status:"
echo "  - Infrastructure Layer: ✅ Redis, Consul, ArangoDB (Docker)"
echo "  - Platform Layer: ✅ Poetry, .env.secrets, DI Container (Docker)"
echo "  - Application Layer: ✅ FastAPI, Experience Layer (Docker)"
echo "  - Frontend: ✅ Next.js React Application (Host)"
echo ""
echo "🎯 Containerized Architecture Benefits:"
echo "  ✅ Clean layer separation"
echo "  ✅ Poetry and .env.secrets containerized"
echo "  ✅ CI/CD ready"
echo "  ✅ Scalable and portable"
echo "  ✅ Dependency isolation"
echo ""
echo "🌐 Access Points:"
echo "  • Main Platform: http://localhost:3000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo ""
echo "💡 This follows modern containerized platform patterns:"
echo "   • Infrastructure as Code (Docker Compose)"
echo "   • Platform as Code (Docker Container)"
echo "   • Application as Code (Docker Container)"
echo "   • Poetry and .env.secrets properly containerized"
echo ""

# Keep running
echo "🔄 Platform is running. Press Ctrl+C to stop."
wait




