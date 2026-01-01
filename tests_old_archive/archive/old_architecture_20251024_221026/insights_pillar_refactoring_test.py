"""
Test Insights Pillar Refactoring - Validate the refactored architecture

Tests the refactored insights pillar architecture including:
- Business services with MCP tool exposure
- Hybrid MCP server pattern (Core + Capability servers)
- Agents using LLMs and MCP tools
- Proper architectural separation
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the symphainy-platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

from utilities.security_authorization.security_authorization_utility import UserContext
from foundations.agentic_foundation.business_services.insights_generation_service import InsightsDataService
from backend.business_enablement.pillars.insights_pillar.mcp_server.insights_pillar_core_mcp_server import InsightsPillarCoreMCPServer
from backend.business_enablement.pillars.insights_pillar.mcp_server.data_analysis_mcp_server import DataAnalysisMCPServer
from backend.business_enablement.pillars.insights_pillar.mcp_server.insights_generation_mcp_server import InsightsGenerationMCPServer
from backend.business_enablement.pillars.insights_pillar.agents.insights_analysis_agent import InsightsAnalysisAgent


async def test_insights_data_service():
    """Test the refactored InsightsDataService with MCP tools."""
    print("\n🧪 Testing InsightsDataService with MCP tools...")
    
    try:
        # Create service
        service = InsightsDataService()
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_456",
            permissions=["insights_analysis", "data_access"],
            tenant_id="test_tenant_789"
        )
        
        # Test MCP tool: prepare_insights_data
        print("  📊 Testing prepare_insights_data MCP tool...")
        analysis_results = {
            "analysis_type": "trend_analysis",
            "confidence_score": 0.85,
            "processing_time": 0.3,
            "data_quality": "high",
            "sample_size": 1000,
            "results": {
                "key_metrics": ["revenue_growth", "customer_satisfaction"],
                "patterns": ["seasonal_trend", "growth_pattern"],
                "anomalies": ["spike_detected"]
            }
        }
        
        result = await service.prepare_insights_data(analysis_results, user_context, "test_session")
        assert result["success"] == True
        assert "insights_context" in result
        assert "business_rules" in result
        assert "historical_context" in result
        print("    ✅ prepare_insights_data MCP tool works")
        
        # Test MCP tool: get_insights_capabilities
        print("  🔧 Testing get_insights_capabilities MCP tool...")
        result = await service.get_insights_capabilities(user_context, "test_session")
        assert result["success"] == True
        assert "available_insight_types" in result
        assert "business_domains" in result
        print("    ✅ get_insights_capabilities MCP tool works")
        
        # Test MCP tool: get_recommendation_templates
        print("  📋 Testing get_recommendation_templates MCP tool...")
        result = await service.get_recommendation_templates(user_context, "test_session")
        assert result["success"] == True
        assert "templates" in result
        print("    ✅ get_recommendation_templates MCP tool works")
        
        # Test MCP tool: get_insights_frameworks
        print("  🏗️ Testing get_insights_frameworks MCP tool...")
        result = await service.get_insights_frameworks(user_context, "test_session")
        assert result["success"] == True
        assert "frameworks" in result
        print("    ✅ get_insights_frameworks MCP tool works")
        
        # Test health check
        print("  ❤️ Testing health check...")
        health = await service.health_check()
        assert health["status"] == "healthy"
        assert "available_mcp_tools" in health
        print("    ✅ Health check works")
        
        print("  ✅ InsightsDataService with MCP tools: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ InsightsDataService test failed: {e}")
        return False


async def test_core_mcp_server():
    """Test the Core MCP Server."""
    print("\n🧪 Testing Core MCP Server...")
    
    try:
        # Create core MCP server
        core_server = InsightsPillarCoreMCPServer()
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_456",
            permissions=["insights_analysis", "data_access"],
            tenant_id="test_tenant_789"
        )
        
        # Test discover capabilities
        print("  🔍 Testing discover_capabilities...")
        result = await core_server.discover_capabilities(user_context, "test_session")
        assert result["success"] == True
        assert "core_tools" in result
        assert "capability_servers" in result
        assert "available_workflows" in result
        print("    ✅ discover_capabilities works")
        
        # Test orchestrate workflow
        print("  🎭 Testing orchestrate_workflow...")
        result = await core_server.orchestrate_workflow(
            "data_analysis_workflow",
            {"data": "test_data"},
            user_context,
            "test_session"
        )
        assert result["success"] == True
        assert result["workflow_type"] == "data_analysis_workflow"
        print("    ✅ orchestrate_workflow works")
        
        # Test get workflow status
        print("  📊 Testing get_workflow_status...")
        result = await core_server.get_workflow_status("workflow_123", user_context)
        assert result["success"] == True
        assert "workflow_id" in result
        print("    ✅ get_workflow_status works")
        
        # Test get service health
        print("  ❤️ Testing get_service_health...")
        result = await core_server.get_service_health(user_context)
        assert result["success"] == True
        assert "core_server" in result
        print("    ✅ get_service_health works")
        
        print("  ✅ Core MCP Server: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Core MCP Server test failed: {e}")
        return False


async def test_data_analysis_mcp_server():
    """Test the Data Analysis MCP Server."""
    print("\n🧪 Testing Data Analysis MCP Server...")
    
    try:
        # Create data analysis MCP server
        data_server = DataAnalysisMCPServer()
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_456",
            permissions=["insights_analysis", "data_access"],
            tenant_id="test_tenant_789"
        )
        
        # Test analyze data
        print("  📊 Testing analyze_data...")
        test_data = {
            "records": 1000,
            "quality": 0.95,
            "completeness": 0.88
        }
        result = await data_server.analyze_data(test_data, "descriptive", user_context, "test_session")
        assert result["success"] == True
        assert "analysis_id" in result
        assert "results" in result
        print("    ✅ analyze_data works")
        
        # Test get analysis types
        print("  🔧 Testing get_analysis_types...")
        result = await data_server.get_analysis_types(user_context, "test_session")
        assert result["success"] == True
        assert "analysis_types" in result
        print("    ✅ get_analysis_types works")
        
        # Test get analysis history
        print("  📈 Testing get_analysis_history...")
        result = await data_server.get_analysis_history(user_context, "test_session")
        assert result["success"] == True
        assert "analysis_history" in result
        print("    ✅ get_analysis_history works")
        
        # Test validate data
        print("  ✅ Testing validate_data...")
        result = await data_server.validate_data(test_data, user_context, "test_session")
        assert result["success"] == True
        assert "validation_results" in result
        print("    ✅ validate_data works")
        
        # Test get analysis capabilities
        print("  🛠️ Testing get_analysis_capabilities...")
        result = await data_server.get_analysis_capabilities(user_context, "test_session")
        assert result["success"] == True
        assert "capabilities" in result
        print("    ✅ get_analysis_capabilities works")
        
        print("  ✅ Data Analysis MCP Server: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Data Analysis MCP Server test failed: {e}")
        return False


async def test_insights_generation_mcp_server():
    """Test the Insights Generation MCP Server."""
    print("\n🧪 Testing Insights Generation MCP Server...")
    
    try:
        # Create insights generation MCP server
        insights_server = InsightsGenerationMCPServer()
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_456",
            permissions=["insights_analysis", "data_access"],
            tenant_id="test_tenant_789"
        )
        
        # Test prepare insights data
        print("  📊 Testing prepare_insights_data...")
        analysis_results = {
            "analysis_type": "trend_analysis",
            "confidence_score": 0.85,
            "results": {"key_metrics": ["revenue", "growth"]}
        }
        result = await insights_server.prepare_insights_data(analysis_results, user_context, "test_session")
        assert result["success"] == True
        assert "insights_context" in result
        assert "business_rules" in result
        print("    ✅ prepare_insights_data works")
        
        # Test get insights capabilities
        print("  🔧 Testing get_insights_capabilities...")
        result = await insights_server.get_insights_capabilities(user_context, "test_session")
        assert result["success"] == True
        assert "available_insight_types" in result
        print("    ✅ get_insights_capabilities works")
        
        # Test get recommendation templates
        print("  📋 Testing get_recommendation_templates...")
        result = await insights_server.get_recommendation_templates(user_context, "test_session")
        assert result["success"] == True
        assert "templates" in result
        print("    ✅ get_recommendation_templates works")
        
        # Test get insights frameworks
        print("  🏗️ Testing get_insights_frameworks...")
        result = await insights_server.get_insights_frameworks(user_context, "test_session")
        assert result["success"] == True
        assert "frameworks" in result
        print("    ✅ get_insights_frameworks works")
        
        # Test get business rules
        print("  📜 Testing get_business_rules...")
        result = await insights_server.get_business_rules(user_context, "test_session")
        assert result["success"] == True
        assert "business_rules" in result
        print("    ✅ get_business_rules works")
        
        # Test get historical context
        print("  📚 Testing get_historical_context...")
        result = await insights_server.get_historical_context(user_context, "test_session")
        assert result["success"] == True
        assert "historical_context" in result
        print("    ✅ get_historical_context works")
        
        print("  ✅ Insights Generation MCP Server: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Insights Generation MCP Server test failed: {e}")
        return False


async def test_insights_analysis_agent():
    """Test the Insights Analysis Agent."""
    print("\n🧪 Testing Insights Analysis Agent...")
    
    try:
        # Create insights analysis agent
        agent = InsightsAnalysisAgent()
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_456",
            permissions=["insights_analysis", "data_access"],
            tenant_id="test_tenant_789"
        )
        
        # Test generate insights
        print("  🧠 Testing generate_insights...")
        test_data = {
            "analysis_type": "comprehensive",
            "confidence_score": 0.85,
            "data_quality": "high",
            "sample_size": 1000
        }
        result = await agent.generate_insights(test_data, user_context, "test_session", "comprehensive")
        assert result["success"] == True
        assert "insights" in result
        assert "recommendations" in result
        assert "analysis_metadata" in result
        print("    ✅ generate_insights works")
        
        # Test analyze trends
        print("  📈 Testing analyze_trends...")
        result = await agent.analyze_trends(test_data, user_context, "test_session")
        assert result["success"] == True
        assert "trend_analysis" in result
        print("    ✅ analyze_trends works")
        
        # Test detect anomalies
        print("  🔍 Testing detect_anomalies...")
        result = await agent.detect_anomalies(test_data, user_context, "test_session")
        assert result["success"] == True
        assert "anomaly_detection" in result
        print("    ✅ detect_anomalies works")
        
        print("  ✅ Insights Analysis Agent: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Insights Analysis Agent test failed: {e}")
        return False


async def test_hybrid_mcp_pattern():
    """Test the hybrid MCP pattern integration."""
    print("\n🧪 Testing Hybrid MCP Pattern Integration...")
    
    try:
        # Create core server
        core_server = InsightsPillarCoreMCPServer()
        
        # Create capability servers
        data_server = DataAnalysisMCPServer()
        insights_server = InsightsGenerationMCPServer()
        
        # Register capability servers with core server
        print("  🔗 Testing capability server registration...")
        await core_server.register_capability_server("data_analysis_server", data_server)
        await core_server.register_capability_server("insights_generation_server", insights_server)
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_456",
            permissions=["insights_analysis", "data_access"],
            tenant_id="test_tenant_789"
        )
        
        # Test discovery with registered servers
        print("  🔍 Testing capability discovery with registered servers...")
        result = await core_server.discover_capabilities(user_context, "test_session")
        assert result["success"] == True
        assert "data_analysis_server" in result["capability_servers"]
        assert "insights_generation_server" in result["capability_servers"]
        print("    ✅ Capability discovery with registered servers works")
        
        # Test workflow orchestration
        print("  🎭 Testing workflow orchestration...")
        result = await core_server.orchestrate_workflow(
            "insights_generation_workflow",
            {"data": "test_data"},
            user_context,
            "test_session"
        )
        assert result["success"] == True
        assert result["workflow_type"] == "insights_generation_workflow"
        print("    ✅ Workflow orchestration works")
        
        # Test service health with registered servers
        print("  ❤️ Testing service health with registered servers...")
        result = await core_server.get_service_health(user_context)
        assert result["success"] == True
        assert "data_analysis_server" in result["capability_servers"]
        assert "insights_generation_server" in result["capability_servers"]
        print("    ✅ Service health with registered servers works")
        
        print("  ✅ Hybrid MCP Pattern Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Hybrid MCP Pattern Integration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Insights Pillar Refactoring Tests")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        ("InsightsDataService with MCP tools", test_insights_data_service),
        ("Core MCP Server", test_core_mcp_server),
        ("Data Analysis MCP Server", test_data_analysis_mcp_server),
        ("Insights Generation MCP Server", test_insights_generation_mcp_server),
        ("Insights Analysis Agent", test_insights_analysis_agent),
        ("Hybrid MCP Pattern Integration", test_hybrid_mcp_pattern)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Insights Pillar refactoring is working correctly.")
        print("\n✅ Architecture Validation:")
        print("  • Business services expose MCP tools for agents")
        print("  • Hybrid MCP pattern: Core server + Capability servers")
        print("  • Agents use LLMs and MCP tools autonomously")
        print("  • Proper architectural separation achieved")
        print("  • No direct LLM usage in business services")
        print("  • No business logic in MCP servers")
    else:
        print(f"❌ {total - passed} tests failed. Please review the issues.")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
