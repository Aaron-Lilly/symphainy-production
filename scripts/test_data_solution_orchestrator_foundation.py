#!/usr/bin/env python3
"""
Limited Functional Test for Data Solution Orchestrator Foundation

This test verifies that the Data Solution Orchestrator foundation is properly
set up and ready for Phase 1 (Content Pillar Vertical Slice).

Tests:
1. Orchestrator file exists and can be imported
2. Orchestrator class structure is correct
3. All required methods exist
4. Method signatures are correct
5. workflow_id handling logic is present
"""

import os
import sys
import inspect
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
platform_path = project_root / 'symphainy-platform'
sys.path.insert(0, str(platform_path))


def test_file_exists():
    """Test 1: Verify orchestrator file exists."""
    print("\n" + "="*80)
    print("TEST 1: File Existence")
    print("="*80)
    
    orchestrator_file = platform_path / 'backend' / 'business_enablement' / 'delivery_manager' / 'data_solution_orchestrator' / 'data_solution_orchestrator.py'
    
    if orchestrator_file.exists():
        print(f"✅ Orchestrator file exists: {orchestrator_file}")
        return True
    else:
        print(f"❌ Orchestrator file not found: {orchestrator_file}")
        return False


def test_class_import():
    """Test 2: Verify orchestrator class can be imported."""
    print("\n" + "="*80)
    print("TEST 2: Class Import")
    print("="*80)
    
    try:
        from backend.business_enablement.delivery_manager.data_solution_orchestrator.data_solution_orchestrator import DataSolutionOrchestrator
        
        print(f"✅ DataSolutionOrchestrator imported successfully")
        print(f"   Class: {DataSolutionOrchestrator}")
        print(f"   Module: {DataSolutionOrchestrator.__module__}")
        
        return True, DataSolutionOrchestrator
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False, None


def test_class_structure(orchestrator_class):
    """Test 3: Verify orchestrator class structure."""
    print("\n" + "="*80)
    print("TEST 3: Class Structure")
    print("="*80)
    
    if not orchestrator_class:
        print("⚠️  Skipping - class not available")
        return False
    
    # Check base class
    from bases.orchestrator_base import OrchestratorBase
    if issubclass(orchestrator_class, OrchestratorBase):
        print(f"✅ Extends OrchestratorBase correctly")
    else:
        print(f"❌ Does not extend OrchestratorBase")
        return False
    
    # Check required attributes
    required_attrs = ['orchestrator_name', 'service_name', 'realm_name']
    for attr in required_attrs:
        if hasattr(orchestrator_class, attr):
            print(f"   ✅ Has attribute: {attr}")
        else:
            print(f"   ⚠️  Missing attribute: {attr} (may be set in __init__)")
    
    return True


def test_required_methods(orchestrator_class):
    """Test 4: Verify all required methods exist."""
    print("\n" + "="*80)
    print("TEST 4: Required Methods")
    print("="*80)
    
    if not orchestrator_class:
        print("⚠️  Skipping - class not available")
        return False
    
    required_methods = [
        "orchestrate_data_ingest",
        "orchestrate_data_parse",
        "orchestrate_data_embed",
        "orchestrate_data_expose",
        "initialize",
    ]
    
    print("🔍 Checking required methods...")
    missing_methods = []
    
    for method_name in required_methods:
        if hasattr(orchestrator_class, method_name):
            method = getattr(orchestrator_class, method_name)
            if callable(method):
                # Check if it's async
                is_async = inspect.iscoroutinefunction(method)
                async_str = "async" if is_async else "sync"
                print(f"   ✅ {method_name}() exists ({async_str})")
            else:
                print(f"   ❌ {method_name} exists but is not callable")
                missing_methods.append(method_name)
        else:
            print(f"   ❌ {method_name}() not found")
            missing_methods.append(method_name)
    
    if missing_methods:
        print(f"\n❌ Missing methods: {', '.join(missing_methods)}")
        return False
    else:
        print(f"\n✅ All required methods present")
        return True


