#!/bin/bash
# Safe Test Runner - Wraps pytest with safety checks and timeouts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run pre-test validation
echo "Running pre-test validation..."
"$SCRIPT_DIR/pre_test_validation.sh" || {
    echo "Pre-test validation failed. Fix issues before running tests."
    exit 1
}

# Set maximum test execution time (10 minutes)
MAX_TEST_TIME=600

# Run tests with timeout
echo "Running tests with ${MAX_TEST_TIME}s timeout..."
timeout $MAX_TEST_TIME pytest "$@" || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "ERROR: Tests timed out after $MAX_TEST_TIME seconds"
        echo "This may indicate hanging tests or infrastructure issues"
        echo "Check for hanging processes: ps aux | grep pytest"
    fi
    exit $exit_code
}

