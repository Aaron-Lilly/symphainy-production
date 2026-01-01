#!/bin/bash
# Run Supabase Migrations on Test Project
# This script runs migrations using test Supabase credentials

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
PLATFORM_DIR="$(dirname "$TESTS_DIR")/symphainy-platform"

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

# Override Supabase credentials for migration script
export SUPABASE_URL="$TEST_SUPABASE_URL"
export SUPABASE_SERVICE_KEY="$TEST_SUPABASE_SERVICE_KEY"
export SUPABASE_ANON_KEY="$TEST_SUPABASE_ANON_KEY"

if [ -n "$TEST_SUPABASE_DB_PASSWORD" ]; then
    export SUPABASE_DB_PASSWORD="$TEST_SUPABASE_DB_PASSWORD"
fi

echo "=========================================="
echo "Running Migrations on Test Supabase"
echo "=========================================="
echo ""
echo "Test Project: $TEST_SUPABASE_URL"
echo ""

# Change to platform directory
cd "$PLATFORM_DIR"

# Run migrations
python3 scripts/run_supabase_migrations.py --skip-confirm

echo ""
echo "✅ Migrations completed on test project"



