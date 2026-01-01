#!/bin/bash
# Start Symphainy Platform - Unified Compose Project
# Single command to start everything

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🚀 Starting Symphainy Platform..."
echo "================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start all services
echo "📦 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose ps

echo ""
echo "✅ Platform starting!"
echo ""
echo "🌐 Access URLs:"
echo "   - Frontend: http://localhost or http://35.215.64.103"
echo "   - Backend API: http://localhost/api or http://35.215.64.103/api"
echo "   - Traefik Dashboard: http://localhost:8080"
echo "   - Consul UI: http://localhost:8500"
echo "   - Grafana: http://localhost:3100"
echo "   - ArangoDB: http://localhost:8529"
echo ""
echo "📝 View logs: docker-compose logs -f [service-name]"
echo "🛑 Stop platform: docker-compose down"
echo ""

