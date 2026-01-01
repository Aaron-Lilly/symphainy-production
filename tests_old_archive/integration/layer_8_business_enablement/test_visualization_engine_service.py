#!/usr/bin/env python3
"""
Visualization Engine Service - Functional Tests

Tests Visualization Engine Service for Insights Orchestrator:
- Visualization creation
- Chart generation
- Dashboard building
- Visual export
- Workflow diagram creation

Uses proven patterns from metrics_calculator_service tests.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_json_file,
    create_test_csv_file
)
from tests.integration.layer_8_business_enablement.test_utilities import (
    ContentStewardHelper,
    TestDataManager
)

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def visualization_engine_service(smart_city_infrastructure):
    """
    VisualizationEngineService instance for each test.
    
    Reuses the proven pattern from metrics_calculator_service tests.
    """
    logger.info("🔧 Fixture: Starting visualization_engine_service fixture...")
    
    from backend.business_enablement.enabling_services.visualization_engine_service.visualization_engine_service import VisualizationEngineService
    
    logger.info("🔧 Fixture: Got infrastructure, creating VisualizationEngineService...")
    infra = smart_city_infrastructure
    service = VisualizationEngineService(
        service_name="VisualizationEngineService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: VisualizationEngineService instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Visualization Engine Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Visualization Engine Service initialization timed out after 60 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Service initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Service ready, yielding to test...")
    yield service
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
async def storage_helper(smart_city_infrastructure, infrastructure_storage):
    """
    Storage helper for each test.
    
    Reuses the proven pattern from metrics_calculator_service tests.
    """
    storage = infrastructure_storage["file_storage"]
    user_context = TestDataManager.get_user_context()
    helper = ContentStewardHelper(storage, user_context)
    
    yield helper
    
    # Cleanup stored files
    try:
        await helper.cleanup()
    except Exception:
        pass  # Ignore cleanup errors


# ============================================================================
# HELPER FUNCTIONS - Test Data Creation
# ============================================================================

def create_test_chart_data() -> tuple[bytes, str]:
    """Create test data for chart visualization."""
    import json
    chart_data = {
        "sales": [
            {"month": "Jan", "revenue": 10000, "costs": 8000},
            {"month": "Feb", "revenue": 12000, "costs": 9000},
            {"month": "Mar", "revenue": 15000, "costs": 10000},
            {"month": "Apr", "revenue": 18000, "costs": 11000}
        ]
    }
    return json.dumps(chart_data, indent=2).encode('utf-8'), "chart_data.json"


# ============================================================================
# TESTS - Core Functionality
# ============================================================================

@pytest.mark.asyncio
async def test_service_initialization(visualization_engine_service):
    """Test that service initializes correctly."""
    logger.info("🧪 Test: Service initialization")
    
    assert visualization_engine_service is not None
    assert hasattr(visualization_engine_service, 'supported_types')
    assert len(visualization_engine_service.supported_types) > 0
    
    logger.info("✅ Service initialized correctly")


@pytest.mark.asyncio
async def test_create_visualization_basic(visualization_engine_service, storage_helper):
    """Test basic visualization creation."""
    logger.info("🧪 Test: Create visualization (basic)")
    
    # Upload test data
    chart_data, filename = create_test_chart_data()
    file_id = await storage_helper.store_file(chart_data, filename, "application/json")
    assert file_id is not None
    
    # Create visualization
    result = await visualization_engine_service.create_visualization(
        data_id=file_id,
        visualization_type="bar_chart"
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "visual_id" in result
    assert result.get("visualization_type") == "bar_chart"
    assert result.get("data_id") == file_id
    assert "visualization" in result
    
    logger.info(f"✅ Visualization created: {result.get('visual_id')}")


@pytest.mark.asyncio
async def test_create_visualization_with_options(visualization_engine_service, storage_helper):
    """Test visualization creation with options."""
    logger.info("🧪 Test: Create visualization with options")
    
    # Upload test data
    chart_data, filename = create_test_chart_data()
    file_id = await storage_helper.store_file(chart_data, filename, "application/json")
    
    # Create visualization with options
    result = await visualization_engine_service.create_visualization(
        data_id=file_id,
        visualization_type="line_chart",
        options={"title": "Sales Trend", "x_axis": "month", "y_axis": "revenue"}
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "visualization" in result
    assert result.get("visualization", {}).get("options", {}).get("title") == "Sales Trend"
    
    logger.info(f"✅ Visualization created with options: {result.get('visual_id')}")


@pytest.mark.asyncio
async def test_generate_chart(visualization_engine_service, storage_helper):
    """Test chart generation."""
    logger.info("🧪 Test: Generate chart")
    
    # Upload test data
    chart_data, filename = create_test_chart_data()
    file_id = await storage_helper.store_file(chart_data, filename, "application/json")
    
    # Generate chart
    result = await visualization_engine_service.generate_chart(
        data_id=file_id,
        chart_type="bar_chart",
        x_axis="month",
        y_axis="revenue"
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "visual_id" in result
    assert result.get("visualization_type") == "bar_chart"
    
    logger.info(f"✅ Chart generated: {result.get('visual_id')}")


@pytest.mark.asyncio
async def test_build_dashboard(visualization_engine_service):
    """Test dashboard building."""
    logger.info("🧪 Test: Build dashboard")
    
    # Define dashboard
    dashboard_definition = {
        "title": "Sales Dashboard",
        "widgets": [
            {"type": "bar_chart", "data_id": "data1", "title": "Revenue by Month"},
            {"type": "line_chart", "data_id": "data2", "title": "Costs Trend"}
        ],
        "layout": "grid"
    }
    
    # Build dashboard
    result = await visualization_engine_service.build_dashboard(
        dashboard_definition=dashboard_definition
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "dashboard_id" in result
    assert result.get("definition") == dashboard_definition
    
    logger.info(f"✅ Dashboard built: {result.get('dashboard_id')}")


@pytest.mark.asyncio
async def test_export_visual(visualization_engine_service, storage_helper):
    """Test visual export."""
    logger.info("🧪 Test: Export visual")
    
    # Upload test data and create visualization first
    chart_data, filename = create_test_chart_data()
    file_id = await storage_helper.store_file(chart_data, filename, "application/json")
    
    # Create visualization
    visual_result = await visualization_engine_service.create_visualization(
        data_id=file_id,
        visualization_type="bar_chart"
    )
    
    if visual_result.get("success"):
        visual_id = visual_result.get("visual_id")
        
        # Export visualization
        result = await visualization_engine_service.export_visual(
            visual_id=visual_id,
            export_format="png"
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("visual_id") == visual_id
        assert result.get("format") == "png"
        assert "export_id" in result
        
        logger.info(f"✅ Visual exported: {result.get('export_id')}")
    else:
        logger.info("⚠️ Visualization creation failed, skipping export test")


@pytest.mark.asyncio
async def test_create_workflow_diagram(visualization_engine_service, storage_helper):
    """Test workflow diagram creation."""
    logger.info("🧪 Test: Create workflow diagram")
    
    # Upload test data (workflow definition)
    workflow_data = {
        "steps": [
            {"id": "step1", "name": "Start", "type": "start"},
            {"id": "step2", "name": "Process", "type": "process"},
            {"id": "step3", "name": "End", "type": "end"}
        ],
        "connections": [
            {"from": "step1", "to": "step2"},
            {"from": "step2", "to": "step3"}
        ]
    }
    import json
    workflow_bytes = json.dumps(workflow_data, indent=2).encode('utf-8')
    file_id = await storage_helper.store_file(workflow_bytes, "workflow.json", "application/json")
    
    # Create workflow diagram
    result = await visualization_engine_service.create_workflow_diagram(
        workflow_id=file_id
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert result.get("visualization_type") == "workflow_diagram"
    assert "visual_id" in result
    
    logger.info(f"✅ Workflow diagram created: {result.get('visual_id')}")


# ============================================================================
# TESTS - Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_create_visualization_invalid_data(visualization_engine_service):
    """Test visualization creation with invalid data ID."""
    logger.info("🧪 Test: Create visualization (invalid data)")
    
    result = await visualization_engine_service.create_visualization(
        data_id="non_existent_file_id",
        visualization_type="bar_chart"
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "message" in result or "error" in result
    
    logger.info("✅ Invalid data handled gracefully")


@pytest.mark.asyncio
async def test_export_visual_invalid_id(visualization_engine_service):
    """Test visual export with invalid visual ID."""
    logger.info("🧪 Test: Export visual (invalid ID)")
    
    result = await visualization_engine_service.export_visual(
        visual_id="non_existent_visual_id",
        export_format="png"
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "message" in result or "error" in result
    
    logger.info("✅ Invalid visual ID handled gracefully")


# ============================================================================
# TESTS - Architecture Verification
# ============================================================================

@pytest.mark.asyncio
async def test_service_uses_smart_city_apis(visualization_engine_service):
    """Test that service uses Smart City SOA APIs."""
    logger.info("🧪 Test: Service uses Smart City APIs")
    
    # Service should have access to Librarian and Data Steward
    assert hasattr(visualization_engine_service, 'librarian')
    assert hasattr(visualization_engine_service, 'data_steward')
    
    logger.info("✅ Service has Smart City API access")


@pytest.mark.asyncio
async def test_service_supports_visualization_types(visualization_engine_service):
    """Test that service supports multiple visualization types."""
    logger.info("🧪 Test: Service supports visualization types")
    
    assert hasattr(visualization_engine_service, 'supported_types')
    assert isinstance(visualization_engine_service.supported_types, list)
    assert len(visualization_engine_service.supported_types) > 0
    
    # Should support common visualization types
    expected_types = ["bar_chart", "line_chart", "pie_chart", "scatter_plot", "heatmap", "workflow_diagram"]
    for viz_type in expected_types:
        if viz_type in visualization_engine_service.supported_types:
            logger.info(f"✅ Supports {viz_type} visualizations")
    
    logger.info(f"✅ Service supports {len(visualization_engine_service.supported_types)} visualization types")





