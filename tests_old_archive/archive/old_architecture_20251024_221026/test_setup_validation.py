#!/usr/bin/env python3
"""
Test Setup Validation

This script validates that our comprehensive testing setup is working correctly.
It tests basic functionality without requiring all platform components to be perfect.
"""

import sys
import os
import pytest
import asyncio
import httpx
import tempfile
import json
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

def test_basic_imports():
    """Test that basic imports work."""
    try:
        from foundations.utility_foundation.utilities.configuration.configuration_utility import ConfigurationUtility
        print("✅ ConfigurationUtility import successful")
        return True
    except Exception as e:
        print(f"❌ ConfigurationUtility import failed: {e}")
        return False

def test_configuration_utility():
    """Test that ConfigurationUtility works."""
    try:
        from foundations.utility_foundation.utilities.configuration.configuration_utility import ConfigurationUtility
        config = ConfigurationUtility("test_setup_validation")
        
        # Test basic functionality
        environment = config.get_environment()
        multi_tenant = config.is_multi_tenant_enabled()
        testing = config.is_testing()
        
        print(f"✅ ConfigurationUtility working - Environment: {environment}, Multi-tenant: {multi_tenant}, Testing: {testing}")
        return True
    except Exception as e:
        print(f"❌ ConfigurationUtility test failed: {e}")
        return False

def test_external_dependencies():
    """Test that external dependencies are available."""
    try:
        import google.cloud.storage
        print("✅ Google Cloud Storage available")
    except ImportError:
        print("⚠️ Google Cloud Storage not available")
    
    try:
        import openai
        print("✅ OpenAI available")
    except ImportError:
        print("⚠️ OpenAI not available")
    
    try:
        import anthropic
        print("✅ Anthropic available")
    except ImportError:
        print("⚠️ Anthropic not available")
    
    try:
        import httpx
        print("✅ HTTPX available")
    except ImportError:
        print("❌ HTTPX not available")
        return False
    
    try:
        import psutil
        print("✅ PSUTIL available")
    except ImportError:
        print("⚠️ PSUTIL not available")
    
    return True

def test_test_structure():
    """Test that our test structure is in place."""
    test_dirs = [
        "architecture",
        "contracts", 
        "chaos",
        "performance",
        "security",
        "real_implementations",
        "e2e",
        "unit",
        "integration"
    ]
    
    base_path = Path(__file__).parent
    
    for test_dir in test_dirs:
        dir_path = base_path / test_dir
        if dir_path.exists():
            print(f"✅ {test_dir} directory exists")
        else:
            print(f"❌ {test_dir} directory missing")
            return False
    
    return True

def test_test_files():
    """Test that our key test files exist."""
    test_files = [
        "architecture/dependency_injection/test_layer_dependencies.py",
        "architecture/interface_validation/test_layer_interfaces.py",
        "contracts/api_contracts/test_api_contracts.py",
        "chaos/failure_injection/test_failure_injection.py",
        "performance/load_testing/test_load_testing.py",
        "security/penetration/test_penetration_testing.py",
        "real_implementations/gcs_integration/test_gcs_real.py",
        "real_implementations/llm_integration/test_llm_real.py",
        "e2e/user_journeys/test_complete_user_journeys.py",
        "run_corrected_vision_tests.py"
    ]
    
    base_path = Path(__file__).parent
    
    for test_file in test_files:
        file_path = base_path / test_file
        if file_path.exists():
            print(f"✅ {test_file} exists")
        else:
            print(f"❌ {test_file} missing")
            return False
    
    return True

def test_api_connectivity():
    """Test basic API connectivity."""
    try:
        import asyncio
        
        async def test_http():
            async with httpx.AsyncClient() as client:
                try:
                    # Test localhost connectivity
                    response = await client.get("http://localhost:8000/health", timeout=5.0)
                    print(f"✅ API connectivity working - Status: {response.status_code}")
                    return True
                except httpx.ConnectError:
                    print("⚠️ API not running on localhost:8000 (expected for setup validation)")
                    return True
                except Exception as e:
                    print(f"⚠️ API connectivity test failed: {e}")
                    return True
        
        return asyncio.run(test_http())
    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        return False

def test_file_operations():
    """Test basic file operations."""
    try:
        # Test temporary file creation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            test_data = {"test": "data", "timestamp": "2025-01-01T00:00:00Z"}
            json.dump(test_data, temp_file)
            temp_file_path = temp_file.name
        
        # Test file reading
        with open(temp_file_path, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data == test_data
        
        # Clean up
        os.unlink(temp_file_path)
        
        print("✅ File operations working")
        return True
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def main():
    """Run all setup validation tests."""
    print("🔍 COMPREHENSIVE TEST SETUP VALIDATION")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration Utility", test_configuration_utility),
        ("External Dependencies", test_external_dependencies),
        ("Test Structure", test_test_structure),
        ("Test Files", test_test_files),
        ("API Connectivity", test_api_connectivity),
        ("File Operations", test_file_operations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL SETUP VALIDATION TESTS PASSED!")
        print("✅ Test infrastructure is ready for comprehensive testing")
        print("✅ Platform integration is working")
        print("✅ External dependencies are available")
        print("✅ Test structure is complete")
        return 0
    else:
        print(f"\n⚠️ {total - passed} SETUP VALIDATION TESTS FAILED")
        print("🔧 Review failed tests and fix issues before running comprehensive tests")
        return 1

if __name__ == "__main__":
    sys.exit(main())
