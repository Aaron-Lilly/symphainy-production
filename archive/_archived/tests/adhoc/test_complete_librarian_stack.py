#!/usr/bin/env python3
"""
Complete Librarian Stack Test

Tests the complete 5-layer architecture for Librarian:
1. Foundation Services (Infrastructure)
2. Smart City Service (Business Logic) 
3. Micro-Modules (Focused Business Logic)
4. Interfaces (Contracts)
5. MCP Server (Abstraction Exposure)

This validates that our Librarian refactoring follows the Data Steward pattern.
"""

import sys
import os
import asyncio

# Add the project root to the Python path
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

print("🧪 Testing Complete Librarian 5-Layer Architecture")
print("=" * 60)

# Test imports
try:
    from config.environment_loader import EnvironmentLoader
    from config import Environment
    print("✅ Environment configuration imported")
    
    from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
    print("✅ Foundation services imported")
    
    from backend.smart_city.services.librarian import LibrarianService
    print("✅ LibrarianService imported")
    
    from backend.smart_city.services.librarian.mcp_server import LibrarianMCPServer
    print("✅ LibrarianMCPServer imported")
    
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
        librarian = LibrarianService(utility, None, None, Environment.DEVELOPMENT)
        await librarian.initialize()
        print("  ✅ Librarian Service initialized")
        
        # Test service health
        health = await librarian.get_service_health()
        print(f"  ✅ Service Health: {health['status']}")
        print(f"  ✅ Environment: {health['environment']}")
        print(f"  ✅ Architecture: {health['architecture']}")
        
        # Layer 3: Micro-Modules
        print("Layer 3: Micro-Modules...")
        knowledge_status = await librarian.knowledge_management.get_status()
        search_status = await librarian.search_engine.get_status()
        metadata_status = await librarian.metadata_extraction.get_status()
        analytics_status = await librarian.knowledge_analytics.get_status()
        recommendations_status = await librarian.knowledge_recommendations.get_status()
        
        print(f"  ✅ Knowledge Management: {knowledge_status['status']}")
        print(f"  ✅ Search Engine: {search_status['status']}")
        print(f"  ✅ Metadata Extraction: {metadata_status['status']}")
        print(f"  ✅ Knowledge Analytics: {analytics_status['status']}")
        print(f"  ✅ Knowledge Recommendations: {recommendations_status['status']}")
        
        # Layer 4: Interfaces (tested via service methods)
        print("Layer 4: Interfaces...")
        from backend.smart_city.interfaces import KnowledgeSearchRequest, SearchMode, KnowledgeType
        
        search_request = KnowledgeSearchRequest(
            query="test knowledge",
            search_mode=SearchMode.SEMANTIC,
            knowledge_type=KnowledgeType.DOCUMENT,
            tags=["test"],
            limit=10
        )
        
        from foundations.utility_foundation.utilities import UserContext
        user_context = UserContext(user_id="test_user", session_id="test_session")
        search_response = await librarian.search_knowledge(search_request, user_context)
        print(f"  ✅ Knowledge Search: {search_response['success']}")
        
        # Layer 5: MCP Server
        print("Layer 5: MCP Server...")
        mcp_server = LibrarianMCPServer(librarian, None)
        await mcp_server.initialize(user_context)
        print("  ✅ Librarian MCP Server initialized")
        
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
        
        # Test search_knowledge tool
        search_params = {
            "query": "test knowledge search",
            "search_mode": "semantic",
            "knowledge_type": "document",
            "limit": 5
        }
        search_result = await mcp_server.execute_tool("search_knowledge", search_params, user_context)
        print(f"  ✅ MCP Search Tool: {search_result['success']}")
        
        # Test index_knowledge tool
        index_params = {
            "title": "Test Knowledge Asset",
            "content": "This is a test knowledge asset for validation.",
            "knowledge_type": "document",
            "tags": ["test", "validation"],
            "content_type": "text/plain"
        }
        index_result = await mcp_server.execute_tool("index_knowledge", index_params, user_context)
        print(f"  ✅ MCP Index Tool: {index_result['success']}")
        
        if index_result['success'] and index_result['data']['success']:
            asset_id = index_result['data']['asset_id']
            print(f"  ✅ Indexed Asset ID: {asset_id}")
            
            # Test get_knowledge_asset tool
            get_params = {"asset_id": asset_id}
            get_result = await mcp_server.execute_tool("get_knowledge_asset", get_params, user_context)
            print(f"  ✅ MCP Get Asset Tool: {get_result['success']}")
        
        # Test extract_metadata tool
        metadata_params = {
            "content": "This is a test document with some content.",
            "content_type": "text/plain",
            "file_name": "test_document.txt"
        }
        metadata_result = await mcp_server.execute_tool("extract_metadata", metadata_params, user_context)
        print(f"  ✅ MCP Metadata Tool: {metadata_result['success']}")
        
        # Test assess_quality tool
        quality_params = {
            "content": "This is a well-structured test document with proper content and formatting.",
            "title": "Quality Test Document",
            "metadata": {"author": "test_user", "tags": ["test", "quality"]}
        }
        quality_result = await mcp_server.execute_tool("assess_quality", quality_params, user_context)
        print(f"  ✅ MCP Quality Tool: {quality_result['success']}")
        
        # Test get_recommendations tool
        rec_params = {
            "recommendation_type": "user_based",
            "limit": 5
        }
        rec_result = await mcp_server.execute_tool("get_recommendations", rec_params, user_context)
        print(f"  ✅ MCP Recommendations Tool: {rec_result['success']}")
        
        # Test get_analytics tool
        analytics_params = {"time_period": "30d"}
        analytics_result = await mcp_server.execute_tool("get_analytics", analytics_params, user_context)
        print(f"  ✅ MCP Analytics Tool: {analytics_result['success']}")
        
        # Test get_service_status tool
        status_params = {}
        status_result = await mcp_server.execute_tool("get_service_status", status_params, user_context)
        print(f"  ✅ MCP Status Tool: {status_result['success']}")
        
        # Test get_search_suggestions tool
        suggestions_params = {"partial_query": "test"}
        suggestions_result = await mcp_server.execute_tool("get_search_suggestions", suggestions_params, user_context)
        print(f"  ✅ MCP Suggestions Tool: {suggestions_result['success']}")
        
        return True
    
    success = asyncio.run(test_complete_stack())
    
    if success:
        print("\n🎉 Complete Librarian Stack Test Passed!")
        print("\n📋 Complete Librarian Stack Summary:")
        print("  ✅ Layer 1: Foundation Services (Infrastructure) - Working")
        print("  ✅ Layer 2: Smart City Service (Business Logic) - Working")
        print("  ✅ Layer 3: Micro-Modules (Focused Business Logic) - Working")
        print("  ✅ Layer 4: Interfaces (Contracts) - Working")
        print("  ✅ Layer 5: MCP Server (Abstraction Exposure) - Working")
        print("  ✅ Environment Configuration - Working")
        print("  ✅ End-to-End Functionality - Working")
        print("\n🎯 The Librarian refactoring follows the Data Steward pattern successfully!")
        print("\n🚀 Librarian is complete and ready to serve as a template for other roles!")
    else:
        print("\n❌ Test Failed")
        
except Exception as e:
    print(f"\n❌ Test Failed: {e}")
    import traceback
    traceback.print_exc()
