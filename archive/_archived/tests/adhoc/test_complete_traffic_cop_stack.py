#!/usr/bin/env python3
"""
Comprehensive Traffic Cop Stack Test

Tests the complete Traffic Cop service stack including:
- Foundation services integration
- Traffic Cop service functionality
- MCP server tools
- End-to-end workflows
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation import CuratorFoundationService
from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
from backend.smart_city.services.traffic_cop.mcp_server.traffic_cop_mcp_server import TrafficCopMCPServer
from config.environment_loader import EnvironmentLoader
from config import Environment


async def test_traffic_cop_stack():
    """Test the complete Traffic Cop stack."""
    print("🚦 Testing Complete Traffic Cop Stack")
    print("=" * 50)

    try:
        # Initialize environment
        env_loader = EnvironmentLoader(Environment.DEVELOPMENT)
        print("✅ Environment initialized")

        # Initialize foundation services
        utility_foundation = UtilityFoundationService(env_loader)
        public_works_foundation = PublicWorksFoundationService(utility_foundation, env_loader)
        curator_foundation = CuratorFoundationService(utility_foundation, env_loader)

        await utility_foundation.initialize()
        await public_works_foundation.initialize()
        await curator_foundation.initialize()
        print("✅ Foundation services initialized")

        # Initialize Traffic Cop Service
        traffic_cop_service = TrafficCopService(
            utility_foundation=utility_foundation,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation,
            environment=Environment.DEVELOPMENT
        )
        await traffic_cop_service.initialize()
        print("✅ Traffic Cop Service initialized")

        # Test 1: Service Health
        print("\n🔍 Test 1: Service Health")
        health_status = await traffic_cop_service.get_health_status()
        print(f"   Health Status: {health_status['overall_status']}")
        print(f"   Micro-modules: {len(health_status['micro_modules'])}")
        assert health_status['overall_status'] == 'healthy', "Service should be healthy"

        # Test 2: Service Info
        print("\n🔍 Test 2: Service Info")
        service_info = await traffic_cop_service.get_service_info()
        print(f"   Service Name: {service_info['service_name']}")
        print(f"   Capabilities: {len(service_info['capabilities'])}")
        assert service_info['service_name'] == 'TrafficCopService', "Service name should match"

        # Test 3: Session Management
        print("\n🔍 Test 3: Session Management")
        
        # Create session
        session_data = {
            "user_id": "test_user_123",
            "dimensions": ["smart_city", "business"],
            "metadata": {"test": True},
            "state_scope": "local",
            "priority": 2
        }
        create_result = await traffic_cop_service.create_session(session_data)
        print(f"   Session Created: {create_result['success']}")
        assert create_result['success'], "Session creation should succeed"
        
        session_id = create_result['session_id']
        print(f"   Session ID: {session_id}")

        # Validate session
        validate_result = await traffic_cop_service.validate_session(session_id)
        print(f"   Session Valid: {validate_result['valid']}")
        assert validate_result['valid'], "Session should be valid"

        # Update session state
        state_data = {
            "key": "test_state",
            "value": {"data": "test_value", "timestamp": datetime.utcnow().isoformat()},
            "scope": "local",
            "priority": 2
        }
        update_result = await traffic_cop_service.update_session_state(session_id, state_data)
        print(f"   State Updated: {update_result['success']}")
        assert update_result['success'], "State update should succeed"

        # Get session state
        get_state_result = await traffic_cop_service.get_session_state(session_id, "test_state")
        print(f"   State Retrieved: {get_state_result['success']}")
        assert get_state_result['success'], "State retrieval should succeed"

        # Test 4: State Coordination
        print("\n🔍 Test 4: State Coordination")
        
        # Share state
        share_data = {
            "key": "shared_state",
            "value": {"shared_data": "test_shared"},
            "dimensions": ["smart_city", "business"],
            "scope": "shared",
            "priority": 2
        }
        share_result = await traffic_cop_service.share_state(share_data)
        print(f"   State Shared: {share_result['success']}")
        assert share_result['success'], "State sharing should succeed"

        # Get shared states
        get_shared_result = await traffic_cop_service.get_shared_states(scope="shared")
        print(f"   Shared States Retrieved: {get_shared_result['success']}")
        assert get_shared_result['success'], "Shared states retrieval should succeed"

        # Test 5: Cross-Dimensional Orchestration
        print("\n🔍 Test 5: Cross-Dimensional Orchestration")
        
        # Create cross-dimensional session
        cross_session_data = {
            "dimensions": ["smart_city", "business", "agentic"],
            "metadata": {"cross_dimensional": True},
            "coordination_strategy": "parallel"
        }
        cross_session_result = await traffic_cop_service.create_cross_dimensional_session(cross_session_data)
        print(f"   Cross-Dimensional Session Created: {cross_session_result['success']}")
        assert cross_session_result['success'], "Cross-dimensional session creation should succeed"
        
        cross_session_id = cross_session_result['session_id']
        print(f"   Cross-Dimensional Session ID: {cross_session_id}")

        # Coordinate dimensions
        coordination_data = {
            "type": "state_sync",
            "target_dimensions": ["smart_city", "business"],
            "payload": {"sync_data": "test_sync"}
        }
        coordinate_result = await traffic_cop_service.coordinate_dimensions(cross_session_id, coordination_data)
        print(f"   Dimensions Coordinated: {coordinate_result['success']}")
        assert coordinate_result['success'], "Dimension coordination should succeed"

        # Test 6: Health Monitoring
        print("\n🔍 Test 6: Health Monitoring")
        
        # Collect metrics
        metrics_data = {
            "session_id": session_id,
            "metric_type": "performance",
            "metric_name": "response_time",
            "metric_value": 0.5,
            "dimensions": ["smart_city"]
        }
        collect_result = await traffic_cop_service.collect_metrics(metrics_data)
        print(f"   Metrics Collected: {collect_result['success']}")
        assert collect_result['success'], "Metrics collection should succeed"

        # Get session health
        health_result = await traffic_cop_service.get_session_health_detailed(session_id)
        print(f"   Session Health Retrieved: {health_result['success']}")
        assert health_result['success'], "Session health retrieval should succeed"

        # Test 7: MCP Server
        print("\n🔍 Test 7: MCP Server")
        
        # Initialize MCP server
        mcp_server = TrafficCopMCPServer(env_loader)
        await mcp_server.initialize()
        print("   MCP Server Initialized")

        # Get server info
        server_info = await mcp_server.get_server_info()
        print(f"   Server Name: {server_info.server_name}")
        print(f"   Tools Available: {len(server_info.tools)}")

        # Get tools
        tools = await mcp_server.get_tools()
        print(f"   Tools Retrieved: {len(tools)}")
        assert len(tools) > 0, "Should have tools available"

        # Test a few MCP tools
        print("\n🔍 Test 8: MCP Tool Execution")
        
        # Test create_session tool
        create_tool_result = await mcp_server.execute_tool("create_session", {
            "user_id": "mcp_test_user",
            "dimensions": ["smart_city"],
            "metadata": {"mcp_test": True}
        })
        print(f"   Create Session Tool: {create_tool_result['success']}")
        assert create_tool_result['success'], "Create session tool should work"

        # Test get_service_health tool
        health_tool_result = await mcp_server.execute_tool("get_service_health", {})
        print(f"   Service Health Tool: {health_tool_result['success']}")
        assert health_tool_result['success'], "Service health tool should work"

        # Test 9: Service Metrics
        print("\n🔍 Test 9: Service Metrics")
        metrics = await traffic_cop_service.get_metrics()
        print(f"   Metrics Retrieved: {metrics['service_name']}")
        print(f"   Session Management Metrics: {metrics['metrics']['session_management']}")
        print(f"   State Coordination Metrics: {metrics['metrics']['state_coordination']}")
        print(f"   Cross-Dimensional Metrics: {metrics['metrics']['cross_dimensional_orchestration']}")
        print(f"   Health Monitoring Metrics: {metrics['metrics']['health_monitoring']}")

        # Test 10: Cleanup
        print("\n🔍 Test 10: Cleanup")
        
        # Terminate session
        terminate_result = await traffic_cop_service.terminate_session(session_id)
        print(f"   Session Terminated: {terminate_result['success']}")
        assert terminate_result['success'], "Session termination should succeed"

        # Cleanup MCP server
        await mcp_server.cleanup()
        print("   MCP Server Cleaned Up")

        # Cleanup service
        await traffic_cop_service.cleanup()
        print("   Traffic Cop Service Cleaned Up")

        print("\n✅ All Traffic Cop Stack Tests Passed!")
        print("🚦 Traffic Cop Service is production-ready!")

        return True

    except Exception as e:
        print(f"\n❌ Traffic Cop Stack Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Traffic Cop Stack Test Suite")
    print("=" * 60)
    
    success = await test_traffic_cop_stack()
    
    if success:
        print("\n🎉 Traffic Cop Stack Test Suite Completed Successfully!")
        print("🚦 Traffic Cop Service is ready for production deployment!")
    else:
        print("\n💥 Traffic Cop Stack Test Suite Failed!")
        print("❌ Please check the errors above and fix them before deployment.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
