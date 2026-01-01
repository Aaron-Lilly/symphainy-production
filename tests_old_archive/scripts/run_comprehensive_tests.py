#!/usr/bin/env python3
"""
SymphAIny Platform - Comprehensive Test Execution Script

This script runs the comprehensive test suite for the new architecture.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_test_category(category: str, description: str):
    """Run a specific test category."""
    print(f"\n🧪 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            'python3', '-m', 'pytest', f'{category}/', '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            print(f"   Tests run: {result.stdout.count('PASSED')}")
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run comprehensive test suite."""
    print("🎉 SYMPHAINY PLATFORM - COMPREHENSIVE TEST EXECUTION")
    print("=" * 60)
    print("Testing the new architecture with comprehensive test suite...")
    print()
    
    # Test categories
    test_categories = [
        ("unit", "Unit Tests - Foundation Services"),
        ("integration", "Integration Tests - Cross-Realm Communication"),
        ("e2e", "End-to-End Tests - MVP Journey Scenarios"),
        ("chaos", "Chaos Tests - System Resilience"),
        ("uat", "C-Suite UAT Tests - Executive Scenarios"),
        ("performance", "Performance Tests - Load and Scalability"),
        ("security", "Security Tests - Zero-Trust Validation")
    ]
    
    results = {}
    
    for category, description in test_categories:
        success = run_test_category(category, description)
        results[category] = success
    
    # Summary
    print("\n📊 TEST EXECUTION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for category, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {category:15} - {status}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} test categories passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Platform is ready for production!")
        return 0
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())