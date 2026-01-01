#!/bin/bash
# Quick script to run all new tests (complete bottom-up test suite)

cd "$(dirname "$0")/.." || exit 1

echo "Running complete new test suite (bottom-up strategy)..."
echo ""

python3 tests/run_complete_new_test_suite.py

