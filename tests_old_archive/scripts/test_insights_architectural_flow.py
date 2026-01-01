#!/usr/bin/env python3
"""
Test Runner Script for Insights Pillar Architectural Flow

Runs all tests to verify the new Solution → Journey → Realm Services architecture.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_tests(test_type: str = "all", verbose: bool = False):
    """
    Run tests for Insights Pillar architectural flow.
    
    Args:
        test_type: Type of tests to run (unit, integration, e2e, all)
        verbose: Enable verbose output
    """
    base_path = project_root / "symphainy_source" / "tests"
    
    test_files = {
        "unit": [
            "unit/solution/test_insights_solution_orchestrator_analysis.py",
            "unit/journey/test_insights_journey_orchestrator_analysis.py"
        ],
        "integration": [
            "integration/insights/test_insights_architectural_flow.py"
        ],
        "e2e": [
            "e2e/insights/test_insights_architectural_e2e.py"
        ]
    }
    
    if test_type == "all":
        test_paths = []
        for paths in test_files.values():
            test_paths.extend(paths)
    else:
        test_paths = test_files.get(test_type, [])
    
    if not test_paths:
        print(f"❌ No tests found for type: {test_type}")
        return False
    
    # Build pytest command
    cmd = ["python3", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add test paths
    for test_path in test_paths:
        full_path = base_path / test_path
        if full_path.exists():
            cmd.append(str(full_path))
        else:
            print(f"⚠️  Test file not found: {full_path}")
    
    # Add markers
    cmd.extend([
        "-m", "insights",
        "--tb=short",
        "--color=yes"
    ])
    
    print(f"🚀 Running {test_type} tests for Insights Pillar Architectural Flow...")
    print(f"📝 Command: {' '.join(cmd)}")
    print()
    
    # Run tests
    result = subprocess.run(cmd, cwd=project_root)
    
    return result.returncode == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test runner for Insights Pillar Architectural Flow"
    )
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    success = run_tests(test_type=args.type, verbose=args.verbose)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()










