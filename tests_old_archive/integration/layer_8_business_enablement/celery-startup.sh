#!/bin/bash
# Celery Startup Script for Testing
# Starts Celery worker/beat outside of Docker for testing
# Uses CeleryAdapter's configuration instead of requiring Celery app in main.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="${SCRIPT_DIR}/../../symphainy-platform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "🌾 Celery Startup for Testing"
echo "============================="
echo ""

# Check if we're in the right location
if [ ! -f "$PLATFORM_DIR/main.py" ]; then
    print_error "main.py not found at $PLATFORM_DIR"
    exit 1
fi

cd "$PLATFORM_DIR"

# ============================================================================
# CHECK PREREQUISITES
# ============================================================================

print_status "Checking prerequisites..."

# Check if Redis is available
if timeout 5 redis-cli -h localhost ping > /dev/null 2>&1; then
    print_success "Redis is available"
else
    print_error "Redis is not available - start infrastructure first"
    exit 1
fi

# Check if Poetry is available
if command -v poetry &> /dev/null; then
    print_success "Poetry is available: $(poetry --version)"
else
    print_error "Poetry is not installed"
    exit 1
fi

echo ""

# ============================================================================
# START CELERY WORKER
# ============================================================================

print_status "Starting Celery worker..."

# Check if Celery worker is already running
if pgrep -f "celery.*worker" > /dev/null; then
    print_warning "Celery worker already running, killing existing process..."
    pkill -f "celery.*worker"
    sleep 2
fi

# Start Celery worker using celery_app module (same as production)
print_status "Starting Celery worker with celery_app module..."
poetry run celery -A celery_app worker --loglevel=info --detach 2>&1 || {
    print_error "Failed to start Celery worker"
    exit 1
}

CELERY_PID=$(pgrep -f "celery.*worker")
print_success "Celery worker started (PID: $CELERY_PID)"

# Wait for Celery to fully start
sleep 3

# ============================================================================
# START CELERY BEAT (OPTIONAL)
# ============================================================================

read -p "Start Celery Beat scheduler? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting Celery Beat..."
    
    # Check if Celery Beat is already running
    if pgrep -f "celery.*beat" > /dev/null; then
        print_warning "Celery Beat already running, killing existing process..."
        pkill -f "celery.*beat"
        sleep 2
    fi
    
    poetry run celery -A celery_app beat --loglevel=info --detach 2>&1 || {
        print_warning "Failed to start Celery Beat (non-critical)"
    }
    
    CELERY_BEAT_PID=$(pgrep -f "celery.*beat")
    if [ -n "$CELERY_BEAT_PID" ]; then
        print_success "Celery Beat started (PID: $CELERY_BEAT_PID)"
    fi
fi

# ============================================================================
# SAVE PIDS FOR CLEANUP
# ============================================================================

echo $CELERY_PID > "$PLATFORM_DIR/.celery_test.pid"
if [ -n "$CELERY_BEAT_PID" ]; then
    echo $CELERY_BEAT_PID > "$PLATFORM_DIR/.celery_beat_test.pid"
fi

# ============================================================================
# FINAL STATUS REPORT
# ============================================================================

print_success "Celery startup complete!"
echo ""
echo "📊 Celery Status:"
echo "  - Worker: Running (PID: $CELERY_PID) ✅"
if [ -n "$CELERY_BEAT_PID" ]; then
    echo "  - Beat: Running (PID: $CELERY_BEAT_PID) ✅"
else
    echo "  - Beat: Not started"
fi
echo ""
echo "💡 To stop Celery:"
echo "   kill $CELERY_PID"
if [ -n "$CELERY_BEAT_PID" ]; then
    echo "   kill $CELERY_BEAT_PID"
fi
echo ""
echo "💡 Using celery_app module (same as production)"
echo ""

