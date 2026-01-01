#!/bin/bash
# SymphAIny Platform - Simplified C-Suite Startup Script
# Uses minimal dependencies and new architecture patterns

echo "🎯 SymphAIny Platform - Simplified C-Suite Startup"
echo "=================================================="
echo "Using minimal dependencies and new architecture patterns"
echo ""

# Change to platform directory
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Step 1: Start Infrastructure Services (Simplified)
echo "📡 Starting Infrastructure Services (Simplified)..."
./scripts/start-infrastructure-simplified.sh

if [ $? -eq 0 ]; then
    echo "✅ Infrastructure services started successfully!"
else
    echo "❌ Infrastructure startup failed!"
    echo "Trying fallback approach..."
    
    # Fallback: Start only essential services
    echo "🔄 Starting essential services only..."
    docker-compose -f docker-compose.simplified.yml up -d consul redis arangodb tempo otel-collector
    
    if [ $? -eq 0 ]; then
        echo "✅ Essential services started!"
    else
        echo "❌ Even essential services failed!"
        echo "Please check Docker and try again."
        exit 1
    fi
fi

echo ""

# Step 2: Start Application Services
echo "🚀 Starting Application Services..."
./startup.sh

if [ $? -eq 0 ]; then
    echo "✅ Application services started successfully!"
else
    echo "❌ Application startup failed!"
    exit 1
fi

echo ""
echo "🎉 SymphAIny Platform is Ready!"
echo "================================"
echo ""
echo "🌐 Access Points:"
echo "  • Main Platform: http://localhost:3000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Grafana: http://localhost:3000"
echo "  • Consul: http://localhost:8501"
echo ""
echo "🎯 Ready for C-Suite Chaos Testing!"
echo "   • Create accounts with your email"
echo "   • Upload files (PDF, DOCX, CSV, images)"
echo "   • Ask off-the-wall questions to AI agents"
echo "   • Click around randomly to explore"
echo ""
echo "📋 See C_SUITE_GUIDE.md for detailed testing instructions"
echo ""
echo "🛑 To stop the platform:"
echo "   ./stop.sh && ./scripts/stop-infrastructure.sh"
echo ""




