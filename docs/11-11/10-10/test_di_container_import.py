#!/usr/bin/env python3
"""
Test DIContainerService Import
"""

import sys
import os
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "symphainy-platform"))

try:
    from foundations.di_container.di_container_service import DIContainerService
    print("✅ DIContainerService import successful")
    
    # Test creating an instance
    di_container = DIContainerService("test_service")
    print("✅ DIContainerService instantiation successful")
    
    # Test basic functionality
    config = di_container.get_config()
    print(f"✅ Configuration access successful: {type(config)}")
    
    # Test configuration access
    test_value = config.get("TEST_KEY", "default_value")
    print(f"✅ Configuration get method successful: {test_value}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
