#!/usr/bin/env python3
"""
Combined Test Script for Phase 1 and Phase 2

Tests both Phase 1 (Security Integration) and Phase 2 (Client Config Foundation).

WHAT: Validates both Phase 1 and Phase 2 implementations
HOW: Runs test suites for both phases sequentially
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test modules
try:
    from scripts.test_phase1_security_integration import Phase1SecurityTester
    from scripts.test_phase2_client_config import Phase2ClientConfigTester
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure test scripts are in the scripts directory")
    sys.exit(1)


class CombinedPhaseTester:
    """Test both Phase 1 and Phase 2."""
    
    def __init__(self):
        self.phase1_tester = Phase1SecurityTester()
        self.phase2_tester = Phase2ClientConfigTester()
        self.all_results = []
    
    async def run_all_tests(self, token: str = None):
        """Run all tests for Phase 1 and Phase 2."""
        print("=" * 70)
        print("Combined Test Suite: Phase 1 & Phase 2")
        print("=" * 70)
        
        # Phase 1 Tests
        print("\n" + "=" * 70)
        print("PHASE 1: Security Integration Tests")
        print("=" * 70)
        
        phase1_results = await self.phase1_tester.run_all_tests(token)
        self.all_results.append({
            "phase": "Phase 1: Security Integration",
            "results": phase1_results
        })
        
        # Phase 2 Tests
        print("\n" + "=" * 70)
        print("PHASE 2: Client Config Foundation Tests")
        print("=" * 70)
        
        phase2_results = await self.phase2_tester.run_all_tests()
        self.all_results.append({
            "phase": "Phase 2: Client Config Foundation",
            "results": phase2_results
        })
        
        # Overall Summary
        print("\n" + "=" * 70)
        print("Overall Test Summary")
        print("=" * 70)
        
        total_tests = phase1_results["total"] + phase2_results["total"]
        total_passed = phase1_results["passed"] + phase2_results["passed"]
        total_failed = phase1_results["failed"] + phase2_results["failed"]
        
        print(f"\nPhase 1: {phase1_results['passed']}/{phase1_results['total']} tests passed")
        print(f"Phase 2: {phase2_results['passed']}/{phase2_results['total']} tests passed")
        print(f"\nOverall: {total_passed}/{total_tests} tests passed ({total_failed} failed)")
        
        if total_passed == total_tests:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {total_failed} test(s) failed")
        
        return {
            "phase1": phase1_results,
            "phase2": phase2_results,
            "overall": {
                "total": total_tests,
                "passed": total_passed,
                "failed": total_failed
            }
        }


async def main():
    """Main test execution."""
    tester = CombinedPhaseTester()
    
    # Get token from environment (optional for Phase 1)
    # Phase1SecurityTester will try to get test token from Supabase if not provided
    token = os.getenv("SYMPHAINY_API_TOKEN")
    
    if not token:
        print("⚠️  No SYMPHAINY_API_TOKEN provided")
        print("   Phase 1 tester will attempt to get test token from Supabase")
        print("   Configure test Supabase:")
        print("   export TEST_SUPABASE_URL='https://your-test-project.supabase.co'")
        print("   export TEST_SUPABASE_ANON_KEY='your-test-anon-key'")
        print("   export TEST_SUPABASE_EMAIL='test@symphainy.com'")
        print("   export TEST_SUPABASE_PASSWORD='test_password'")
        print()
    
    results = await tester.run_all_tests(token)
    
    # Exit with appropriate code
    overall_failed = results["overall"]["failed"]
    sys.exit(0 if overall_failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())

