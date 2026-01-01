#!/usr/bin/env python3
"""
Simple Configuration Test

Test the basic functionality of the UnifiedConfigurationManager.
"""

import sys
import os
from pathlib import Path

# Add the platform to the Python path
sys.path.insert(0, str(Path(__file__).parent / "symphainy-platform"))

def test_unified_configuration():
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
        
        # Test configuration validation
        required_keys = ["ENVIRONMENT", "API_PORT", "DATABASE_HOST"]
        validation = config.validate_configuration(required_keys)
        print(f"✅ Configuration validation: {validation['valid']}")
        
        print("✅ UnifiedConfigurationManager test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ UnifiedConfigurationManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🚀 Starting Simple Configuration Test...\n")
    
    success = test_unified_configuration()
    
    if success:
        print("\n🎉 Configuration test passed! Unified Configuration is working correctly!")
        return True
    else:
        print("\n⚠️ Configuration test failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
