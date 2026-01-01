#!/bin/bash
# Quick Test Runner - Self-Service Testing (No Cursor Agent Needed)
# Usage: ./quick_test.sh [test_path]

set -e

cd "$(dirname "$0")"

if [ -z "$1" ]; then
    # No argument: Run fast tests
    echo "🚀 Running fast tests (< 30 seconds)..."
    python3 run_tests.py --fast
elif [ "$1" == "--unit" ]; then
    # Unit tests
    echo "🚀 Running unit tests (< 2 minutes)..."
    python3 run_tests.py --unit
elif [ "$1" == "--failed" ]; then
    # Last failed
    echo "🚀 Running last failed tests..."
    pytest --lf -v
elif [ -f "$1" ]; then
    # Specific test file
    echo "🚀 Running test: $1"
    pytest "$1" -v
else
    # Test path pattern
    echo "🚀 Running tests matching: $1"
    pytest "$1" -v
fi

echo ""
echo "✅ Test execution complete!"
echo "💡 Tip: Read errors above - they usually tell you what's wrong"
echo "💡 Tip: Run 'pytest --lf' to rerun only failed tests"
