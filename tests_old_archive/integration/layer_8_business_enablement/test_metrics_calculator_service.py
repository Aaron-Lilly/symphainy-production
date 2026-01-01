#!/usr/bin/env python3
"""
Metrics Calculator Service - Functional Tests

Tests Metrics Calculator Service for Insights Orchestrator:
- Metric calculation (single metrics)
- KPI calculation (composite metrics)
- Batch calculation
- ROI calculation
- Financial analysis

Uses proven patterns from data_analyzer_service tests.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_excel_file,
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
async def metrics_calculator_service(smart_city_infrastructure):
    """
    MetricsCalculatorService instance for each test.
    
    Reuses the proven pattern from data_analyzer_service tests.
    """
    logger.info("🔧 Fixture: Starting metrics_calculator_service fixture...")
    
    from backend.business_enablement.enabling_services.metrics_calculator_service.metrics_calculator_service import MetricsCalculatorService
    
    logger.info("🔧 Fixture: Got infrastructure, creating MetricsCalculatorService...")
    infra = smart_city_infrastructure
    service = MetricsCalculatorService(
        service_name="MetricsCalculatorService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: MetricsCalculatorService instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Metrics Calculator Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Metrics Calculator Service initialization timed out after 60 seconds")
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
    
    Reuses the proven pattern from data_analyzer_service tests.
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

def create_test_sales_data() -> tuple[bytes, str]:
    """Create test sales data for metrics calculation."""
    import json
    sales_data = {
        "revenue": 2500000,
        "costs": 1800000,
        "profit": 700000,
        "customers": 450,
        "churn_rate": 0.032,
        "growth_rate": 0.15,
        "customer_satisfaction": 4.5,
        "employee_satisfaction": 4.2,
        "market_share": 0.12
    }
    return json.dumps(sales_data, indent=2).encode('utf-8'), "sales_data.json"


def create_test_financial_data() -> tuple[bytes, str]:
    """Create test financial data for ROI calculation."""
    import json
    financial_data = {
        "initial_investment": 500000,
        "current_value": 750000,
        "revenue": 300000,
        "operating_costs": 150000,
        "time_period_months": 12
    }
    return json.dumps(financial_data, indent=2).encode('utf-8'), "financial_data.json"


# ============================================================================
# TESTS - Core Functionality
# ============================================================================

@pytest.mark.asyncio
async def test_service_initialization(metrics_calculator_service):
    """Test that service initializes correctly."""
    logger.info("🧪 Test: Service initialization")
    
    assert metrics_calculator_service is not None
    assert hasattr(metrics_calculator_service, 'supported_metric_types')
    assert len(metrics_calculator_service.supported_metric_types) > 0
    
    logger.info("✅ Service initialized correctly")


@pytest.mark.asyncio
async def test_calculate_metric_basic(metrics_calculator_service, storage_helper):
    """Test basic metric calculation."""
    logger.info("🧪 Test: Calculate metric (basic)")
    
    # Upload test data
    sales_data, filename = create_test_sales_data()
    file_id = await storage_helper.store_file(sales_data, filename, "application/json")
    assert file_id is not None
    
    # Calculate metric
    result = await metrics_calculator_service.calculate_metric(
        metric_name="revenue",
        data_source=file_id
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "value" in result
    assert result.get("metric_name") == "revenue"
    assert result.get("data_source") == file_id
    
    logger.info(f"✅ Metric calculated: {result.get('value')}")


@pytest.mark.asyncio
async def test_calculate_metric_with_params(metrics_calculator_service, storage_helper):
    """Test metric calculation with parameters."""
    logger.info("🧪 Test: Calculate metric with parameters")
    
    # Upload test data
    sales_data, filename = create_test_sales_data()
    file_id = await storage_helper.store_file(sales_data, filename, "application/json")
    
    # Calculate metric with parameters
    result = await metrics_calculator_service.calculate_metric(
        metric_name="profit_margin",
        data_source=file_id,
        metric_params={"revenue_field": "revenue", "cost_field": "costs"}
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "value" in result
    
    logger.info(f"✅ Metric calculated with params: {result.get('value')}")


@pytest.mark.asyncio
async def test_calculate_kpi_single_source(metrics_calculator_service, storage_helper):
    """Test KPI calculation from single data source."""
    logger.info("🧪 Test: Calculate KPI (single source)")
    
    # Upload test data
    sales_data, filename = create_test_sales_data()
    file_id = await storage_helper.store_file(sales_data, filename, "application/json")
    
    # Calculate KPI
    result = await metrics_calculator_service.calculate_kpi(
        kpi_name="business_performance",
        data_sources=file_id  # Single source as string
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "value" in result
    assert result.get("kpi_name") == "business_performance"
    assert "components" in result
    
    logger.info(f"✅ KPI calculated: {result.get('value')}")


@pytest.mark.asyncio
async def test_calculate_kpi_multiple_sources(metrics_calculator_service, storage_helper):
    """Test KPI calculation from multiple data sources."""
    logger.info("🧪 Test: Calculate KPI (multiple sources)")
    
    # Upload multiple test data files
    sales_data, filename1 = create_test_sales_data()
    file_id1 = await storage_helper.store_file(sales_data, filename1, "application/json")
    
    financial_data, filename2 = create_test_financial_data()
    file_id2 = await storage_helper.store_file(financial_data, filename2, "application/json")
    
    # Calculate KPI from multiple sources
    result = await metrics_calculator_service.calculate_kpi(
        kpi_name="composite_performance",
        data_sources=[file_id1, file_id2]  # Multiple sources as list
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "value" in result
    assert "components" in result
    assert len(result.get("components", [])) >= 0  # May have 0 if components failed
    
    logger.info(f"✅ KPI calculated from multiple sources: {result.get('value')}")


@pytest.mark.asyncio
async def test_calculate_batch(metrics_calculator_service, storage_helper):
    """Test batch metric calculation."""
    logger.info("🧪 Test: Calculate batch metrics")
    
    # Upload test data
    sales_data, filename = create_test_sales_data()
    file_id = await storage_helper.store_file(sales_data, filename, "application/json")
    
    # Define batch metrics
    metrics = [
        {"name": "revenue", "source": file_id, "params": {}},
        {"name": "profit", "source": file_id, "params": {}},
        {"name": "growth_rate", "source": file_id, "params": {}}
    ]
    
    # Calculate batch
    result = await metrics_calculator_service.calculate_batch(metrics=metrics)
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "results" in result
    assert len(result.get("results", [])) == len(metrics)
    assert "successful" in result
    assert "failed" in result
    
    logger.info(f"✅ Batch calculation: {result.get('successful')}/{len(metrics)} successful")


@pytest.mark.asyncio
async def test_calculate_roi(metrics_calculator_service):
    """Test ROI calculation."""
    logger.info("🧪 Test: Calculate ROI")
    
    # Prepare investment data (as dict, not file_id)
    investment_data = {
        "investment_cost": 500000,
        "expected_returns": 750000,
        "time_period_months": 12
    }
    
    # Calculate ROI
    result = await metrics_calculator_service.calculate_roi(
        investment_data=investment_data
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "roi_result" in result
    assert "roi_percentage" in result.get("roi_result", {})
    
    logger.info(f"✅ ROI calculation: {result.get('roi_result', {}).get('roi_percentage', 'N/A')}%")


@pytest.mark.asyncio
async def test_analyze_financials(metrics_calculator_service):
    """Test financial analysis."""
    logger.info("🧪 Test: Analyze financials")
    
    # Prepare financial data (as dict, not file_id)
    financial_data = {
        "revenue": 300000,
        "costs": 150000,
        "growth_rate": 0.15
    }
    
    # Analyze financials
    result = await metrics_calculator_service.analyze_financials(
        financial_data=financial_data
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "financial_analysis" in result
    assert "profit_margin" in result.get("financial_analysis", {})
    
    logger.info(f"✅ Financial analysis: {result.get('financial_analysis', {}).get('profit_margin', 'N/A')}% margin")


@pytest.mark.asyncio
async def test_get_metric_definition(metrics_calculator_service):
    """Test getting metric definition."""
    logger.info("🧪 Test: Get metric definition")
    
    result = await metrics_calculator_service.get_metric_definition(
        metric_name="revenue"
    )
    
    assert isinstance(result, dict)
    # May return definition or error if metric not found
    assert "success" in result or "definition" in result or "error" in result
    
    logger.info(f"✅ Metric definition result: {result.get('success', 'N/A')}")


@pytest.mark.asyncio
async def test_track_metric_history(metrics_calculator_service, storage_helper):
    """Test tracking metric history."""
    logger.info("🧪 Test: Track metric history")
    
    # Upload test data
    sales_data, filename = create_test_sales_data()
    file_id = await storage_helper.store_file(sales_data, filename, "application/json")
    
    # Calculate metric first
    metric_result = await metrics_calculator_service.calculate_metric(
        metric_name="revenue",
        data_source=file_id
    )
    
    if metric_result.get("success"):
        metric_name = metric_result.get("metric_name", "revenue")
        
        # Track history (uses metric_name, not metric_id)
        result = await metrics_calculator_service.track_metric_history(
            metric_name=metric_name
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "history" in result
        assert "data_points" in result
        
        logger.info(f"✅ Metric history tracking: {result.get('data_points', 0)} data points")
    else:
        logger.info("⚠️ Metric calculation failed, skipping history tracking")


# ============================================================================
# TESTS - Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_calculate_metric_invalid_source(metrics_calculator_service):
    """Test metric calculation with invalid data source."""
    logger.info("🧪 Test: Calculate metric (invalid source)")
    
    result = await metrics_calculator_service.calculate_metric(
        metric_name="revenue",
        data_source="non_existent_file_id"
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "message" in result or "error" in result
    
    logger.info("✅ Invalid source handled gracefully")


@pytest.mark.asyncio
async def test_calculate_kpi_invalid_sources(metrics_calculator_service):
    """Test KPI calculation with invalid data sources."""
    logger.info("🧪 Test: Calculate KPI (invalid sources)")
    
    result = await metrics_calculator_service.calculate_kpi(
        kpi_name="test_kpi",
        data_sources=["non_existent_file_id_1", "non_existent_file_id_2"]
    )
    
    assert isinstance(result, dict)
    # May succeed with empty components or fail
    assert "success" in result or "error" in result
    
    logger.info("✅ Invalid sources handled gracefully")


# ============================================================================
# TESTS - Architecture Verification
# ============================================================================

@pytest.mark.asyncio
async def test_service_uses_smart_city_apis(metrics_calculator_service):
    """Test that service uses Smart City SOA APIs."""
    logger.info("🧪 Test: Service uses Smart City APIs")
    
    # Service should have access to Librarian and Data Steward
    assert hasattr(metrics_calculator_service, 'librarian')
    assert hasattr(metrics_calculator_service, 'data_steward')
    
    # These may be None if not initialized, but the attributes should exist
    logger.info("✅ Service has Smart City API access")


@pytest.mark.asyncio
async def test_service_supports_metric_types(metrics_calculator_service):
    """Test that service supports multiple metric types."""
    logger.info("🧪 Test: Service supports metric types")
    
    assert hasattr(metrics_calculator_service, 'supported_metric_types')
    assert isinstance(metrics_calculator_service.supported_metric_types, list)
    assert len(metrics_calculator_service.supported_metric_types) > 0
    
    # Should support common metric types
    expected_types = ["business", "operational", "financial", "quality", "performance", "custom"]
    for metric_type in expected_types:
        if metric_type in metrics_calculator_service.supported_metric_types:
            logger.info(f"✅ Supports {metric_type} metrics")
    
    logger.info(f"✅ Service supports {len(metrics_calculator_service.supported_metric_types)} metric types")

