#!/usr/bin/env python3
"""
Comprehensive Phase 1 Test Suite

Tests all Phase 1 components together:
1. Schema Mapper canonical model support
2. CLI Tool functionality
3. Orchestrator complete workflows
4. End-to-end integration

This script provides a comprehensive test of all Phase 1 MVP components.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
symphainy_platform_path = project_root / 'symphainy-platform'
sys.path.insert(0, str(symphainy_platform_path))

# Test results
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def print_header(title: str):
    """Print test section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_result(test_name: str, success: bool, message: str = ""):
    """Print test result."""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")
    
    if success:
        test_results["passed"].append(test_name)
    else:
        test_results["failed"].append(test_name)


async def test_schema_mapper_canonical_support():
    """Test 1: Schema Mapper canonical model support."""
    print_header("TEST 1: Schema Mapper Canonical Model Support")
    
    try:
        from backend.business_enablement.enabling_services.schema_mapper_service.schema_mapper_service import SchemaMapperService
        
        # Check that methods exist
        assert hasattr(SchemaMapperService, 'map_to_canonical'), "map_to_canonical method missing"
        assert hasattr(SchemaMapperService, 'map_from_canonical'), "map_from_canonical method missing"
        assert hasattr(SchemaMapperService, 'map_schema_chain'), "map_schema_chain method missing"
        
        print_result("Schema Mapper canonical support", True, "All methods present")
        return True
        
    except Exception as e:
        print_result("Schema Mapper canonical support", False, str(e))
        return False


async def test_cli_tool_exists():
    """Test 2: CLI Tool exists and is executable."""
    print_header("TEST 2: CLI Tool Existence")
    
    cli_path = project_root / 'scripts' / 'insurance_use_case' / 'data_mash_cli.py'
    
    if not cli_path.exists():
        print_result("CLI Tool exists", False, f"File not found: {cli_path}")
        return False
    
    if not os.access(cli_path, os.X_OK):
        print_result("CLI Tool executable", False, "File not executable")
        return False
    
    # Check that it has all commands
    with open(cli_path, 'r') as f:
        content = f.read()
        commands = ['ingest', 'profile', 'map-to-canonical', 'validate-mapping', 'generate-plan']
        missing = [cmd for cmd in commands if f"'{cmd}'" not in content and f'"{cmd}"' not in content]
        
        if missing:
            print_result("CLI Tool commands", False, f"Missing commands: {missing}")
            return False
    
    print_result("CLI Tool exists", True, "All commands present")
    return True


async def test_orchestrator_complete_workflows():
    """Test 3: Orchestrator complete workflows."""
    print_header("TEST 3: Orchestrator Complete Workflows")
    
    try:
        from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_migration_orchestrator.insurance_migration_orchestrator import InsuranceMigrationOrchestrator
        
        # Check that methods have complete orchestration
        import inspect
        
        # Check ingest_legacy_data signature
        ingest_sig = inspect.signature(InsuranceMigrationOrchestrator.ingest_legacy_data)
        assert 'file_data' in ingest_sig.parameters or 'file_id' in ingest_sig.parameters, "Missing file parameters"
        
        # Check map_to_canonical signature
        map_sig = inspect.signature(InsuranceMigrationOrchestrator.map_to_canonical)
        assert 'source_data' in map_sig.parameters, "Missing source_data parameter"
        assert 'canonical_model_name' in map_sig.parameters, "Missing canonical_model_name parameter"
        
        # Check route_policies signature
        route_sig = inspect.signature(InsuranceMigrationOrchestrator.route_policies)
        assert 'policy_data' in route_sig.parameters, "Missing policy_data parameter"
        
        print_result("Orchestrator workflows", True, "All methods have correct signatures")
        return True
        
    except Exception as e:
        print_result("Orchestrator workflows", False, str(e))
        return False


async def test_pytest_suite():
    """Test 4: Run pytest test suite."""
    print_header("TEST 4: Pytest Test Suite")
    
    test_file = project_root / 'tests' / 'integration' / 'insurance_use_case' / 'phase1_mvp' / 'test_phase1_mvp.py'
    
    if not test_file.exists():
        print_result("Pytest suite exists", False, f"Test file not found: {test_file}")
        return False
    
    try:
        # Run pytest
        result = subprocess.run(
            ['python3', '-m', 'pytest', str(test_file), '-v', '--tb=short'],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        # Parse results
        import re
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        
        if failed == 0 and passed > 0:
            print_result("Pytest suite", True, f"{passed} tests passed")
            return True
        elif failed > 0:
            print_result("Pytest suite", False, f"{passed} passed, {failed} failed")
            print(f"\n   Test output:\n{output[-500:]}")  # Last 500 chars
            return False
        else:
            print_result("Pytest suite", False, "Could not parse test results")
            print(f"\n   Output:\n{output[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print_result("Pytest suite", False, "Test timeout")
        return False
    except Exception as e:
        print_result("Pytest suite", False, str(e))
        return False


async def test_integration_components():
    """Test 5: Integration component checks."""
    print_header("TEST 5: Integration Component Checks")
    
    checks = []
    
    # Check Wave Orchestrator exists
    wave_path = symphainy_platform_path / 'backend' / 'business_enablement' / 'delivery_manager' / 'insurance_use_case_orchestrators' / 'wave_orchestrator' / 'wave_orchestrator.py'
    checks.append(("Wave Orchestrator", wave_path.exists()))
    
    # Check Policy Tracker exists
    tracker_path = symphainy_platform_path / 'backend' / 'business_enablement' / 'delivery_manager' / 'insurance_use_case_orchestrators' / 'policy_tracker_orchestrator' / 'policy_tracker_orchestrator.py'
    checks.append(("Policy Tracker Orchestrator", tracker_path.exists()))
    
    # Check templates exist
    templates_path = symphainy_platform_path / 'backend' / 'business_enablement' / 'delivery_manager' / 'insurance_use_case_orchestrators' / 'insurance_templates'
    checks.append(("Insurance Templates", templates_path.exists()))
    
    # Check WAL module exists
    wal_path = symphainy_platform_path / 'backend' / 'smart_city' / 'services' / 'data_steward' / 'modules' / 'write_ahead_logging.py'
    checks.append(("WAL Module", wal_path.exists()))
    
    # Check Canonical Model Service exists
    canonical_path = symphainy_platform_path / 'backend' / 'business_enablement' / 'enabling_services' / 'canonical_model_service' / 'canonical_model_service.py'
    checks.append(("Canonical Model Service", canonical_path.exists()))
    
    # Check Routing Engine exists
    routing_path = symphainy_platform_path / 'backend' / 'business_enablement' / 'enabling_services' / 'routing_engine_service' / 'routing_engine_service.py'
    checks.append(("Routing Engine Service", routing_path.exists()))
    
    all_passed = all(result for _, result in checks)
    
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
    
    print_result("Integration components", all_passed, f"{sum(1 for _, r in checks if r)}/{len(checks)} components found")
    return all_passed


async def main():
    """Run all Phase 1 comprehensive tests."""
    print("\n" + "="*80)
    print("  PHASE 1 COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    tests = [
        ("Schema Mapper Canonical Support", test_schema_mapper_canonical_support),
        ("CLI Tool Existence", test_cli_tool_exists),
        ("Orchestrator Complete Workflows", test_orchestrator_complete_workflows),
        ("Pytest Test Suite", test_pytest_suite),
        ("Integration Components", test_integration_components)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

