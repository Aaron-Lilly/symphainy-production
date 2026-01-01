#!/usr/bin/env python3
"""
Test AGUI Refactoring - Agentic Realm Business Service

Tests the refactored AGUI Output Formatter and Schema Registry as business services
using Post Office infrastructure from Public Works Foundation.
"""

import asyncio
import sys
import os
import logging

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agui_refactoring():
    """Test the refactored AGUI business services."""
    try:
        logger.info("🧪 Testing AGUI Refactoring - Agentic Realm Business Service")
        
        # Test 1: Import AGUI Infrastructure
        logger.info("📋 Test 1: Import AGUI Infrastructure")
        
        from foundations.public_works_foundation.abstraction_contracts.agui_communication_protocol import (
            AGUIMessage, AGUIResponse, AGUIEvent
        )
        from foundations.public_works_foundation.infrastructure_adapters.websocket_adapter import WebSocketAdapter
        from foundations.public_works_foundation.infrastructure_abstractions.agui_communication_abstraction import AGUICommunicationAbstraction
        from foundations.public_works_foundation.composition_services.agui_composition_service import AGUICompositionService
        
        logger.info("✅ AGUI infrastructure imported successfully")
        
        # Test 2: Create AGUI Infrastructure
        logger.info("📋 Test 2: Create AGUI Infrastructure")
        
        # Create WebSocket adapter
        websocket_adapter = WebSocketAdapter()
        
        # Create AGUI communication abstraction
        agui_abstraction = AGUICommunicationAbstraction(websocket_adapter)
        
        # Create AGUI composition service
        agui_composition_service = AGUICompositionService(agui_abstraction)
        
        logger.info("✅ AGUI infrastructure created successfully")
        
        # Test 3: Import AGUI Business Services
        logger.info("📋 Test 3: Import AGUI Business Services")
        
        from foundations.agentic_foundation.business_services.agui_output_formatter import AGUIOutputFormatter
        from foundations.agentic_foundation.business_services.agui_schema_registry import AGUISchemaRegistry, AGUISchema, AGUIComponent
        
        logger.info("✅ AGUI business services imported successfully")
        
        # Test 4: Create AGUI Business Services
        logger.info("📋 Test 4: Create AGUI Business Services")
        
        # Create AGUI Output Formatter
        agui_formatter = AGUIOutputFormatter()
        
        # Create AGUI Schema Registry
        agui_schema_registry = AGUISchemaRegistry()
        
        logger.info("✅ AGUI business services created successfully")
        
        # Test 5: Test AGUI Output Formatter
        logger.info("📋 Test 5: Test AGUI Output Formatter")
        
        # Test formatting agent response
        response_data = {
            "title": "Test Analysis",
            "metrics": {"accuracy": 0.95, "confidence": 0.87},
            "status": "completed",
            "visualizations": [{"type": "bar_chart", "data": [1, 2, 3]}],
            "actions": [{"label": "Save", "action": "save"}]
        }
        
        format_result = await agui_formatter.format_agent_response(
            agent_name="test_agent",
            response_data=response_data,
            output_type="analysis_card"
        )
        
        if not format_result.get("success", False):
            logger.error(f"❌ AGUI formatting failed: {format_result}")
            return False
        
        logger.info("✅ AGUI Output Formatter test passed")
        
        # Test 6: Test AGUI Schema Registry
        logger.info("📋 Test 6: Test AGUI Schema Registry")
        
        # Create test schema
        test_component = AGUIComponent(
            type="analysis_card",
            title="Analysis Results",
            description="Display analysis results",
            required=True,
            properties={"metrics": "object", "status": "string"},
            examples=[{"metrics": {"accuracy": 0.95}, "status": "completed"}]
        )
        
        test_schema = AGUISchema(
            agent_name="test_agent",
            version="1.0.0",
            description="Test agent schema",
            components=[test_component],
            metadata={"author": "test", "created_at": "2024-01-01"}
        )
        
        # Register schema
        register_result = await agui_schema_registry.register_agent_schema(
            agent_name="test_agent",
            schema=test_schema
        )
        
        if not register_result.get("success", False):
            logger.error(f"❌ AGUI schema registration failed: {register_result}")
            return False
        
        # Get schema
        retrieved_schema = await agui_schema_registry.get_agent_schema("test_agent")
        
        if not retrieved_schema:
            logger.error("❌ Failed to retrieve AGUI schema")
            return False
        
        logger.info("✅ AGUI Schema Registry test passed")
        
        # Test 7: Verify Architecture
        logger.info("📋 Test 7: Verify Architecture")
        
        # Test AGUI Output Formatter health
        formatter_health = agui_formatter.get_formatter_health()
        
        if formatter_health.get("service_type") != "business_service":
            logger.error("❌ AGUI Output Formatter not properly identified as business service")
            return False
        
        if formatter_health.get("realm") != "agentic":
            logger.error("❌ AGUI Output Formatter not properly identified as agentic realm")
            return False
        
        # Test AGUI Schema Registry health
        registry_health = agui_schema_registry.get_registry_health()
        
        if registry_health.get("service_type") != "business_service":
            logger.error("❌ AGUI Schema Registry not properly identified as business service")
            return False
        
        if registry_health.get("realm") != "agentic":
            logger.error("❌ AGUI Schema Registry not properly identified as agentic realm")
            return False
        
        logger.info("✅ Architecture verification passed")
        
        # Test 8: Test Business Metrics
        logger.info("📋 Test 8: Test Business Metrics")
        
        # Test formatter metrics
        formatter_metrics = agui_formatter.get_business_metrics()
        
        if formatter_metrics.get("total_outputs_generated", 0) == 0:
            logger.error("❌ AGUI Output Formatter metrics not updated")
            return False
        
        # Test registry metrics
        registry_metrics = agui_schema_registry.get_business_metrics()
        
        if registry_metrics.get("total_schemas_registered", 0) == 0:
            logger.error("❌ AGUI Schema Registry metrics not updated")
            return False
        
        logger.info("✅ Business metrics test passed")
        
        logger.info("🎉 AGUI refactoring test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ AGUI refactoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run AGUI refactoring test."""
    logger.info("🚀 Starting AGUI Refactoring Test")
    
    success = await test_agui_refactoring()
    
    if success:
        logger.info("🎉 AGUI refactoring test passed!")
        return True
    else:
        logger.error("❌ AGUI refactoring test failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


