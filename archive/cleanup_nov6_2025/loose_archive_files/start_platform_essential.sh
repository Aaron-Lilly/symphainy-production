#!/bin/bash
# SymphAIny Platform - Essential Services C-Suite Startup
# Starts only the most critical services for C-suite testing

echo "🎯 SymphAIny Platform - Essential Services C-Suite Startup"
echo "=========================================================="
echo "Starting only the most critical services for C-suite testing"
echo ""

# Change to platform directory
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Step 1: Start Essential Services Only
echo "📡 Starting Essential Services (Redis + Consul)..."
./scripts/start-essential-services.sh

if [ $? -eq 0 ]; then
    echo "✅ Essential services started successfully!"
else
    echo "❌ Essential services startup failed!"
    echo "Please check Docker and try again."
    exit 1
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
echo "   ./stop.sh && docker stop symphainy-redis-essential symphainy-consul-essential"
echo ""




