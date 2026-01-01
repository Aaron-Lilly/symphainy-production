#!/usr/bin/env python3
"""
SymphAIny Platform - Test Runner

Comprehensive test runner for the new architecture.
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

# Layer definitions for bottom-up testing
LAYERS = {
    0: {
        "name": "Infrastructure Adapters",
        "marker": "infrastructure",
        "path": "unit/infrastructure_adapters",
        "description": "Test adapters in isolation"
    },
    1: {
        "name": "Foundations",
        "marker": "foundations",
        "path": "unit/foundations",
        "description": "Test foundation services in isolation"
    },
    2: {
        "name": "Smart City Services",
        "marker": "smart_city",
        "path": "unit/smart_city",
        "description": "Test Smart City services in isolation"
    },
    3: {
        "name": "Enabling Services",
        "marker": "enabling_services",
        "path": "unit/enabling_services",
        "description": "Test enabling services in isolation"
    },
    4: {
        "name": "Orchestrators",
        "marker": "orchestrators",
        "path": "unit/orchestrators",
        "description": "Test orchestrators in isolation"
    },
    5: {
        "name": "MCP Servers",
        "marker": "mcp",
        "path": "unit/mcp_servers",
        "description": "Test MCP servers in isolation"
    },
    6: {
        "name": "Agents",
        "marker": "agents",
        "path": "unit/agents",
        "description": "Test agents in isolation"
    },
    7: {
        "name": "Integration",
        "marker": "integration",
        "path": "integration",
        "description": "Test multiple components together"
    },
    8: {
        "name": "End-to-End",
        "marker": "e2e",
        "path": "e2e",
        "description": "Test full system"
    },
}

def run_layer(layer_num: int, pytest_args: list) -> bool:
    """Run tests for a specific layer."""
    if layer_num not in LAYERS:
        log_error(f"Invalid layer number: {layer_num}")
        return False
    
    layer = LAYERS[layer_num]
    log_header(f"Layer {layer_num}: {layer['name']}")
    log_info(layer['description'])
    
    # Build pytest args for this layer
    layer_args = pytest_args + ["-m", layer['marker']]
    
    # Also try path-based if marker doesn't work
    layer_path = f"tests/{layer['path']}"
    if Path(layer_path).exists():
        layer_args.append(layer_path)
    
    return run_pytest(layer_args, layer['name'])

def main():
    parser = argparse.ArgumentParser(description="SymphAIny Platform Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--foundations", action="store_true", help="Run foundation layer tests only")
    parser.add_argument("--smart-city", action="store_true", help="Run Smart City service tests only")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--slow", action="store_true", help="Run slow tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--layer", type=int, help="Run specific layer (0-8)")
    parser.add_argument("--layers", type=str, help="Run range of layers (e.g., '0-6' or '0,1,2')")
    parser.add_argument("--validate", action="store_true", help="Validate production code before testing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--failed", action="store_true", help="Run only failed tests from last run")
    parser.add_argument("--markers", action="store_true", help="List all test markers")
    args = parser.parse_args()
    
    # Change to tests directory
    os.chdir(Path(__file__).parent)
    
    log_header("SymphAIny Platform Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Validate production code if requested
    if args.validate:
        log_header("Validating Production Code")
        validate_script = Path(__file__).parent / "scripts" / "validate_production_code.py"
        if validate_script.exists():
            result = subprocess.run([sys.executable, str(validate_script)], cwd=Path(__file__).parent.parent)
            if result.returncode != 0:
                log_error("Production code validation failed! Fix violations before running tests.")
                return 1
            log_success("Production code validation passed!")
        else:
            log_warning(f"Validation script not found: {validate_script}")
    
    # List markers if requested
    if args.markers:
        run_pytest(["--markers"], "List Available Markers")
        return
    
    # Build pytest arguments
    pytest_args = ["-v"] if args.verbose else []
    
    if args.coverage:
        pytest_args.extend(["--cov=symphainy-platform", "--cov-report=html", "--cov-report=term"])
    
    if args.failed:
        pytest_args.append("--lf")  # Last failed
    
    # Run specific test categories
    results = []
    
    # Layer-by-layer execution
    if args.layer is not None:
        results.append(run_layer(args.layer, pytest_args))
    
    elif args.layers:
        # Parse layer range (e.g., "0-6" or "0,1,2")
        layer_nums = []
        if '-' in args.layers:
            start, end = map(int, args.layers.split('-'))
            layer_nums = list(range(start, end + 1))
        elif ',' in args.layers:
            layer_nums = [int(x.strip()) for x in args.layers.split(',')]
        else:
            layer_nums = [int(args.layers)]
        
        log_header(f"Running Layers: {', '.join(map(str, layer_nums))}")
        for layer_num in layer_nums:
            if not run_layer(layer_num, pytest_args):
                log_error(f"Layer {layer_num} failed! Stopping.")
                break
            results.append(True)
    
    if args.fast:
        results.append(run_pytest(pytest_args + ["-m", "fast"], "Fast Tests"))
    
    elif args.slow:
        results.append(run_pytest(pytest_args + ["-m", "slow"], "Slow Tests"))
    
    elif args.unit:
        results.append(run_pytest(pytest_args + ["-m", "unit"], "Unit Tests"))
    
    elif args.integration:
        results.append(run_pytest(pytest_args + ["-m", "integration"], "Integration Tests"))
    
    elif args.e2e:
        results.append(run_pytest(pytest_args + ["-m", "e2e"], "End-to-End Tests"))
    
    elif args.foundations:
        results.append(run_pytest(pytest_args + ["-m", "foundations"], "Foundation Layer Tests"))
    
    elif args.smart_city:
        results.append(run_pytest(pytest_args + ["-m", "smart_city"], "Smart City Service Tests"))
    
    elif args.all:
        log_header("Running Complete Test Suite (Bottom-Up)")
        log_info("Running all layers in order (0-8)")
        
        # Run all layers in order (bottom-up)
        for layer_num in sorted(LAYERS.keys()):
            if not run_layer(layer_num, pytest_args):
                log_error(f"Layer {layer_num} failed! Stopping.")
                break
            results.append(True)
    
    else:
        # Default: Run unit tests only
        log_warning("No test category specified, running unit tests only")
        log_info("Use --all to run complete test suite")
        results.append(run_pytest(pytest_args + ["-m", "unit"], "Unit Tests"))
    
    # Print summary
    print("\n")
    log_header("Test Summary")
    
    if results:
        passed = sum(1 for r in results if r)
        failed = sum(1 for r in results if not r)
        
        print(f"Total test runs: {len(results)}")
        print(f"Passed: {Colors.GREEN}{passed}{Colors.NC}")
        print(f"Failed: {Colors.RED}{failed}{Colors.NC}")
        
        if failed == 0:
            log_success("All test runs passed! 🎉")
            return 0
        else:
            log_error(f"{failed} test run(s) failed")
            return 1
    else:
        log_warning("No tests run")
        return 0

if __name__ == "__main__":
    sys.exit(main())













