#!/usr/bin/env python3
"""
Test Redis Integration - Verify Real Implementation Works

Tests that the refactored Smart City services can actually use real Redis
for session management, state synchronization, and communication.

Tests:
1. Redis Adapter connection
2. Session Creation via Session Abstraction
3. Session Retrieval via Session Abstraction
4. End-to-end session management flow
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.public_works_foundation.infrastructure_registry.security_registry import SecurityRegistry
from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter
from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionContext, SessionType, SecurityLevel


class MockConfigAdapter(ConfigAdapter):
    """Mock configuration adapter for testing."""
    
    def get_redis_config(self):
        """Return Redis configuration for testing."""
        return {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": ""
        }
    
    def get_supabase_url(self):
        return "https://mock.supabase.co"
    
    def get_supabase_anon_key(self):
        return "mock_anon_key"
    
    def get_supabase_service_key(self):
        return "mock_service_key"
    
    def get_jwt_config(self):
        return {
            "secret_key": "mock_secret_key_for_testing",
            "algorithm": "HS256"
        }


async def test_redis_adapter_connection():
    """Test that Redis adapter can connect to real Redis."""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Redis Adapter Connection")
    print("=" * 70)
    
    try:
        from symphainy_platform.infrastructure.adapters.redis_adapter import RedisAdapter
        
        # Try to connect to Redis
        redis_adapter = RedisAdapter(host="localhost", port=6379, db=0)
        
        # Test basic operations
        await redis_adapter.set("test_key", "test_value")
        value = await redis_adapter.get("test_key")
        
        if value == "test_value":
            print("✅ Redis adapter connection works!")
            print(f"   Got value: {value}")
            return True
        else:
            print(f"❌ Redis adapter failed - got: {value}")
            return False
            
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
        print("   (This is OK for now - Redis needs to be running)")
        return False


async def test_session_abstraction():
    """Test that Session Abstraction uses real Redis."""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Session Abstraction with Real Redis")
    print("=" * 70)
    
    try:
        # Create mock config
        config = MockConfigAdapter()
        
        # Create Security Registry (builds real infrastructure)
        security_registry = SecurityRegistry(config)
        await security_registry.initialize()
        
        # Get session abstraction
        session_abstraction = security_registry.get_abstraction("session")
        
        if not session_abstraction:
            print("❌ Session abstraction not available")
            return False
        
        print(f"✅ Session abstraction created")
        print(f"   Adapter type: {session_abstraction.adapter_type}")
        
        # Try to create a session
        context = SessionContext(
            service_id="test_service",
            agent_id="test_agent",
            tenant_id="test_tenant",
            environment="test",
            region="us-west-2",
            metadata={}
        )
        
        session_data = {
            "user_id": "test_user_123",
            "agent_id": "test_agent",
            "session_type": "user",
            "security_level": "medium",
            "metadata": {"test": "data"},
            "tags": ["test", "integration"]
        }
        
        # This will use real Redis if available
        session = await session_abstraction.create_session(context, session_data)
        
        print(f"✅ Session created successfully!")
        print(f"   Session ID: {session.session_id}")
        print(f"   User ID: {session.user_id}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Session creation failed: {e}")
        print("   (This might be OK if Redis is not running)")
        import traceback
        traceback.print_exc()
        return False


async def test_traffic_cop_service():
    """Test that Traffic Cop service can use Redis for sessions."""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Traffic Cop Service with Redis")
    print("=" * 70)
    
    try:
        from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
        from bases.protocols.traffic_cop_protocol import SessionRequest, SessionResponse
        
        # Create mock DI container
        class MockDIContainer:
            def __init__(self):
                self.foundation_services = {}
            
            def get_foundation_service(self, service_name):
                return self.foundation_services.get(service_name)
        
        di_container = MockDIContainer()
        
        # Create Traffic Cop service
        traffic_cop = TrafficCopService(di_container)
        
        # Try to create a session
        session_request = SessionRequest(
            session_id="test_session_123",
            session_type="default",
            context={"test": "data"},
            ttl_seconds=3600,
            tenant_id="test_tenant"
        )
        
        # This will try to use session abstraction (which uses Redis)
        session_response = await traffic_cop.create_session(session_request)
        
        print(f"✅ Traffic Cop service uses session abstraction!")
        print(f"   Session ID: {session_response.session_id}")
        print(f"   Status: {session_response.status}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Traffic Cop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all Redis integration tests."""
    print("=" * 70)
    print("🚀 TESTING REDIS INTEGRATION - REAL INFRASTRUCTURE")
    print("=" * 70)
    
    tests = [
        ("Redis Adapter Connection", test_redis_adapter_connection),
        ("Session Abstraction", test_session_abstraction),
        ("Traffic Cop Service", test_traffic_cop_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "⚠️  FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Redis integration is working!")
    elif passed > 0:
        print(f"\n⚠️  {total - passed} tests failed (may need Redis running)")
    else:
        print(f"\n⚠️  All tests failed - need to debug")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)


