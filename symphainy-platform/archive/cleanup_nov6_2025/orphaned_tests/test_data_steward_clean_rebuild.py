#!/usr/bin/env python3
"""
Test Data Steward Service Clean Rebuild

This test validates the clean rebuild of the Data Steward Service using ONLY our new base and protocol construct.
No archived dependencies, no complex refactoring - just clean, focused implementation.
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the clean rebuild
from data_steward_service_clean_rebuild import DataStewardService


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.services = {}
        self.foundations = {}
        self.logger = None
        self.telemetry_utility = MockTelemetryUtility()
    
    def get_service(self, service_name: str):
        return self.services.get(service_name)
    
    def register_service(self, service_name: str, service_instance):
        self.services[service_name] = service_instance
    
    def get_foundation_service(self, foundation_name: str):
        return self.foundations.get(foundation_name)
    
    def register_foundation_service(self, foundation_name: str, foundation_instance):
        self.foundations[foundation_name] = foundation_instance
    
    def get_utility(self, utility_name: str):
        """Mock utility getter for testing."""
        if utility_name == "logger":
            import logging
            return logging.getLogger("test")
        elif utility_name == "health":
            return {"status": "healthy"}
        elif utility_name == "telemetry":
            return self.telemetry_utility
        elif utility_name == "error_handler":
            return {"handle_error": lambda e: None}
        else:
            return f"mock_{utility_name}"


class MockTelemetryUtility:
    """Mock telemetry utility for testing."""
    
    def record_event(self, event_name: str, data: Dict[str, Any]):
        """Mock record event."""
        pass
    
    def record_metric(self, metric_name: str, value: float, metadata: Dict[str, Any]):
        """Mock record metric."""
        pass


class MockCuratorFoundation:
    """Mock Curator Foundation for testing."""
    
    def __init__(self):
        self.soa_apis = {}
        self.mcp_tools = {}
        self.capabilities = {}
    
    async def register_soa_api(self, service_name: str, api_name: str, endpoint: str, handler: Any, metadata: Dict[str, Any] = None):
        """Mock SOA API registration."""
        key = f"{service_name}.{api_name}"
        self.soa_apis[key] = {
            "service_name": service_name,
            "api_name": api_name,
            "endpoint": endpoint,
            "handler": handler,
            "metadata": metadata or {}
        }
        return True
    
    async def register_mcp_tool(self, tool_name: str, tool_definition: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Mock MCP tool registration."""
        self.mcp_tools[tool_name] = {
            "tool_name": tool_name,
            "tool_definition": tool_definition,
            "metadata": metadata or {}
        }
        return True


