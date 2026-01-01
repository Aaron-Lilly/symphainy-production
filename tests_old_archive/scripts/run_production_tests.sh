#!/bin/bash
# Run Production Tests with Test Supabase
# This script runs tests using test Supabase credentials

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$TESTS_DIR")"

# Load test environment
ENV_TEST_FILE="$TESTS_DIR/.env.test"
if [ ! -f "$ENV_TEST_FILE" ]; then
    echo "❌ .env.test file not found"
    echo "   Run: ./tests/scripts/setup_test_supabase.sh"
    exit 1
fi

# Export test environment variables
export TEST_MODE=true
source "$ENV_TEST_FILE"

# Override Supabase credentials for backend (if backend is running)
export SUPABASE_URL="$TEST_SUPABASE_URL"
export SUPABASE_SERVICE_KEY="$TEST_SUPABASE_SERVICE_KEY"
export SUPABASE_ANON_KEY="$TEST_SUPABASE_ANON_KEY"

echo "=========================================="
echo "Running Production Tests with Test Supabase"
echo "=========================================="
echo ""
echo "Test Project: $TEST_SUPABASE_URL"
echo "Backend URL: $TEST_BACKEND_URL"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Run tests
pytest tests/e2e/production/ -v "$@"

echo ""
echo "✅ Tests completed"