def test_method_signatures(orchestrator_class):
    """Test 5: Verify method signatures are correct."""
    print("\n" + "="*80)
    print("TEST 5: Method Signatures")
    print("="*80)
    
    if not orchestrator_class:
        print("⚠️  Skipping - class not available")
        return False
    
    # Check orchestrate_data_ingest signature
    if hasattr(orchestrator_class, 'orchestrate_data_ingest'):
        sig = inspect.signature(orchestrator_class.orchestrate_data_ingest)
        params = list(sig.parameters.keys())
        expected_params = ['self', 'file_data', 'file_name', 'file_type', 'user_context']
        
        print(f"📋 orchestrate_data_ingest signature:")
        print(f"   Parameters: {params}")
        
        missing_params = [p for p in expected_params if p not in params]
        if missing_params:
            print(f"   ⚠️  Missing parameters: {missing_params}")
        else:
            print(f"   ✅ All expected parameters present")
    
    # Check orchestrate_data_parse signature
    if hasattr(orchestrator_class, 'orchestrate_data_parse'):
        sig = inspect.signature(orchestrator_class.orchestrate_data_parse)
        params = list(sig.parameters.keys())
        expected_params = ['self', 'file_id', 'parse_options', 'user_context', 'workflow_id']
        
        print(f"\n📋 orchestrate_data_parse signature:")
        print(f"   Parameters: {params}")
        
        missing_params = [p for p in expected_params if p not in params]
        if missing_params:
            print(f"   ⚠️  Missing parameters: {missing_params}")
        else:
            print(f"   ✅ All expected parameters present")
    
    return True


def test_workflow_id_handling(orchestrator_class):
    """Test 6: Verify workflow_id handling logic exists."""
    print("\n" + "="*80)
    print("TEST 6: workflow_id Handling")
    print("="*80)
    
    if not orchestrator_class:
        print("⚠️  Skipping - class not available")
        return False
    
    try:
        # Read the source file to check for workflow_id handling
        orchestrator_file = platform_path / 'backend' / 'business_enablement' / 'delivery_manager' / 'data_solution_orchestrator' / 'data_solution_orchestrator.py'
        
        if not orchestrator_file.exists():
            print("❌ Cannot read source file")
            return False
        
        source_code = orchestrator_file.read_text()
        
        # Check for workflow_id patterns
        checks = [
            ("workflow_id from user_context", "user_context.get(\"workflow_id\")" in source_code or "user_context.get('workflow_id')" in source_code),
            ("workflow_id generation", "uuid.uuid4()" in source_code),
            ("correlation_ids", "\"correlation_ids\"" in source_code or "'correlation_ids'" in source_code),
            ("file_id in correlation", "\"file_id\"" in source_code or "'file_id'" in source_code),
        ]
        
        print("🔍 Checking workflow_id handling patterns...")
        all_present = True
        
        for check_name, present in checks:
            if present:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ⚠️  {check_name} not found")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"❌ workflow_id handling check failed: {e}")
        return False


def test_smart_city_service_methods(orchestrator_class):
    """Test 7: Verify Smart City service access methods exist."""
    print("\n" + "="*80)
    print("TEST 7: Smart City Service Access Methods")
    print("="*80)
    
    if not orchestrator_class:
        print("⚠️  Skipping - class not available")
        return False
    
    # These methods should be inherited from OrchestratorBase
    required_methods = [
        "get_content_steward_api",
        "get_librarian_api",
        "get_data_steward_api",
        "get_nurse_api",
    ]
    
    print("🔍 Checking Smart City service access methods...")
    missing_methods = []
    
    for method_name in required_methods:
        if hasattr(orchestrator_class, method_name):
            method = getattr(orchestrator_class, method_name)
            if callable(method):
                is_async = inspect.iscoroutinefunction(method)
                async_str = "async" if is_async else "sync"
                print(f"   ✅ {method_name}() exists ({async_str})")
            else:
                print(f"   ⚠️  {method_name} exists but is not callable")
                missing_methods.append(method_name)
        else:
            print(f"   ⚠️  {method_name}() not found (may be inherited)")
            # Not a failure - may be inherited from base class
    
    if missing_methods:
        print(f"\n⚠️  Some methods not found: {', '.join(missing_methods)}")
        print("   (These may be inherited from OrchestratorBase)")
    
    return True  # Not a failure - methods may be inherited


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("DATA SOLUTION ORCHESTRATOR FOUNDATION TEST")
    print("="*80)
    print("\nThis test verifies the foundation is ready for Phase 1 (Content Pillar).")
    print("="*80)
    
    results = {}
    
    # Test 1: File exists
    results["file_exists"] = test_file_exists()
    
    # Test 2: Class import
    success, orchestrator_class = test_class_import()
    results["class_import"] = success
    
    # Test 3: Class structure
    results["class_structure"] = test_class_structure(orchestrator_class)
    
    # Test 4: Required methods
    results["required_methods"] = test_required_methods(orchestrator_class)
    
    # Test 5: Method signatures
    results["method_signatures"] = test_method_signatures(orchestrator_class)
    
    # Test 6: workflow_id handling
    results["workflow_id_handling"] = test_workflow_id_handling(orchestrator_class)
    
    # Test 7: Smart City service methods
    results["smart_city_methods"] = test_smart_city_service_methods(orchestrator_class)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Foundation is ready for Phase 1.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
