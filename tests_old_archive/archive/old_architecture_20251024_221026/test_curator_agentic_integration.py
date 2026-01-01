#!/usr/bin/env python3
"""
Test Curator Foundation Agentic Integration

Comprehensive test suite for the enhanced Curator Foundation Service with agentic integration.
Tests all 8 micro-services including the 4 new agentic-specific services.

WHAT (Test Role): I validate Curator Foundation integration with agentic dimension
HOW (Test Implementation): I test all micro-services and their integration with agentic capabilities
"""

import asyncio
import sys
import os
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import using importlib to handle hyphenated module names
import importlib.util

# Load FoundationServices
foundation_spec = importlib.util.spec_from_file_location(
    "foundation_services", 
    "symphainy-platform/bases/foundation_services.py"
)
foundation_module = importlib.util.module_from_spec(foundation_spec)
foundation_spec.loader.exec_module(foundation_module)
FoundationServices = foundation_module.FoundationServices

# Load PublicWorksFoundationService
public_works_spec = importlib.util.spec_from_file_location(
    "public_works_foundation_service", 
    "symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py"
)
public_works_module = importlib.util.module_from_spec(public_works_spec)
public_works_spec.loader.exec_module(public_works_module)
PublicWorksFoundationService = public_works_module.PublicWorksFoundationService

# Load CuratorFoundationServiceAgentic
curator_spec = importlib.util.spec_from_file_location(
    "curator_foundation_service_agentic", 
    "symphainy-platform/foundations/curator_foundation/curator_foundation_service_agentic.py"
)
curator_module = importlib.util.module_from_spec(curator_spec)
curator_spec.loader.exec_module(curator_module)
CuratorFoundationServiceAgentic = curator_module.CuratorFoundationServiceAgentic


async def test_curator_foundation_initialization():
    """Test Curator Foundation Service initialization."""
    print("🧪 Testing Curator Foundation Service Initialization...")
    
    try:
        # Initialize Foundation Services
        foundation_services = FoundationServices("test_curator")
        
        # Initialize Public Works Foundation
        public_works_foundation = PublicWorksFoundationService(foundation_services)
        await public_works_foundation.initialize()
        
        # Initialize Curator Foundation with Agentic Integration
        curator_foundation = CuratorFoundationServiceAgentic(
            foundation_services, public_works_foundation
        )
        await curator_foundation.initialize()
        
        # Verify all micro-services are initialized
        assert curator_foundation.capability_registry is not None
        assert curator_foundation.pattern_validation is not None
        assert curator_foundation.antipattern_detection is not None
        assert curator_foundation.documentation_generation is not None
        assert curator_foundation.agent_capability_registry is not None
        assert curator_foundation.agent_specialization_management is not None
        assert curator_foundation.agui_schema_documentation is not None
        assert curator_foundation.agent_health_monitoring is not None
        
        print("✅ Curator Foundation Service Initialization test passed")
        return curator_foundation
        
    except Exception as e:
        print(f"❌ Curator Foundation Service Initialization test failed: {e}")
        raise


async def test_agent_registration_with_curator(curator_foundation):
    """Test agent registration with Curator Foundation."""
    print("🧪 Testing Agent Registration with Curator Foundation...")
    
    try:
        # Test agent configuration
        agent_config = {
            "capabilities": [
                {
                    "name": "data_analysis",
                    "type": "analysis",
                    "description": "Advanced data analysis capabilities",
                    "parameters": {"max_rows": 10000, "supported_formats": ["csv", "json"]},
                    "version": "1.0.0",
                    "status": "active"
                },
                {
                    "name": "insight_generation",
                    "type": "insights",
                    "description": "Generate business insights from data",
                    "parameters": {"confidence_threshold": 0.8},
                    "version": "1.0.0",
                    "status": "active"
                }
            ],
            "pillar": "insights",
            "specialization": "data_analyst",
            "specialization_config": {
                "id": "data_analyst",
                "name": "Data Analyst",
                "pillar": "insights",
                "description": "Specialized in data analysis and insight generation",
                "capabilities": ["data_analysis", "insight_generation"],
                "system_prompt_template": "You are a data analyst specializing in...",
                "expertise_level": "advanced",
                "version": "1.0.0",
                "status": "active"
            }
        }
        
        # Register agent
        success = await curator_foundation.register_agent_with_curator(
            "test_agent_001", "Test Data Analyst Agent", agent_config
        )
        
        assert success, "Agent registration should succeed"
        
        print("✅ Agent Registration with Curator Foundation test passed")
        
    except Exception as e:
        print(f"❌ Agent Registration with Curator Foundation test failed: {e}")
        raise


