#!/usr/bin/env python3
"""
Debug script to test why InfrastructureAccessMixin returns None
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bases.mixins.infrastructure_access_mixin import InfrastructureAccessMixin
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
import asyncio

class TestService(InfrastructureAccessMixin):
    """Test service to debug mixin behavior."""
    
    def __init__(self):
        self.role_name = "security_guard"
        self._init_infrastructure_access(None)  # Will be set later

async def test_mixin():
    """Test the mixin behavior."""
    print("🔍 Testing InfrastructureAccessMixin behavior...\n")
    
    # Create DI container
    di_container = DIContainerService("test")
    
    # Initialize Public Works Foundation
    public_works = PublicWorksFoundationService(di_container)
    await public_works.initialize()
    di_container.public_works_foundation = public_works
    
    print(f"✅ Public Works Foundation initialized: {public_works.is_initialized}")
    
    # Create test service
    test_service = TestService()
    test_service.di_container = di_container
    
    # Test getting auth abstraction
    print("\n📝 Testing get_auth_abstraction()...")
    try:
        auth_abstraction = test_service.get_auth_abstraction()
        print(f"   Result: {auth_abstraction}")
        print(f"   Type: {type(auth_abstraction)}")
        if auth_abstraction:
            print("   ✅ SUCCESS: Auth abstraction retrieved!")
        else:
            print("   ❌ FAILED: Auth abstraction is None")
            
            # Try direct call
            print("\n📝 Testing direct call...")
            direct = di_container.get_foundation_service("PublicWorksFoundationService")
            if direct:
                direct_abstraction = direct.get_abstraction("auth")
                print(f"   Direct result: {direct_abstraction}")
                print(f"   Direct type: {type(direct_abstraction)}")
                if direct_abstraction:
                    print("   ✅ Direct call works!")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mixin())




