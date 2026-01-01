#!/bin/bash
# Stop Symphainy Platform - Unified Compose Project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🛑 Stopping Symphainy Platform..."
echo "=================================="
echo ""

docker-compose down

echo ""
echo "✅ Platform stopped!"
echo ""

