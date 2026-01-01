#!/usr/bin/env python3
"""
Test Unified Configuration Manager

Test the basic functionality of the UnifiedConfigurationManager
and DIContainerService integration.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the platform to the Python path
sys.path.insert(0, str(Path(__file__).parent / "symphainy-platform"))
sys.path.insert(0, str(Path(__file__).parent))

def test_unified_configuration_manager():
    """Test UnifiedConfigurationManager basic functionality."""
    print("🧪 Testing UnifiedConfigurationManager...")
    
    try:
        from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
        
        # Test basic initialization
        config = UnifiedConfigurationManager(service_name="test_service")
        print("✅ UnifiedConfigurationManager initialized successfully")
        
        # Test basic configuration access
        env = config.get_environment()
        print(f"✅ Environment detected: {env}")
        
        # Test configuration methods
        api_port = config.get_int("API_PORT", 8000)
        print(f"✅ API Port: {api_port}")
        
        debug_mode = config.get_bool("API_DEBUG", False)
        print(f"✅ Debug Mode: {debug_mode}")
        
        # Test specialized configuration
        db_config = config.get_database_config()
        print(f"✅ Database config loaded: {len(db_config)} settings")
        
        redis_config = config.get_redis_config()
        print(f"✅ Redis config loaded: {len(redis_config)} settings")
        
        llm_config = config.get_llm_config()
        print(f"✅ LLM config loaded: {len(llm_config)} settings")
        
        # Test configuration status
        status = config.get_configuration_status()
        print(f"✅ Configuration status: {status['total_config_values']} values loaded")
        
        print("✅ UnifiedConfigurationManager test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ UnifiedConfigurationManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_di_container_service():
    """Test DIContainerService with UnifiedConfigurationManager."""
    print("\n🧪 Testing DIContainerService with UnifiedConfigurationManager...")
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        
        # Test basic initialization
        di_container = DIContainerService(service_name="test_di_container")
        print("✅ DIContainerService initialized successfully")
        
        # Test unified configuration methods
        env = di_container.get_environment()
        print(f"✅ Environment from DIContainer: {env}")
        
        api_port = di_container.get_int("API_PORT", 8000)
        print(f"✅ API Port from DIContainer: {api_port}")
        
        debug_mode = di_container.get_bool("API_DEBUG", False)
        print(f"✅ Debug Mode from DIContainer: {debug_mode}")
        
        # Test specialized configuration methods
        db_config = di_container.get_database_config()
        print(f"✅ Database config from DIContainer: {len(db_config)} settings")
        
        redis_config = di_container.get_redis_config()
        print(f"✅ Redis config from DIContainer: {len(redis_config)} settings")
        
        llm_config = di_container.get_llm_config()
        print(f"✅ LLM config from DIContainer: {len(llm_config)} settings")
        
        governance_config = di_container.get_governance_config()
        print(f"✅ Governance config from DIContainer: {len(governance_config)} settings")
        
        # Test environment-specific methods
        is_dev = di_container.is_development()
        print(f"✅ Is Development: {is_dev}")
        
        is_prod = di_container.is_production()
        print(f"✅ Is Production: {is_prod}")
        
        # Test configuration status
        status = di_container.get_configuration_status()
        print(f"✅ DIContainer configuration status: {status['total_config_values']} values loaded")
        
        # Test health check
        health = di_container.get_service_health()
        print(f"✅ DIContainer health: {health['status']}")
        
        print("✅ DIContainerService test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ DIContainerService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_layers():
    """Test configuration layer loading."""
    print("\n🧪 Testing Configuration Layers...")
    
    try:
        from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
        
        config = UnifiedConfigurationManager(service_name="test_layers")
        
        # Test that we can access configuration from different layers
        print("✅ Testing configuration layer access...")
        
        # Test environment-specific configuration
        env = config.get_environment()
        print(f"✅ Environment layer: {env}")
        
        # Test business logic configuration
        llm_config = config.get_llm_config()
        print(f"✅ LLM config from business logic: {len(llm_config)} settings")
        
        # Test infrastructure configuration
        db_config = config.get_database_config()
        print(f"✅ Database config from infrastructure: {len(db_config)} settings")
        
        # Test configuration validation
        required_keys = ["ENVIRONMENT", "API_PORT", "DATABASE_HOST"]
        validation = config.validate_configuration(required_keys)
        print(f"✅ Configuration validation: {validation['valid']}")
        
        print("✅ Configuration layers test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration layers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Unified Configuration Tests...\n")
    
    tests = [
        test_unified_configuration_manager,
        test_di_container_service,
        test_configuration_layers
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    print(f"📈 Success Rate: {(sum(results) / len(results)) * 100:.1f}%")
    
    if all(results):
        print("\n🎉 All tests passed! Unified Configuration is working correctly!")
        return True
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