async def test_data_steward_clean_rebuild():
    """Test the clean rebuild of Data Steward Service."""
    print("\n🔍 Testing Data Steward Service Clean Rebuild...")
    
    try:
        # Setup mock dependencies
        di_container = MockDIContainer()
        curator_foundation = MockCuratorFoundation()
        
        di_container.register_foundation_service("CuratorFoundationService", curator_foundation)
        
        # Initialize Data Steward Service (Clean Rebuild)
        data_steward = DataStewardService(di_container)
        success = await data_steward.initialize()
        assert success, "Data Steward Service should initialize successfully"
        print("✅ Data Steward Service (Clean Rebuild) initialization successful")
        
        # Test SOA API exposure
        assert len(data_steward.soa_apis) == 7, "Should have 7 SOA APIs"
        expected_apis = [
            "create_content_policy", "get_policy_for_content", "record_lineage",
            "get_lineage", "validate_schema", "get_quality_metrics", "enforce_compliance"
        ]
        for api_name in expected_apis:
            assert api_name in data_steward.soa_apis, f"Should have {api_name} API"
        print("✅ SOA API exposure configured (7 APIs)")
        
        # Test MCP server integration
        assert len(data_steward.mcp_tools) == 7, "Should have 7 MCP tools"
        expected_tools = [
            "create_content_policy", "get_policy_for_content", "record_lineage",
            "get_lineage", "validate_schema", "get_quality_metrics", "enforce_compliance"
        ]
        for tool_name in expected_tools:
            assert tool_name in data_steward.mcp_tools, f"Should have {tool_name} MCP tool"
        assert data_steward.mcp_server_enabled, "MCP server should be enabled"
        print("✅ MCP server integration configured (7 tools)")
        
        # Test SOA API registration with Curator
        assert len(curator_foundation.soa_apis) == 7, "SOA APIs should be registered with Curator"
        for api_name in expected_apis:
            key = f"data_steward.{api_name}"
            assert key in curator_foundation.soa_apis, f"SOA API {api_name} should be registered"
        print("✅ SOA APIs registered with Curator")
        
        # Test MCP tool registration with Curator
        assert len(curator_foundation.mcp_tools) == 7, "MCP tools should be registered with Curator"
        for tool_name in expected_tools:
            assert tool_name in curator_foundation.mcp_tools, f"MCP tool {tool_name} should be registered"
        print("✅ MCP tools registered with Curator")
        
        # Test core functionality
        policy_id = await data_steward.create_content_policy("user_data", {"retention": "7_years"})
        assert policy_id, "Policy creation should work"
        print("✅ Core policy creation functionality works")
        
        # Test policy retrieval
        policy_result = await data_steward.get_policy_for_content("user_data")
        assert policy_result["success"], "Policy retrieval should work"
        print("✅ Core policy retrieval functionality works")
        
        # Test lineage recording
        lineage_id = await data_steward.record_lineage({"asset_id": "test_asset", "source": "upload"})
        assert lineage_id, "Lineage recording should work"
        print("✅ Core lineage recording functionality works")
        
        # Test lineage retrieval
        lineage_result = await data_steward.get_lineage("test_asset")
        assert lineage_result["success"], "Lineage retrieval should work"
        print("✅ Core lineage retrieval functionality works")
        
        # Test schema validation
        schema_valid = await data_steward.validate_schema({"name": "test", "type": "object", "fields": []})
        assert schema_valid, "Schema validation should work"
        print("✅ Core schema validation functionality works")
        
        # Test quality metrics
        metrics_result = await data_steward.get_quality_metrics("test_asset")
        assert metrics_result["success"], "Quality metrics should work"
        print("✅ Core quality metrics functionality works")
        
        # Test compliance enforcement
        compliance_result = await data_steward.enforce_compliance("test_asset", ["data_retention"])
        assert isinstance(compliance_result, bool), "Compliance enforcement should work"
        print("✅ Core compliance enforcement functionality works")
        
        # Test MCP tool handlers
        mcp_result = await data_steward._mcp_create_content_policy({
            "data_type": "test_data",
            "rules": {"retention": "1_year"}
        })
        assert "content" in mcp_result, "MCP handler should return content"
        assert not mcp_result["isError"], "MCP handler should not return error"
        print("✅ MCP tool handlers work")
        
        # Test base class features
        assert hasattr(data_steward, 'get_logger'), "Should have logger from base class"
        assert hasattr(data_steward, 'get_infrastructure_abstraction'), "Should have infrastructure access"
        assert hasattr(data_steward, 'validate_access'), "Should have security mixin"
        assert hasattr(data_steward, 'record_telemetry_metric'), "Should have performance monitoring"
        assert hasattr(data_steward, 'get_module'), "Should have micro-module support"
        print("✅ New base class features integrated")
        
        # Test protocol compliance
        from data_steward_service_clean_rebuild import DataStewardServiceProtocol
        assert isinstance(data_steward, DataStewardServiceProtocol), "Should implement DataStewardServiceProtocol"
        print("✅ Protocol compliance validated")
        
        return True
        
    except Exception as e:
        print(f"❌ Data Steward Service clean rebuild test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run Data Steward Service clean rebuild test."""
    print("🚀 Testing Data Steward Service Clean Rebuild")
    print("=" * 60)
    
    try:
        result = await test_data_steward_clean_rebuild()
        
        print("\n" + "=" * 60)
        print("📊 DATA STEWARD SERVICE CLEAN REBUILD TEST SUMMARY")
        print("=" * 60)
        
        if result:
            print("🎉 DATA STEWARD SERVICE CLEAN REBUILD VALIDATED!")
            print("✅ Clean rebuild using ONLY new base and protocol construct")
            print("🔗 SOA APIs exposed for realm consumption (7 APIs)")
            print("🔧 MCP tools available for agent access (7 tools)")
            print("🏗️ Micro-module architecture integrated")
            print("🎯 New base class alignment complete")
            print("📋 Protocol compliance validated")
            print("\n🎯 CLEAN REBUILD ADVANTAGES:")
            print("   • No archived dependencies")
            print("   • No complex refactoring")
            print("   • Clean, focused implementation")
            print("   • Uses ONLY new base and protocol construct")
            print("   • All 7 core data governance methods implemented")
            print("   • Complete SOA API and MCP tool integration")
            print("\n📝 DATA GOVERNANCE CAPABILITIES:")
            print("   • Policy Management: ✅ create_content_policy, get_policy_for_content")
            print("   • Lineage Tracking: ✅ record_lineage, get_lineage")
            print("   • Data Quality: ✅ validate_schema, get_quality_metrics")
            print("   • Compliance: ✅ enforce_compliance")
            print("\n🎯 RECOMMENDATION:")
            print("   Use clean rebuild approach for remaining Smart City services!")
            return True
        else:
            print("⚠️ Data Steward Service clean rebuild needs attention")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