async def test_agent_capability_registry(curator_foundation):
    """Test Agent Capability Registry Service."""
    print("🧪 Testing Agent Capability Registry Service...")
    
    try:
        # Get agent capability report
        capability_report = await curator_foundation.agent_capability_registry.get_agent_capability_report("test_agent_001")
        
        assert capability_report is not None, "Capability report should exist"
        assert capability_report.agent_id == "test_agent_001", "Agent ID should match"
        assert capability_report.total_capabilities == 2, "Should have 2 capabilities"
        assert capability_report.active_capabilities == 2, "Should have 2 active capabilities"
        assert capability_report.pillar == "insights", "Should be in insights pillar"
        
        # Test capability usage update
        usage_success = await curator_foundation.agent_capability_registry.update_capability_usage(
            "data_analysis", "test_agent_001", {"rows_processed": 1000}
        )
        assert usage_success, "Usage update should succeed"
        
        # Get capability analytics
        analytics = await curator_foundation.agent_capability_registry.get_capability_analytics()
        assert analytics is not None, "Analytics should exist"
        assert analytics["total_agents"] >= 1, "Should have at least 1 agent"
        
        print("✅ Agent Capability Registry Service test passed")
        
    except Exception as e:
        print(f"❌ Agent Capability Registry Service test failed: {e}")
        raise


async def test_agent_specialization_management(curator_foundation):
    """Test Agent Specialization Management Service."""
    print("🧪 Testing Agent Specialization Management Service...")
    
    try:
        # Get agent specialization
        specialization = await curator_foundation.agent_specialization_management.get_agent_specialization("test_agent_001")
        
        assert specialization is not None, "Specialization should exist"
        assert specialization.agent_id == "test_agent_001", "Agent ID should match"
        assert specialization.specialization_id == "data_analyst", "Specialization ID should match"
        assert specialization.pillar == "insights", "Should be in insights pillar"
        
        # Test specialization usage update
        usage_success = await curator_foundation.agent_specialization_management.update_specialization_usage(
            "test_agent_001", success=True, capability_used="data_analysis"
        )
        assert usage_success, "Usage update should succeed"
        
        # Get specialization analytics
        spec_analytics = await curator_foundation.agent_specialization_management.get_specialization_analytics("data_analyst")
        assert spec_analytics is not None, "Specialization analytics should exist"
        assert spec_analytics.total_agents >= 1, "Should have at least 1 agent"
        
        # Get pillar specializations
        pillar_specs = await curator_foundation.agent_specialization_management.get_pillar_specializations("insights")
        assert "data_analyst" in pillar_specs, "Data analyst should be in insights pillar"
        
        print("✅ Agent Specialization Management Service test passed")
        
    except Exception as e:
        print(f"❌ Agent Specialization Management Service test failed: {e}")
        raise


async def test_agui_schema_documentation(curator_foundation):
    """Test AGUI Schema Documentation Service."""
    print("🧪 Testing AGUI Schema Documentation Service...")
    
    try:
        # Generate documentation for different types
        api_doc = await curator_foundation.agui_schema_documentation.generate_agent_documentation(
            "Test Data Analyst Agent", "api"
        )
        
        user_guide_doc = await curator_foundation.agui_schema_documentation.generate_agent_documentation(
            "Test Data Analyst Agent", "user_guide"
        )
        
        # Get agent documentation
        documentation = await curator_foundation.agui_schema_documentation.get_agent_documentation(
            "Test Data Analyst Agent"
        )
        
        assert len(documentation) >= 2, "Should have at least 2 documentation types"
        
        # Get documentation report
        doc_report = await curator_foundation.agui_schema_documentation.get_documentation_report()
        assert doc_report is not None, "Documentation report should exist"
        assert doc_report.total_agents >= 1, "Should have at least 1 agent documented"
        
        # Get documentation quality report
        quality_report = await curator_foundation.agui_schema_documentation.get_documentation_quality_report()
        assert quality_report is not None, "Quality report should exist"
        
        print("✅ AGUI Schema Documentation Service test passed")
        
    except Exception as e:
        print(f"❌ AGUI Schema Documentation Service test failed: {e}")
        raise


