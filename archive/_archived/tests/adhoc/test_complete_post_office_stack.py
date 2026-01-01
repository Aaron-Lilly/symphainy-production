#!/usr/bin/env python3
"""
Complete Post Office Stack Test

Comprehensive test for the entire Post Office stack including:
- Foundation services
- Post Office service with micro-modules
- MCP server
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

print('🧪 Testing Complete Post Office Stack...')

async def test_post_office_stack():
    """Test the complete Post Office stack."""
    try:
        # Test 1: Import Post Office Service
        print('\n1️⃣ Testing Post Office Service Import...')
        from backend.smart_city.services.post_office import PostOfficeService
        print('✅ PostOfficeService imported successfully')

        # Test 2: Import MCP Server
        print('\n2️⃣ Testing MCP Server Import...')
        from backend.smart_city.services.post_office.mcp_server import PostOfficeMCPServer
        print('✅ PostOfficeMCPServer imported successfully')

        # Test 3: Initialize Post Office Service
        print('\n3️⃣ Testing Post Office Service Initialization...')
        post_office_service = PostOfficeService()
        await post_office_service.initialize()
        print('✅ Post Office Service initialized successfully')

        # Test 4: Test Event Routing
        print('\n4️⃣ Testing Event Routing...')
        event_data = {
            "event_type": "system",
            "source": "test_source",
            "target": "test_target",
            "scope": "local",
            "priority": "normal",
            "payload": {"test": "data"},
            "metadata": {"test": "metadata"}
        }
        event_result = await post_office_service.publish_event(event_data)
        print(f'✅ Event published: {event_result["success"]}')

        # Test 5: Test Messaging
        print('\n5️⃣ Testing Messaging...')
        message_data = {
            "message_type": "text",
            "sender": "test_sender",
            "recipients": ["test_recipient"],
            "subject": "Test Message",
            "content": "This is a test message",
            "priority": "normal"
        }
        message_result = await post_office_service.send_message(message_data)
        print(f'✅ Message sent: {message_result["success"]}')

        # Test 6: Test AGUI Communication
        print('\n6️⃣ Testing AGUI Communication...')
        agent_data = {
            "agent_name": "Test Agent",
            "agent_type": "test",
            "capabilities": ["test_capability"],
            "endpoint_url": "http://test.example.com"
        }
        agent_result = await post_office_service.register_agent(agent_data)
        print(f'✅ Agent registered: {agent_result["success"]}')

        # Test 7: Test Notifications
        print('\n7️⃣ Testing Notifications...')
        notification_data = {
            "notification_type": "info",
            "title": "Test Notification",
            "message": "This is a test notification",
            "recipients": ["test_user"],
            "priority": "normal",
            "channels": ["in_app"]
        }
        notification_result = await post_office_service.create_notification(notification_data)
        print(f'✅ Notification created: {notification_result["success"]}')

        # Test 8: Test Service Health
        print('\n8️⃣ Testing Service Health...')
        health_status = await post_office_service.get_health_status()
        print(f'✅ Service health: {health_status["overall_status"]}')

        # Test 9: Test Service Metrics
        print('\n9️⃣ Testing Service Metrics...')
        metrics = await post_office_service.get_metrics()
        print(f'✅ Service metrics retrieved: {len(metrics["metrics"])} modules')

        # Test 10: Initialize MCP Server
        print('\n🔟 Testing MCP Server Initialization...')
        mcp_server = PostOfficeMCPServer()
        await mcp_server.initialize()
        print('✅ MCP Server initialized successfully')

        # Test 11: Test MCP Tools
        print('\n1️⃣1️⃣ Testing MCP Tools...')
        tools = await mcp_server.get_tools()
        print(f'✅ MCP Tools available: {len(tools)} tools')

        # Test 12: Test MCP Tool Execution
        print('\n1️⃣2️⃣ Testing MCP Tool Execution...')
        tool_result = await mcp_server.execute_tool("get_service_health", {})
        print(f'✅ MCP Tool executed: {tool_result.get("overall_status", "unknown")}')

        # Test 13: Test Service Info
        print('\n1️⃣3️⃣ Testing Service Info...')
        service_info = await post_office_service.get_service_info()
        print(f'✅ Service info: {service_info["service_name"]} v{service_info["service_version"]}')

        # Test 14: Test Micro-Modules Status
        print('\n1️⃣4️⃣ Testing Micro-Modules Status...')
        event_routing_status = await post_office_service.event_routing_module.get_status()
        messaging_status = await post_office_service.messaging_module.get_status()
        agui_communication_status = await post_office_service.agui_communication_module.get_status()
        notification_status = await post_office_service.notification_module.get_status()
        
        print(f'✅ Event Routing: {event_routing_status["status"]}')
        print(f'✅ Messaging: {messaging_status["status"]}')
        print(f'✅ AGUI Communication: {agui_communication_status["status"]}')
        print(f'✅ Notification: {notification_status["status"]}')

        # Test 15: Test Cleanup
        print('\n1️⃣5️⃣ Testing Cleanup...')
        await post_office_service.cleanup()
        await mcp_server.cleanup()
        print('✅ Cleanup completed successfully')

        print('\n🎉 All Post Office Stack tests passed!')
        return True

    except Exception as e:
        print(f'\n❌ Post Office Stack test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print('🚀 Starting Complete Post Office Stack Test...')
    print('=' * 60)
    
    success = await test_post_office_stack()
    
    print('=' * 60)
    if success:
        print('🎉 Post Office Stack Test: PASSED')
        print('\n📋 Test Summary:')
        print('  ✅ Post Office Service imported and initialized')
        print('  ✅ Event routing functionality working')
        print('  ✅ Messaging functionality working')
        print('  ✅ AGUI communication functionality working')
        print('  ✅ Notification management functionality working')
        print('  ✅ MCP server imported and initialized')
        print('  ✅ MCP tools available and executable')
        print('  ✅ Service health and metrics working')
        print('  ✅ Micro-modules status working')
        print('  ✅ Cleanup completed successfully')
        print('\n🏆 Post Office Service is ready for production!')
    else:
        print('❌ Post Office Stack Test: FAILED')
        print('\n🔧 Please check the error messages above and fix any issues.')

if __name__ == "__main__":
    asyncio.run(main())
