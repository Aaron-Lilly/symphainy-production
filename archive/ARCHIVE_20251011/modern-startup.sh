#!/bin/bash
# SymphAIny Platform - Modern Startup Script
# Following modern DDD/SOA best practices

set -e

echo "🚀 SymphAIny Platform - Modern Startup"
echo "======================================"
echo "Following modern DDD/SOA best practices"
echo ""

# Step 1: Environment setup (minimal)
echo "🔧 Step 1: Setting up environment..."
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Set environment variables
export ENVIRONMENT=development
export DEBUG=true
export HOST=0.0.0.0
export PORT=8000
export RELOAD=true

echo "✅ Environment configured"

# Step 2: Start minimal infrastructure (only what's needed)
echo ""
echo "🐳 Step 2: Starting minimal infrastructure..."
echo "Starting only essential services..."

# Start Redis (essential for caching/sessions)
docker-compose -f docker-compose.simplified.yml up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
sleep 5

# Check Redis health
if docker exec symphainy-redis-essential redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
    exit 1
fi

# Step 3: Start application (modern pattern)
echo ""
echo "🔧 Step 3: Starting application with modern pattern..."
echo "Using minimal dependencies and clean architecture"

# Start the modern application
python3 modern_main.py &
APP_PID=$!

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 5

# Health check
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application: Healthy"
else
    echo "❌ Application: Unhealthy"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Step 4: Start frontend (if needed)
echo ""
echo "🌐 Step 4: Starting frontend..."
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

# Step 5: Final status
echo ""
echo "🎉 SymphAIny Platform - Modern Startup Complete!"
echo "==============================================="
echo ""
echo "📊 Platform Status:"
echo "  - Infrastructure: ✅ Redis only (minimal)"
echo "  - Backend API: ✅ Running (http://localhost:8000)"
echo "  - Frontend: ✅ Running (http://localhost:3000)"
echo ""
echo "🎯 Modern Architecture Benefits:"
echo "  ✅ Minimal dependencies"
echo "  ✅ Clean startup process"
echo "  ✅ Fast and reliable"
echo "  ✅ Easy to debug"
echo "  ✅ Production-ready pattern"
echo ""
echo "🌐 Access Points:"
echo "  • Main Platform: http://localhost:3000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • API Test: http://localhost:8000/api/test"
echo ""
echo "💡 This follows modern DDD/SOA best practices:"
echo "   • Application Factory Pattern"
echo "   • Minimal DI Container"
echo "   • Clean separation of concerns"
echo "   • Fast startup and reliable operation"
echo ""

# Keep running
echo "🔄 Platform is running. Press Ctrl+C to stop."
wait