async def test_agent_health_monitoring(curator_foundation):
    """Test Agent Health Monitoring Service."""
    print("🧪 Testing Agent Health Monitoring Service...")
    
    try:
        # Get agent health
        health_metrics = await curator_foundation.agent_health_monitoring.get_agent_health("test_agent_001")
        
        assert health_metrics is not None, "Health metrics should exist"
        assert health_metrics.agent_id == "test_agent_001", "Agent ID should match"
        assert health_metrics.overall_status in ["healthy", "degraded", "unhealthy", "unknown"], "Status should be valid"
        
        # Get agent health report
        health_report = await curator_foundation.agent_health_monitoring.get_agent_health_report("test_agent_001")
        
        assert health_report is not None, "Health report should exist"
        assert health_report.agent_id == "test_agent_001", "Agent ID should match"
        assert 0 <= health_report.performance_score <= 100, "Performance score should be 0-100"
        assert 0 <= health_report.reliability_score <= 100, "Reliability score should be 0-100"
        assert 0 <= health_report.availability_score <= 100, "Availability score should be 0-100"
        
        # Get health summary
        health_summary = await curator_foundation.agent_health_monitoring.get_health_summary()
        assert health_summary is not None, "Health summary should exist"
        assert health_summary["total_agents"] >= 1, "Should have at least 1 agent monitored"
        
        print("✅ Agent Health Monitoring Service test passed")
        
    except Exception as e:
        print(f"❌ Agent Health Monitoring Service test failed: {e}")
        raise


async def test_agent_curator_report(curator_foundation):
    """Test comprehensive agent Curator report."""
    print("🧪 Testing Agent Curator Report...")
    
    try:
        # Get comprehensive agent report
        agent_report = await curator_foundation.get_agent_curator_report("test_agent_001")
        
        assert agent_report is not None, "Agent report should exist"
        assert agent_report["agent_id"] == "test_agent_001", "Agent ID should match"
        assert agent_report["capability_report"] is not None, "Capability report should exist"
        assert agent_report["specialization"] is not None, "Specialization should exist"
        assert agent_report["documentation"] is not None, "Documentation should exist"
        assert agent_report["health_report"] is not None, "Health report should exist"
        
        print("✅ Agent Curator Report test passed")
        
    except Exception as e:
        print(f"❌ Agent Curator Report test failed: {e}")
        raise


async def test_agentic_dimension_summary(curator_foundation):
    """Test agentic dimension summary."""
    print("🧪 Testing Agentic Dimension Summary...")
    
    try:
        # Get agentic dimension summary
        summary = await curator_foundation.get_agentic_dimension_summary()
        
        assert summary is not None, "Summary should exist"
        assert summary["total_agents"] >= 1, "Should have at least 1 agent"
        assert "capability_summary" in summary, "Should have capability summary"
        assert "specialization_summary" in summary, "Should have specialization summary"
        assert "documentation_summary" in summary, "Should have documentation summary"
        assert "health_summary" in summary, "Should have health summary"
        
        print("✅ Agentic Dimension Summary test passed")
        
    except Exception as e:
        print(f"❌ Agentic Dimension Summary test failed: {e}")
        raise


async def test_agent_usage_update(curator_foundation):
    """Test agent usage update across all services."""
    print("🧪 Testing Agent Usage Update...")
    
    try:
        # Update agent usage
        usage_success = await curator_foundation.update_agent_usage(
            "test_agent_001", "data_analysis", success=True, 
            usage_data={"rows_processed": 5000, "processing_time_ms": 2500}
        )
        
        assert usage_success, "Usage update should succeed"
        
        print("✅ Agent Usage Update test passed")
        
    except Exception as e:
        print(f"❌ Agent Usage Update test failed: {e}")
        raise


async def test_curator_foundation_status(curator_foundation):
    """Test Curator Foundation status and health check."""
    print("🧪 Testing Curator Foundation Status...")
    
    try:
        # Get status
        status = await curator_foundation.get_status()
        
        assert status is not None, "Status should exist"
        assert status["service_name"] == "curator_foundation_agentic", "Service name should match"
        assert status["overall_status"] in ["healthy", "degraded"], "Status should be valid"
        assert "core_services" in status, "Should have core services status"
        assert "agentic_services" in status, "Should have agentic services status"
        assert status["total_services"] == 8, "Should have 8 total services"
        
        # Run health check
        health_check = await curator_foundation.run_health_check()
        
        assert health_check is not None, "Health check should exist"
        assert health_check["overall_health"] in ["healthy", "degraded"], "Health should be valid"
        assert "agentic_dimension" in health_check, "Should have agentic dimension info"
        
        print("✅ Curator Foundation Status test passed")
        
    except Exception as e:
        print(f"❌ Curator Foundation Status test failed: {e}")
        raise


