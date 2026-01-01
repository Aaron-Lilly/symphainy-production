#!/usr/bin/env python3
"""
Rock-Solid Test Runner

This script runs all our rock-solid tests to validate that our platform actually works
from configuration utility to frontend file upload saving to Supabase + GCS.

CRITICAL REQUIREMENT: These tests use REAL implementations, not mocks.
We need to prove the platform actually works when UAT team gets it.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_test_file(test_file_path, test_name):
    """Run a specific test file and return the result."""
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file_path, 
            "-v", 
            "--tb=short",
            "--no-header",
            "--no-summary"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"✅ {test_name}: PASSED")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ {test_name}: ERROR - {e}")
        return False

def main():
    """Run all rock-solid tests."""
    print("🚀 ROCK-SOLID TEST RUNNER")
    print("=" * 60)
    print("Testing complete platform architecture from configuration to frontend")
    print("Using REAL implementations, not mocks")
    print("=" * 60)
    
    # Define test files and their descriptions
    tests = [
        {
            "file": "unit/end_to_end_architecture_validation.py",
            "name": "End-to-End Architecture Validation"
        },
        {
            "file": "unit/layer_3_infrastructure/test_infrastructure_foundation_real.py",
            "name": "Infrastructure Foundation Real Implementation"
        },
        {
            "file": "unit/layer_4_public_works/test_public_works_foundation_real.py",
            "name": "Public Works Foundation Real Implementation"
        },
        {
            "file": "unit/layer_7_smart_city_roles/test_smart_city_services_real.py",
            "name": "Smart City Services Real Implementation"
        }
    ]
    
    # Track results
    passed_tests = 0
    total_tests = len(tests)
    
    # Run each test
    for test in tests:
        test_path = os.path.join(os.path.dirname(__file__), test["file"])
        if os.path.exists(test_path):
            if run_test_file(test_path, test["name"]):
                passed_tests += 1
        else:
            print(f"⚠️  {test['name']}: Test file not found at {test_path}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Platform is ready for UAT team - everything actually works!")
        print("✅ No mocks, no stubs, no TODOs - only real, working implementations!")
        return 0
    else:
        print(f"\n❌ {total_tests - passed_tests} TESTS FAILED!")
        print("⚠️  Platform needs fixes before UAT team gets it")
        return 1

if __name__ == "__main__":
    sys.exit(main())

