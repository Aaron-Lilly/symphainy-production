#!/usr/bin/env python3
"""
SymphAIny Platform - Test Runner

Comprehensive test runner aligned with Testing Strategy Overhaul Plan.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for output
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log_header(msg):
    print(f"{Colors.PURPLE}{'='*60}{Colors.NC}")
    print(f"{Colors.PURPLE}{msg}{Colors.NC}")
    print(f"{Colors.PURPLE}{'='*60}{Colors.NC}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")

def log_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")

def log_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.NC}")

def run_pytest(args_list, test_name):
    """Run pytest with given arguments."""
    log_header(f"Running {test_name}")
    
    cmd = ["pytest"] + args_list
    log_info(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        log_success(f"{test_name} passed!")
        return True
    else:
        log_error(f"{test_name} failed!")
        return False

def main():
    parser = argparse.ArgumentParser(description="SymphAIny Platform Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    parser.add_argument("--contracts", action="store_true", help="Run contract tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--marker", type=str, help="Run tests with specific marker")
    parser.add_argument("--path", type=str, help="Run tests in specific path")
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = ["-v"]
    
    if args.coverage:
        pytest_args.extend([
            "--cov=../symphainy-platform",
            "--cov-report=html",
            "--cov-report=term",
        ])
    
    # Determine test paths
    if args.unit:
        pytest_args.append("tests/unit/")
        test_name = "Unit Tests"
    elif args.integration:
        pytest_args.append("tests/integration/")
        test_name = "Integration Tests"
    elif args.e2e:
        pytest_args.append("tests/e2e/")
        test_name = "E2E Tests"
    elif args.contracts:
        pytest_args.append("tests/contracts/")
        test_name = "Contract Tests"
    elif args.fast:
        pytest_args.extend(["-m", "fast"])
        test_name = "Fast Tests"
    elif args.marker:
        pytest_args.extend(["-m", args.marker])
        test_name = f"Tests with marker '{args.marker}'"
    elif args.path:
        pytest_args.append(args.path)
        test_name = f"Tests in '{args.path}'"
    elif args.all:
        pytest_args.append("tests/")
        test_name = "All Tests"
    else:
        # Default: run all tests
        pytest_args.append("tests/")
        test_name = "All Tests"
    
    # Run tests
    start_time = datetime.now()
    success = run_pytest(pytest_args, test_name)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Summary
    print()
    if success:
        log_success(f"Test execution completed successfully in {duration:.2f} seconds")
        return 0
    else:
        log_error(f"Test execution failed after {duration:.2f} seconds")
        return 1

if __name__ == "__main__":
    sys.exit(main())