async def test_multiple_agents_registration(curator_foundation):
    """Test registration of multiple agents with different specializations."""
    print("🧪 Testing Multiple Agents Registration...")
    
    try:
        # Register content agent
        content_agent_config = {
            "capabilities": [
                {
                    "name": "content_analysis",
                    "type": "analysis",
                    "description": "Content analysis capabilities",
                    "version": "1.0.0",
                    "status": "active"
                }
            ],
            "pillar": "content",
            "specialization": "content_analyst",
            "specialization_config": {
                "id": "content_analyst",
                "name": "Content Analyst",
                "pillar": "content",
                "description": "Specialized in content analysis",
                "capabilities": ["content_analysis"],
                "expertise_level": "intermediate",
                "version": "1.0.0",
                "status": "active"
            }
        }
        
        content_success = await curator_foundation.register_agent_with_curator(
            "test_agent_002", "Test Content Analyst Agent", content_agent_config
        )
        assert content_success, "Content agent registration should succeed"
        
        # Register operations agent
        operations_agent_config = {
            "capabilities": [
                {
                    "name": "workflow_optimization",
                    "type": "optimization",
                    "description": "Workflow optimization capabilities",
                    "version": "1.0.0",
                    "status": "active"
                }
            ],
            "pillar": "operations",
            "specialization": "operations_optimizer",
            "specialization_config": {
                "id": "operations_optimizer",
                "name": "Operations Optimizer",
                "pillar": "operations",
                "description": "Specialized in operations optimization",
                "capabilities": ["workflow_optimization"],
                "expertise_level": "advanced",
                "version": "1.0.0",
                "status": "active"
            }
        }
        
        operations_success = await curator_foundation.register_agent_with_curator(
            "test_agent_003", "Test Operations Optimizer Agent", operations_agent_config
        )
        assert operations_success, "Operations agent registration should succeed"
        
        # Get updated agentic dimension summary
        summary = await curator_foundation.get_agentic_dimension_summary()
        assert summary["total_agents"] == 3, "Should have 3 agents total"
        
        # Verify pillar distribution
        pillar_dist = summary["capability_summary"]["capabilities_by_pillar"]
        assert "insights" in pillar_dist, "Should have insights pillar"
        assert "content" in pillar_dist, "Should have content pillar"
        assert "operations" in pillar_dist, "Should have operations pillar"
        
        print("✅ Multiple Agents Registration test passed")
        
    except Exception as e:
        print(f"❌ Multiple Agents Registration test failed: {e}")
        raise


async def main():
    """Run all Curator Foundation Agentic Integration tests."""
    print("🚀 Starting Curator Foundation Agentic Integration Tests...")
    print("=" * 80)
    
    try:
        # Initialize Curator Foundation
        curator_foundation = await test_curator_foundation_initialization()
        
        # Test agent registration
        await test_agent_registration_with_curator(curator_foundation)
        
        # Test individual agentic services
        await test_agent_capability_registry(curator_foundation)
        await test_agent_specialization_management(curator_foundation)
        await test_agui_schema_documentation(curator_foundation)
        await test_agent_health_monitoring(curator_foundation)
        
        # Test integration features
        await test_agent_curator_report(curator_foundation)
        await test_agentic_dimension_summary(curator_foundation)
        await test_agent_usage_update(curator_foundation)
        
        # Test multiple agents
        await test_multiple_agents_registration(curator_foundation)
        
        # Test status and health
        await test_curator_foundation_status(curator_foundation)
        
        print("=" * 80)
        print("✅ All Curator Foundation Agentic Integration Tests Passed!")
        print("🎉 Curator Foundation successfully integrated with agentic dimension!")
        print("🔧 All 8 micro-services working correctly")
        print("🏗️ Agentic capabilities properly managed and monitored")
        print("📊 Comprehensive reporting and analytics functional")
        print("🌐 Multi-agent support with pillar-based organization")
        
    except Exception as e:
        print("=" * 80)
        print(f"❌ Curator Foundation Agentic Integration Tests Failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
