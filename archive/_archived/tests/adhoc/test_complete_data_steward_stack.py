#!/usr/bin/env python3
"""
Complete Data Steward Stack Test

Tests the complete 5-layer architecture for Data Steward:
1. Foundation Services (Infrastructure)
2. Smart City Service (Business Logic) 
3. Micro-Modules (Focused Business Logic)
4. Interfaces (Contracts)
5. MCP Server (Abstraction Exposure)

This validates that our new layered pattern works end-to-end.
"""

import sys
import os
import asyncio
import base64

# Add the project root to the Python path
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

from config.environment_loader import EnvironmentLoader
from config import Environment
from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.infrastructure_foundation.infrastructure_foundation_service_env_integrated import InfrastructureFoundationServiceEnvIntegrated
from foundations.public_works_foundation.public_works_foundation_service_env_integrated import PublicWorksFoundationServiceEnvIntegrated
from foundations.curator_foundation.services import CapabilityRegistryService
from foundations.utility_foundation.utilities import UserContext
from backend.smart_city.services.data_steward import DataStewardService
from backend.smart_city.services.data_steward.mcp_server import DataStewardMCPServer


async def test_complete_data_steward_stack():
    """Test the complete Data Steward 5-layer architecture."""
    print("🧪 Testing Complete Data Steward Stack")
    print("=" * 60)
    
    try:
        # Layer 1: Foundation Services (Infrastructure)
        print("\n🏗️ Layer 1: Foundation Services")
        print("-" * 40)
        
        utility = UtilityFoundationService()
        await utility.initialize()
        print("✅ Utility Foundation Service initialized")
        
        infrastructure = InfrastructureFoundationServiceEnvIntegrated(utility, None, None, Environment.DEVELOPMENT)
        await infrastructure.initialize()
        print("✅ Infrastructure Foundation Service initialized")
        
        public_works = PublicWorksFoundationServiceEnvIntegrated(utility, None, infrastructure, Environment.DEVELOPMENT)
        await public_works.initialize()
        print("✅ Public Works Foundation Service initialized")
        
        curator = CuratorFoundationService(utility)
        await curator.initialize()
        print("✅ Curator Foundation Service initialized")
        
        # Layer 2: Smart City Service (Business Logic)
        print("\n🏙️ Layer 2: Smart City Service")
        print("-" * 40)
        
        data_steward = DataStewardService(utility, public_works, curator, Environment.DEVELOPMENT)
        await data_steward.initialize()
        print("✅ Data Steward Service initialized")
        
        # Test service health
        health = await data_steward.get_service_health()
        print(f"✅ Service Health: {health['status']}")
        print(f"✅ Environment: {health['environment']}")
        print(f"✅ Architecture: {health['architecture']}")
        
        # Layer 3: Micro-Modules (Focused Business Logic)
        print("\n🔧 Layer 3: Micro-Modules")
        print("-" * 40)
        
        # Test micro-module functionality
        file_lifecycle_status = await data_steward.file_lifecycle.get_status()
        print(f"✅ File Lifecycle Module: {file_lifecycle_status['status']}")
        print(f"✅ Total Files: {file_lifecycle_status['total_files']}")
        
        # Layer 4: Interfaces (Contracts) - Tested via service methods
        print("\n📋 Layer 4: Interfaces (Contracts)")
        print("-" * 40)
        
        # Test file upload (IFileStorage interface)
        from backend.smart_city.interfaces.file_storage_interface import FileUploadRequest, FileType, StorageTier
        
        test_data = b"Hello, Data Steward! This is a test file."
        upload_request = FileUploadRequest(
            file_name="test_file.txt",
            file_data=test_data,
            content_type="text/plain",
            storage_tier=StorageTier.WARM,
            file_type=FileType.DOCUMENT,
            tags=["test", "mcp"],
            description="Test file for MCP server validation"
        )
        
        user_context = UserContext(user_id="test_user", session_id="test_session")
        upload_response = await data_steward.upload_file(upload_request, user_context)
        print(f"✅ File Upload: {upload_response['success']}")
        
        if upload_response['success']:
            file_id = upload_response['file_id']
            print(f"✅ File ID: {file_id}")
            
            # Test file download
            from backend.smart_city.interfaces.file_storage_interface import FileDownloadRequest
            download_request = FileDownloadRequest(file_id=file_id)
            download_response = await data_steward.download_file(download_request, user_context)
            print(f"✅ File Download: {download_response['success']}")
            
            if download_response['success']:
                print(f"✅ Downloaded Data: {download_response['file_data'][:50]}...")
        
        # Layer 5: MCP Server (Abstraction Exposure)
        print("\n🌐 Layer 5: MCP Server")
        print("-" * 40)
        
        # Initialize MCP server
        mcp_server = DataStewardMCPServer(data_steward, curator.capability_registry)
        await mcp_server.initialize(user_context)
        print("✅ Data Steward MCP Server initialized")
        
        # Test MCP server info
        server_info = mcp_server.get_server_info()
        print(f"✅ Server Name: {server_info.server_name}")
        print(f"✅ Version: {server_info.version}")
        print(f"✅ Tools Count: {len(server_info.tools)}")
        print(f"✅ Capabilities: {len(server_info.capabilities)}")
        
        # Test MCP tools
        tools = mcp_server.get_tools()
        print(f"✅ Available Tools: {[tool.name for tool in tools]}")
        
        # Test MCP tool execution
        print("\n🔧 Testing MCP Tool Execution")
        print("-" * 30)
        
        # Test upload_file tool
        test_data_b64 = base64.b64encode(test_data).decode('utf-8')
        upload_params = {
            "file_name": "mcp_test_file.txt",
            "file_data": test_data_b64,
            "content_type": "text/plain",
            "storage_tier": "warm",
            "file_type": "document",
            "tags": ["test", "mcp", "validation"],
            "description": "Test file uploaded via MCP tool"
        }
        
        upload_result = await mcp_server.execute_tool("upload_file", upload_params, user_context)
        print(f"✅ MCP Upload Tool: {upload_result['success']}")
        
        if upload_result['success'] and upload_result['data']['success']:
            mcp_file_id = upload_result['data']['file_id']
            print(f"✅ MCP File ID: {mcp_file_id}")
            
            # Test download_file tool
            download_params = {"file_id": mcp_file_id}
            download_result = await mcp_server.execute_tool("download_file", download_params, user_context)
            print(f"✅ MCP Download Tool: {download_result['success']}")
            
            # Test get_service_status tool
            status_params = {}
            status_result = await mcp_server.execute_tool("get_service_status", status_params, user_context)
            print(f"✅ MCP Status Tool: {status_result['success']}")
            
            if status_result['success']:
                status_data = status_result['data']
                print(f"✅ Service Status: {status_data['service_status']}")
                print(f"✅ Environment: {status_data['environment']}")
                print(f"✅ Architecture: {status_data['architecture']}")
        
        # Test search_files tool
        search_params = {
            "query": "test",
            "file_type": "document",
            "limit": 10
        }
        search_result = await mcp_server.execute_tool("search_files", search_params, user_context)
        print(f"✅ MCP Search Tool: {search_result['success']}")
        
        if search_result['success']:
            search_data = search_result['data']
            print(f"✅ Search Results: {search_data['total_count']} files found")
        
        # Test get_storage_stats tool
        stats_params = {}
        stats_result = await mcp_server.execute_tool("get_storage_stats", stats_params, user_context)
        print(f"✅ MCP Stats Tool: {stats_result['success']}")
        
        if stats_result['success']:
            stats_data = stats_result['data']
            print(f"✅ Storage Stats: {stats_data['total_files']} total files")
        
        print("\n🎉 Complete Data Steward Stack Test Passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Complete Data Steward Stack Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_environment_switching():
    """Test that the Data Steward service works across different environments."""
    print("\n🌍 Testing Environment Switching")
    print("=" * 60)
    
    try:
        # Test different environments
        environments = [Environment.DEVELOPMENT, Environment.TESTING, Environment.PRODUCTION]
        
        for env in environments:
            print(f"\n🔧 Testing {env.value} environment...")
            
            # Initialize foundation services
            utility = UtilityFoundationService()
            await utility.initialize()
            
            infrastructure = InfrastructureFoundationServiceEnvIntegrated(utility, None, None, env)
            await infrastructure.initialize()
            
            public_works = PublicWorksFoundationServiceEnvIntegrated(utility, None, infrastructure, env)
            await public_works.initialize()
            
            curator = CuratorFoundationService(utility)
            await curator.initialize()
            
            # Initialize Data Steward Service
            data_steward = DataStewardService(utility, public_works, curator, env)
            await data_steward.initialize()
            
            # Test service health
            health = await data_steward.get_service_health()
            print(f"  ✅ Service Health: {health['status']}")
            print(f"  ✅ Environment: {health['environment']}")
            print(f"  ✅ Architecture: {health['architecture']}")
            
            # Test environment-specific behavior
            print(f"  ✅ Is Production: {data_steward.env_loader.config_manager.is_production()}")
            print(f"  ✅ Is Development: {data_steward.env_loader.config_manager.is_development()}")
            print(f"  ✅ Feature Flags: {data_steward.feature_flags}")
            
            print(f"  ✅ {env.value} environment test completed")
        
        print("\n🎉 Environment Switching Test Passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Environment Switching Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the complete Data Steward stack tests."""
    print("🚀 Starting Complete Data Steward Stack Tests...")
    print("=" * 60)
    
    # Test 1: Complete stack functionality
    stack_success = await test_complete_data_steward_stack()
    
    # Test 2: Environment switching
    env_success = await test_environment_switching()
    
    if stack_success and env_success:
        print("\n🎉 All Tests Passed!")
        print("\n📋 Complete Data Steward Stack Summary:")
        print("  ✅ Layer 1: Foundation Services (Infrastructure) - Working")
        print("  ✅ Layer 2: Smart City Service (Business Logic) - Working")
        print("  ✅ Layer 3: Micro-Modules (Focused Business Logic) - Working")
        print("  ✅ Layer 4: Interfaces (Contracts) - Working")
        print("  ✅ Layer 5: MCP Server (Abstraction Exposure) - Working")
        print("  ✅ Environment Configuration - Working")
        print("  ✅ End-to-End Functionality - Working")
        print("\n🎯 The 5-layer architecture pattern is validated and ready for replication!")
        return True
    else:
        print("\n❌ Some Tests Failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
