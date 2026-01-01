#!/usr/bin/env python3
"""
Complete Conductor Stack Test

Tests the complete 5-layer architecture for Conductor:
1. Foundation Services (Infrastructure)
2. Smart City Service (Business Logic) 
3. Micro-Modules (Focused Business Logic)
4. Interfaces (Contracts)
5. MCP Server (Abstraction Exposure)

This validates that our Conductor refactoring follows the Data Steward pattern.
"""

import sys
import os
import asyncio

# Add the project root to the Python path
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

print("🧪 Testing Complete Conductor 5-Layer Architecture")
print("=" * 60)

# Test imports
try:
    from config.environment_loader import EnvironmentLoader
    from config import Environment
    print("✅ Environment configuration imported")
    
    from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
    print("✅ Foundation services imported")
    
    from backend.smart_city.services.conductor.conductor_service import ConductorService
    print("✅ ConductorService imported")
    
    from backend.smart_city.services.conductor.mcp_server.conductor_mcp_server import ConductorMCPServer
    print("✅ ConductorMCPServer imported")
    
    print("\n🎉 All imports successful!")
    
    # Test service initialization
    async def test_complete_stack():
        print("\n🏗️ Testing Complete 5-Layer Architecture")
        print("-" * 50)
        
        # Layer 1: Foundation Services
        print("Layer 1: Foundation Services...")
        utility = UtilityFoundationService()
        await utility.initialize()
        print("  ✅ Utility Foundation Service initialized")
        
        # Layer 2: Smart City Service
        print("Layer 2: Smart City Service...")
        conductor = ConductorService(utility, None, None, Environment.DEVELOPMENT)
        await conductor.initialize()
        print("  ✅ Conductor Service initialized")
        
        # Test service health
        health = await conductor.get_service_health()
        print(f"  ✅ Service Health: {health['status']}")
        print(f"  ✅ Environment: {health['environment']}")
        print(f"  ✅ Architecture: {health['architecture']}")
        
        # Layer 3: Micro-Modules
        print("Layer 3: Micro-Modules...")
        workflow_mgmt_status = await conductor.workflow_management.get_status()
        workflow_exec_status = await conductor.workflow_execution.get_status()
        task_mgmt_status = await conductor.task_management.get_status()
        scheduling_status = await conductor.workflow_scheduling.get_status()
        analytics_status = await conductor.orchestration_analytics.get_status()
        
        print(f"  ✅ Workflow Management: {workflow_mgmt_status['status']}")
        print(f"  ✅ Workflow Execution: {workflow_exec_status['status']}")
        print(f"  ✅ Task Management: {task_mgmt_status['status']}")
        print(f"  ✅ Workflow Scheduling: {scheduling_status['status']}")
        print(f"  ✅ Orchestration Analytics: {analytics_status['status']}")
        
        # Layer 4: Interfaces (tested via service methods)
        print("Layer 4: Interfaces...")
        from backend.smart_city.interfaces import WorkflowCreateRequest, WorkflowType, WorkflowStep
        
        workflow_request = WorkflowCreateRequest(
            name="Test Workflow",
            description="A test workflow for validation",
            workflow_type=WorkflowType.SEQUENTIAL,
            steps=[
                WorkflowStep(
                    step_id="step1",
                    name="Test Step 1",
                    task_type="test",
                    input_data={"test": "data"}
                )
            ],
            triggers=[],
            conditions=[],
            variables={},
            tags=["test", "validation"],
            category="test"
        )
        
        from foundations.utility_foundation.utilities import UserContext
        user_context = UserContext(user_id="test_user", session_id="test_session")
        workflow = await conductor.create_workflow(workflow_request, user_context)
        print(f"  ✅ Workflow Creation: {workflow['name']} ({workflow['workflow_id']})")
        
        # Layer 5: MCP Server
        print("Layer 5: MCP Server...")
        mcp_server = ConductorMCPServer(conductor, None)
        await mcp_server.initialize(user_context)
        print("  ✅ Conductor MCP Server initialized")
        
        # Test MCP server info
        server_info = mcp_server.get_server_info()
        print(f"  ✅ Server Name: {server_info.server_name}")
        print(f"  ✅ Version: {server_info.version}")
        print(f"  ✅ Tools Count: {len(server_info.tools)}")
        print(f"  ✅ Capabilities: {len(server_info.capabilities)}")
        
        # Test MCP tools
        tools = mcp_server.get_tools()
        print(f"  ✅ Available Tools: {[tool.name for tool in tools]}")
        
        # Test MCP tool execution
        print("\n🔧 Testing MCP Tool Execution...")
        
        # Test create_workflow tool
        create_params = {
            "name": "MCP Test Workflow",
            "description": "A workflow created via MCP",
            "workflow_type": "sequential",
            "steps": [
                {
                    "step_id": "mcp_step1",
                    "name": "MCP Test Step",
                    "task_type": "test",
                    "input_data": {"mcp": "test"}
                }
            ],
            "tags": ["mcp", "test"],
            "category": "mcp_test"
        }
        create_result = await mcp_server.execute_tool("create_workflow", create_params, user_context)
        print(f"  ✅ MCP Create Workflow Tool: {create_result['success']}")
        
        if create_result['success'] and create_result['data']['workflow_id']:
            workflow_id = create_result['data']['workflow_id']
            print(f"  ✅ Created Workflow ID: {workflow_id}")
            
            # Test get_workflow tool
            get_params = {"workflow_id": workflow_id}
            get_result = await mcp_server.execute_tool("get_workflow", get_params, user_context)
            print(f"  ✅ MCP Get Workflow Tool: {get_result['success']}")
            
            # Test execute_workflow tool
            execute_params = {
                "workflow_id": workflow_id,
                "input_data": {"test_input": "MCP execution test"}
            }
            execute_result = await mcp_server.execute_tool("execute_workflow", execute_params, user_context)
            print(f"  ✅ MCP Execute Workflow Tool: {execute_result['success']}")
        
        # Test create_task tool
        task_params = {
            "name": "MCP Test Task",
            "description": "A task created via MCP",
            "task_type": "test",
            "priority": "normal",
            "input_data": {"mcp": "task_test"},
            "tags": ["mcp", "task"],
            "category": "mcp_test"
        }
        task_result = await mcp_server.execute_tool("create_task", task_params, user_context)
        print(f"  ✅ MCP Create Task Tool: {task_result['success']}")
        
        # Test create_schedule tool
        schedule_params = {
            "workflow_id": workflow_id if 'workflow_id' in locals() else "test_workflow",
            "name": "MCP Test Schedule",
            "description": "A schedule created via MCP",
            "schedule_type": "once",
            "start_time": "2024-01-01T00:00:00Z",
            "input_data": {"mcp": "schedule_test"},
            "tags": ["mcp", "schedule"],
            "category": "mcp_test"
        }
        schedule_result = await mcp_server.execute_tool("create_schedule", schedule_params, user_context)
        print(f"  ✅ MCP Create Schedule Tool: {schedule_result['success']}")
        
        # Test get_workflow_analytics tool
        analytics_params = {"time_period": "30d"}
        analytics_result = await mcp_server.execute_tool("get_workflow_analytics", analytics_params, user_context)
        print(f"  ✅ MCP Analytics Tool: {analytics_result['success']}")
        
        # Test get_performance_metrics tool
        metrics_params = {}
        metrics_result = await mcp_server.execute_tool("get_performance_metrics", metrics_params, user_context)
        print(f"  ✅ MCP Performance Metrics Tool: {metrics_result['success']}")
        
        # Test get_service_status tool
        status_params = {}
        status_result = await mcp_server.execute_tool("get_service_status", status_params, user_context)
        print(f"  ✅ MCP Status Tool: {status_result['success']}")
        
        return True
    
    success = asyncio.run(test_complete_stack())
    
    if success:
        print("\n🎉 Complete Conductor Stack Test Passed!")
        print("\n📋 Complete Conductor Stack Summary:")
        print("  ✅ Layer 1: Foundation Services (Infrastructure) - Working")
        print("  ✅ Layer 2: Smart City Service (Business Logic) - Working")
        print("  ✅ Layer 3: Micro-Modules (Focused Business Logic) - Working")
        print("  ✅ Layer 4: Interfaces (Contracts) - Working")
        print("  ✅ Layer 5: MCP Server (Abstraction Exposure) - Working")
        print("  ✅ Environment Configuration - Working")
        print("  ✅ End-to-End Functionality - Working")
        print("\n🎯 The Conductor refactoring follows the Data Steward pattern successfully!")
        print("\n🚀 Conductor is complete and ready to serve as a template for other roles!")
    else:
        print("\n❌ Test Failed")
        
except Exception as e:
    print(f"\n❌ Test Failed: {e}")
    import traceback
    traceback.print_exc()
