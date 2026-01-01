#!/usr/bin/env python3
"""
Export Formatter Service - Functional Tests

Tests ExportFormatterService with lessons learned from previous testing:
- Reuses proven infrastructure fixture patterns
- Applies timeout protections
- Focuses on service functionality (not infrastructure issues)
- Tests core SOA API methods with realistic data

Uses proper fixtures, timeouts, and applies all lessons learned.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_json_file,
    create_test_csv_file,
    create_test_excel_file
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
async def export_formatter_service(smart_city_infrastructure):
    """
    ExportFormatterService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    Reuses the proven pattern from previous service tests.
    """
    logger.info("🔧 Fixture: Starting export_formatter_service fixture...")
    
    from backend.business_enablement.enabling_services.export_formatter_service.export_formatter_service import ExportFormatterService
    
    logger.info("🔧 Fixture: Got infrastructure, creating ExportFormatterService...")
    infra = smart_city_infrastructure
    service = ExportFormatterService(
        service_name="ExportFormatterService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: ExportFormatterService instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Export Formatter Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Export Formatter Service initialization timed out after 60 seconds")
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
    
    Reuses the proven pattern from previous service tests.
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
# FUNCTIONAL TESTS - Core SOA API Methods
# ============================================================================

@pytest.mark.asyncio
async def test_export_data_json(export_formatter_service, storage_helper):
    """Test exporting data to JSON format."""
    logger.info("🧪 Test: test_export_data_json")
    
    # 1. Create and store test data
    test_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "balance": 1000.50
    }
    
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="test_data.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Export data
    user_context = TestDataManager.get_user_context()
    result = await export_formatter_service.export_data(
        data_id=data_id,
        export_format="json",
        options=None,
        user_context=user_context
    )
    
    # 3. Assertions
    logger.info(f"✅ Export result: {result}")
    assert result.get("success") is True, f"Export should succeed. Result: {result}"
    assert result.get("source_data_id") == data_id, "Result should include source_data_id"
    assert result.get("export_format") == "json", "Export format should be json"
    assert "export_id" in result, "Result should include export_id"
    assert "formatted_data" in result, "Result should include formatted_data"


@pytest.mark.asyncio
async def test_export_data_csv(export_formatter_service, storage_helper):
    """Test exporting data to CSV format."""
    logger.info("🧪 Test: test_export_data_csv")
    
    # 1. Create and store test data
    test_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }
    
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="test_data.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Export data
    user_context = TestDataManager.get_user_context()
    result = await export_formatter_service.export_data(
        data_id=data_id,
        export_format="csv",
        options=None,
        user_context=user_context
    )
    
    # 3. Assertions
    logger.info(f"✅ Export result: {result}")
    assert result.get("success") is True, f"Export should succeed. Result: {result}"
    assert result.get("source_data_id") == data_id, "Result should include source_data_id"
    assert result.get("export_format") == "csv", "Export format should be csv"
    assert "export_id" in result, "Result should include export_id"


@pytest.mark.asyncio
async def test_export_data_xml(export_formatter_service, storage_helper):
    """Test exporting data to XML format."""
    logger.info("🧪 Test: test_export_data_xml")
    
    # 1. Create and store test data
    test_data = {"name": "John", "age": 30}
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="test_data.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Export data
    user_context = TestDataManager.get_user_context()
    result = await export_formatter_service.export_data(
        data_id=data_id,
        export_format="xml",
        options=None,
        user_context=user_context
    )
    
    # 3. Assertions
    logger.info(f"✅ Export result: {result}")
    assert result.get("success") is True, f"Export should succeed. Result: {result}"
    assert result.get("export_format") == "xml", "Export format should be xml"


@pytest.mark.asyncio
async def test_format_export(export_formatter_service):
    """Test format_export method (direct data formatting)."""
    logger.info("🧪 Test: test_format_export")
    
    # 1. Prepare test data
    test_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }
    
    # 2. Format export
    user_context = TestDataManager.get_user_context()
    result = await export_formatter_service.format_export(
        data=test_data,
        target_format="json",
        user_context=user_context
    )
    
    # 3. Assertions
    logger.info(f"✅ Format export result: {result}")
    assert result.get("success") is True, f"Format export should succeed. Result: {result}"
    assert result.get("target_format") == "json", "Target format should be json"
    assert "formatted_data" in result, "Result should include formatted_data"


@pytest.mark.asyncio
async def test_batch_export(export_formatter_service, storage_helper):
    """Test batch export functionality."""
    logger.info("🧪 Test: test_batch_export")
    
    # 1. Create and store multiple test data files
    data_ids = []
    for i in range(3):
        test_data = {"id": i, "name": f"Item {i}", "value": i * 10}
        json_bytes = create_test_json_file(test_data)
        data_id = await storage_helper.store_file(
            file_data=json_bytes,
            filename=f"batch_test_{i}.json",
            content_type="application/json"
        )
        data_ids.append(data_id)
        logger.info(f"✅ Stored test data {i} with ID: {data_id}")
    
    # 2. Prepare batch export requests
    exports = [
        {"data_id": data_id, "export_format": "json", "options": None}
        for data_id in data_ids
    ]
    
    # 3. Batch export
    user_context = TestDataManager.get_user_context()
    result = await export_formatter_service.batch_export(
        exports=exports,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Batch export result: {result}")
    assert result.get("success") is True, f"Batch export should succeed. Result: {result}"
    assert "results" in result or "exports" in result, "Result should include batch export results"
    results_list = result.get("results", result.get("exports", []))
    assert len(results_list) == len(data_ids), f"Should export all data items. Expected {len(data_ids)}, got {len(results_list)}"


@pytest.mark.asyncio
async def test_get_export_formats(export_formatter_service):
    """Test getting supported export formats."""
    logger.info("🧪 Test: test_get_export_formats")
    
    # 1. Get export formats
    result = await export_formatter_service.get_export_formats()
    
    # 2. Assertions
    logger.info(f"✅ Export formats result: {result}")
    assert result.get("success") is True, f"Get export formats should succeed. Result: {result}"
    # The service returns supported_formats directly or in a formats key
    formats = result.get("formats", result.get("supported_formats", []))
    if not formats:
        # If not in result, check service attribute
        formats = export_formatter_service.supported_formats
    assert isinstance(formats, list), f"Formats should be a list. Got: {type(formats)}"
    assert len(formats) > 0, "Should support at least one export format"
    
    # Check for expected formats
    expected_formats = ["json", "csv", "xml", "excel", "pdf"]
    for expected_format in expected_formats:
        assert expected_format in formats, f"Should support {expected_format} format. Available: {formats}"


@pytest.mark.asyncio
async def test_validate_export(export_formatter_service, storage_helper):
    """Test export validation."""
    logger.info("🧪 Test: test_validate_export")
    
    # 1. Create and store test data, then export it
    test_data = {"name": "John", "age": 30}
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="validate_test.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Export the data first to get an export_id
    user_context = TestDataManager.get_user_context()
    export_result = await export_formatter_service.export_data(
        data_id=data_id,
        export_format="json",
        options=None,
        user_context=user_context
    )
    export_id = export_result.get("export_id")
    assert export_id is not None, "Export should return an export_id"
    logger.info(f"✅ Created export with ID: {export_id}")
    
    # 3. Validate export
    result = await export_formatter_service.validate_export(
        export_id=export_id,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Export validation result: {result}")
    assert result.get("success") is True, f"Export validation should succeed. Result: {result}"
    assert result.get("export_id") == export_id, "Result should include export_id"
    assert "is_valid" in result or "valid" in result, "Result should include validation status"


# ============================================================================
# ARCHITECTURAL TESTS - Verify Service Structure
# ============================================================================

@pytest.mark.asyncio
async def test_service_initialization(export_formatter_service):
    """Test that service initializes correctly."""
    logger.info("🧪 Test: test_service_initialization")
    
    assert export_formatter_service is not None, "Service should be initialized"
    assert export_formatter_service.librarian is not None, "Librarian should be available"
    assert export_formatter_service.data_steward is not None, "Data Steward should be available"
    assert len(export_formatter_service.supported_formats) > 0, "Should support export formats"


@pytest.mark.asyncio
async def test_supported_formats(export_formatter_service):
    """Test that service reports supported export formats."""
    logger.info("🧪 Test: test_supported_formats")
    
    supported = export_formatter_service.supported_formats
    assert isinstance(supported, list), "Supported formats should be a list"
    assert len(supported) > 0, "Should support at least one export format"
    
    # Check for expected formats
    expected_formats = ["json", "csv", "xml", "excel", "pdf", "parquet"]
    for expected_format in expected_formats:
        assert expected_format in supported, f"Should support {expected_format} format"


@pytest.mark.asyncio
async def test_health_check(export_formatter_service):
    """Test service health check."""
    logger.info("🧪 Test: test_health_check")
    
    result = await export_formatter_service.health_check()
    
    assert result.get("status") == "healthy", f"Service should be healthy. Result: {result}"
    assert result.get("service_name") == "ExportFormatterService", "Service name should match"
    assert "supported_formats" in result, "Result should include supported_formats count"


@pytest.mark.asyncio
async def test_get_service_capabilities(export_formatter_service):
    """Test getting service capabilities."""
    logger.info("🧪 Test: test_get_service_capabilities")
    
    result = await export_formatter_service.get_service_capabilities()
    
    assert result.get("service_name") == "ExportFormatterService", "Service name should match"
    assert result.get("service_type") == "enabling_service", "Service type should match"
    assert "capabilities" in result, "Result should include capabilities"
    assert "soa_apis" in result, "Result should include SOA APIs"
    assert "supported_formats" in result, "Result should include supported formats"

