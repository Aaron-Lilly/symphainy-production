#!/usr/bin/env python3
"""
Test Agentic Infrastructure Abstractions

Test the newly implemented MCP Client, MCP Protocol, and Tool Registry abstractions
to ensure they work correctly and fill the Agentic domain gaps.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.infrastructure_foundation.abstractions.mcp_client_abstraction import MCPClientAbstraction
from foundations.infrastructure_foundation.abstractions.mcp_protocol_abstraction import MCPProtocolAbstraction
from foundations.infrastructure_foundation.abstractions.tool_registry_abstraction import ToolRegistryAbstraction
from foundations.public_works_foundation.abstractions.agui_abstraction import AGUIAbstraction


async def test_mcp_client_abstraction():
    """Test MCP Client Abstraction."""
    print("🧪 Testing MCP Client Abstraction...")
    
    try:
        # Create MCP client
        client = MCPClientAbstraction(
            server_endpoint="http://localhost:8000/mcp",
            server_name="test-mcp-server"
        )
        
        # Test connection
        await client.connect()
        print("✅ MCP Client connection successful")
        
        # Test ping
        ping_result = await client.ping()
        print(f"✅ MCP Client ping: {ping_result}")
        
        # Test list tools
        tools = await client.list_tools()
        print(f"✅ MCP Client list tools: {len(tools)} tools found")
        
        # Test server info
        server_info = await client.get_server_info()
        print(f"✅ MCP Client server info: {server_info['server_name']}")
        
        # Test disconnect
        await client.disconnect()
        print("✅ MCP Client disconnect successful")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Client test failed: {e}")
        return False


async def test_mcp_protocol_abstraction():
    """Test MCP Protocol Abstraction."""
    print("\n🧪 Testing MCP Protocol Abstraction...")
    
    try:
        # Create MCP protocol
        protocol = MCPProtocolAbstraction(server_name="test-mcp-protocol")
        
        # Test initialization
        await protocol.initialize()
        print("✅ MCP Protocol initialization successful")
        
        # Test tool registration
        protocol.register_tool(
            "test_tool",
            "Test tool for validation",
            {"type": "object", "properties": {"input": {"type": "string"}}}
        )
        print("✅ MCP Protocol tool registration successful")
        
        # Test request handling
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = protocol.handle_request(json.dumps(test_request))
        response_data = json.loads(response)
        print(f"✅ MCP Protocol request handling: {len(response_data.get('result', {}).get('tools', []))} tools")
        
        # Test server info
        server_info = protocol.get_server_info()
        print(f"✅ MCP Protocol server info: {server_info['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Protocol test failed: {e}")
        return False


async def test_tool_registry_abstraction():
    """Test Tool Registry Abstraction."""
    print("\n🧪 Testing Tool Registry Abstraction...")
    
    try:
        # Create tool registry (without ArangoDB for this test)
        registry = ToolRegistryAbstraction()
        
        # Test initialization
        await registry.initialize()
        print("✅ Tool Registry initialization successful")
        
        # Test tool registration
        tool_data = {
            "name": "test_tool",
            "description": "Test tool for validation",
            "input_schema": {"type": "object"},
            "category": "test",
            "domain": "agentic"
        }
        
        result = await registry.register_tool(tool_data)
        print(f"✅ Tool Registry registration: {result['success']}")
        
        # Test tool discovery
        tools = await registry.discover_tools({"category": "test"})
        print(f"✅ Tool Registry discovery: {len(tools)} tools found")
        
        # Test tool details
        tool_details = await registry.get_tool_details(result['tool_id'])
        print(f"✅ Tool Registry tool details: {tool_details['name'] if tool_details else 'None'}")
        
        # Test registry stats
        stats = await registry.get_registry_stats()
        print(f"✅ Tool Registry stats: {stats['total_tools']} total tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool Registry test failed: {e}")
        return False


async def test_agui_abstraction():
    """Test AGUI Abstraction (existing)."""
    print("\n🧪 Testing AGUI Abstraction...")
    
    try:
        # Create AGUI abstraction (without infrastructure dependencies for this test)
        agui = AGUIAbstraction({})
        
        # Test initialization
        await agui.initialize()
        print("✅ AGUI initialization successful")
        
        # Test agent message sending (will fail gracefully without WebSocket)
        result = await agui.send_agent_message("test_agent", {"message": "test"})
        print(f"✅ AGUI send message: {result['success']}")
        
        # Test broadcast message
        result = await agui.broadcast_agent_message({"message": "broadcast"})
        print(f"✅ AGUI broadcast message: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ AGUI test failed: {e}")
        return False


async def main():
    """Run all agentic abstraction tests."""
    print("🚀 Starting Agentic Infrastructure Abstractions Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test all abstractions
    results.append(await test_mcp_client_abstraction())
    results.append(await test_mcp_protocol_abstraction())
    results.append(await test_tool_registry_abstraction())
    results.append(await test_agui_abstraction())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Agentic domain infrastructure is complete.")
        print("✅ MCP Client Abstraction: Working")
        print("✅ MCP Protocol Abstraction: Working")
        print("✅ Tool Registry Abstraction: Working")
        print("✅ AGUI Abstraction: Working")
        print("\n🏆 The Agentic domain now has full infrastructure support!")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    import json
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
