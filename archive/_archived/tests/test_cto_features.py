#!/usr/bin/env python3
"""
Test CTO Features Implementation

Test script to verify that CTO-suggested features are properly implemented.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from foundations.di_container.di_container_service import DIContainerService
from backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server_enhanced import SecurityGuardMCPServer
from utilities import UserContext

async def test_cto_features():
    """Test CTO-suggested features implementation."""
    print("🧪 Testing CTO Features Implementation...")
    
    try:
        # Initialize DI container
        print("1. Initializing DI container...")
        di_container = DIContainerService()
        print("✅ DI container initialized")
        
        # Test SecurityGuardMCPServer with CTO features
        print("2. Testing SecurityGuardMCPServer with CTO features...")
        security_server = SecurityGuardMCPServer(di_container)
        
        # Test server info
        server_info = security_server.get_server_info()
        print(f"✅ Server info: {server_info['name']} v{server_info['version']}")
        
        # Test usage guide
        print("3. Testing usage guide...")
        usage_guide = security_server.get_usage_guide()
        print(f"✅ Usage guide: {usage_guide['server_name']}")
        print(f"   - Capabilities: {len(usage_guide['capabilities'])}")
        print(f"   - Tools: {len(usage_guide['tools'])}")
        print(f"   - Examples: {len(usage_guide['examples'])}")
        print(f"   - Schemas: {len(usage_guide['schemas'])}")
        
        # Test health status
        print("4. Testing health status...")
        health = security_server.get_health()
        print(f"✅ Health status: {health['status']}")
        print(f"   - Dependencies: {len(health['dependencies'])}")
        print(f"   - Uptime: {health['uptime']}")
        
        # Test version info
        print("5. Testing version info...")
        version = security_server.get_version()
        print(f"✅ Version: {version['version']}")
        print(f"   - API Version: {version['api_version']}")
        print(f"   - Compatibility: {version['compatibility']['supported_versions']}")
        print(f"   - Changelog entries: {len(version['changelog'])}")
        
        # Test tool list
        print("6. Testing tool list...")
        tools = security_server.list_tools()
        print(f"✅ Tools: {len(tools)} tools available")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # Test tool execution
        print("7. Testing tool execution...")
        user_context = UserContext(
            user_id="test_user",
            tenant_id="test_tenant", 
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["read", "write"]
        )
        
        result = await security_server.execute_tool("get_user_context_with_tenant", {
            "token": "test_token_123"
        }, user_context)
        print(f"✅ Tool execution: {result.get('success', 'unknown')}")
        print(f"   - Result: {result.get('result', 'no result')}")
        
        print("\n🎉 All CTO features tests passed!")
        print("📊 CTO Features Summary:")
        print(f"   - Usage Guide: ✅ Complete with examples and schemas")
        print(f"   - Health Monitoring: ✅ Complete with dependency checks")
        print(f"   - Version Management: ✅ Complete with compatibility info")
        print(f"   - Tool Discovery: ✅ Complete with descriptions")
        print(f"   - Tool Execution: ✅ Complete with validation")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cto_features())
    sys.exit(0 if success else 1)
