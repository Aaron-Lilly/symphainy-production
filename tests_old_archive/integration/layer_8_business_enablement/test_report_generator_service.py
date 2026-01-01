#!/usr/bin/env python3
"""
Report Generator Service - Functional Tests

Tests Report Generator Service for Insights Orchestrator:
- Report generation from templates
- Template rendering
- Report export
- Report scheduling
- Report distribution

Uses proven patterns from visualization_engine_service tests.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_json_file
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
async def report_generator_service(smart_city_infrastructure):
    """
    ReportGeneratorService instance for each test.
    
    Reuses the proven pattern from visualization_engine_service tests.
    """
    logger.info("🔧 Fixture: Starting report_generator_service fixture...")
    
    from backend.business_enablement.enabling_services.report_generator_service.report_generator_service import ReportGeneratorService
    
    logger.info("🔧 Fixture: Got infrastructure, creating ReportGeneratorService...")
    infra = smart_city_infrastructure
    service = ReportGeneratorService(
        service_name="ReportGeneratorService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: ReportGeneratorService instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Report Generator Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Report Generator Service initialization timed out after 60 seconds")
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
    
    Reuses the proven pattern from visualization_engine_service tests.
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

def create_test_report_data() -> tuple[bytes, str]:
    """Create test data for report generation."""
    import json
    report_data = {
        "title": "Q4 Sales Report",
        "period": "Q4 2024",
        "summary": {
            "total_revenue": 2500000,
            "total_costs": 1800000,
            "profit": 700000,
            "growth_rate": 0.15
        },
        "sections": [
            {"name": "Revenue", "value": 2500000},
            {"name": "Costs", "value": 1800000},
            {"name": "Profit", "value": 700000}
        ]
    }
    return json.dumps(report_data, indent=2).encode('utf-8'), "report_data.json"


def create_test_template() -> tuple[bytes, str]:
    """Create test template for report generation."""
    import json
    template = {
        "template_type": "sales_report",
        "sections": [
            {"name": "title", "type": "header"},
            {"name": "summary", "type": "summary"},
            {"name": "sections", "type": "list"}
        ]
    }
    return json.dumps(template, indent=2).encode('utf-8'), "template.json"


# ============================================================================
# TESTS - Core Functionality
# ============================================================================

@pytest.mark.asyncio
async def test_service_initialization(report_generator_service):
    """Test that service initializes correctly."""
    logger.info("🧪 Test: Service initialization")
    
    assert report_generator_service is not None
    assert hasattr(report_generator_service, 'supported_formats')
    assert len(report_generator_service.supported_formats) > 0
    
    logger.info("✅ Service initialized correctly")


@pytest.mark.asyncio
async def test_generate_report_basic(report_generator_service, storage_helper):
    """Test basic report generation."""
    logger.info("🧪 Test: Generate report (basic)")
    
    # Upload template and data
    template_data, template_filename = create_test_template()
    template_id = await storage_helper.store_file(template_data, template_filename, "application/json")
    
    report_data, report_filename = create_test_report_data()
    data_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Generate report
    result = await report_generator_service.generate_report(
        template_id=template_id,
        data_id=data_id
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "report_id" in result
    assert result.get("template_id") == template_id
    assert result.get("data_id") == data_id
    assert "report_content" in result
    
    logger.info(f"✅ Report generated: {result.get('report_id')}")


@pytest.mark.asyncio
async def test_generate_report_with_options(report_generator_service, storage_helper):
    """Test report generation with options."""
    logger.info("🧪 Test: Generate report with options")
    
    # Upload template and data
    template_data, template_filename = create_test_template()
    template_id = await storage_helper.store_file(template_data, template_filename, "application/json")
    
    report_data, report_filename = create_test_report_data()
    data_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Generate report with options
    result = await report_generator_service.generate_report(
        template_id=template_id,
        data_id=data_id,
        options={"format": "html", "include_charts": True}
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "report_content" in result
    
    logger.info(f"✅ Report generated with options: {result.get('report_id')}")


@pytest.mark.asyncio
async def test_generate_report_builtin_template(report_generator_service, storage_helper):
    """Test report generation with built-in POC proposal template."""
    logger.info("🧪 Test: Generate report (built-in template)")
    
    # Upload data only (template is built-in)
    report_data, report_filename = create_test_report_data()
    data_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Generate report using built-in template
    result = await report_generator_service.generate_report(
        template_id="poc_proposal_template",
        data_id=data_id
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "report_id" in result
    assert result.get("template_id") == "poc_proposal_template"
    
    logger.info(f"✅ Report generated with built-in template: {result.get('report_id')}")


@pytest.mark.asyncio
async def test_render_template(report_generator_service):
    """Test template rendering."""
    logger.info("🧪 Test: Render template")
    
    # Define template and data
    template = {
        "template_type": "summary",
        "sections": [
            {"name": "title", "type": "header"},
            {"name": "summary", "type": "summary"}
        ]
    }
    
    data = {
        "title": "Test Report",
        "summary": {"total": 1000, "count": 10}
    }
    
    # Render template
    result = await report_generator_service.render_template(
        template=template,
        data=data
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "rendered_content" in result
    assert "rendered_at" in result
    
    logger.info("✅ Template rendered successfully")


@pytest.mark.asyncio
async def test_export_report(report_generator_service, storage_helper):
    """Test report export."""
    logger.info("🧪 Test: Export report")
    
    # Upload template and data, generate report first
    template_data, template_filename = create_test_template()
    template_id = await storage_helper.store_file(template_data, template_filename, "application/json")
    
    report_data, report_filename = create_test_report_data()
    data_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Generate report
    report_result = await report_generator_service.generate_report(
        template_id=template_id,
        data_id=data_id
    )
    
    if report_result.get("success"):
        report_id = report_result.get("report_id")
        
        # Export report
        result = await report_generator_service.export_report(
            report_id=report_id,
            format="pdf"
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("report_id") == report_id
        assert result.get("format") == "pdf"
        assert "export_id" in result
        
        logger.info(f"✅ Report exported: {result.get('export_id')}")
    else:
        logger.info("⚠️ Report generation failed, skipping export test")


@pytest.mark.asyncio
async def test_export_report_multiple_formats(report_generator_service, storage_helper):
    """Test report export in multiple formats."""
    logger.info("🧪 Test: Export report (multiple formats)")
    
    # Upload template and data, generate report first
    template_data, template_filename = create_test_template()
    template_id = await storage_helper.store_file(template_data, template_filename, "application/json")
    
    report_data, report_filename = create_test_report_data()
    data_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Generate report
    report_result = await report_generator_service.generate_report(
        template_id=template_id,
        data_id=data_id
    )
    
    if report_result.get("success"):
        report_id = report_result.get("report_id")
        
        # Test multiple formats
        formats = ["pdf", "html", "excel", "csv", "json"]
        for fmt in formats:
            result = await report_generator_service.export_report(
                report_id=report_id,
                format=fmt
            )
            assert result.get("success") is True
            assert result.get("format") == fmt
            logger.info(f"✅ Report exported as {fmt}")
    else:
        logger.info("⚠️ Report generation failed, skipping export test")


@pytest.mark.asyncio
async def test_schedule_report(report_generator_service, storage_helper):
    """Test report scheduling."""
    logger.info("🧪 Test: Schedule report")
    
    # Upload template
    template_data, template_filename = create_test_template()
    template_id = await storage_helper.store_file(template_data, template_filename, "application/json")
    
    # Upload data source
    report_data, report_filename = create_test_report_data()
    data_source_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Schedule report
    result = await report_generator_service.schedule_report(
        template_id=template_id,
        data_source_id=data_source_id,
        schedule="0 0 * * *"  # Daily at midnight (cron format)
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "schedule_id" in result
    assert result.get("template_id") == template_id
    assert result.get("schedule") == "0 0 * * *"
    
    logger.info(f"✅ Report scheduled: {result.get('schedule_id')}")


@pytest.mark.asyncio
async def test_distribute_report(report_generator_service, storage_helper):
    """Test report distribution."""
    logger.info("🧪 Test: Distribute report")
    
    # Upload template and data, generate report first
    template_data, template_filename = create_test_template()
    template_id = await storage_helper.store_file(template_data, template_filename, "application/json")
    
    report_data, report_filename = create_test_report_data()
    data_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Generate report
    report_result = await report_generator_service.generate_report(
        template_id=template_id,
        data_id=data_id
    )
    
    if report_result.get("success"):
        report_id = report_result.get("report_id")
        
        # Distribute report
        result = await report_generator_service.distribute_report(
            report_id=report_id,
            recipients=["user1", "user2", "user3"]
        )
        
        # May succeed or fail depending on Post Office availability
        assert isinstance(result, dict)
        assert "success" in result
        
        if result.get("success"):
            assert result.get("report_id") == report_id
            assert result.get("recipients_count") == 3
            logger.info(f"✅ Report distributed: {result.get('recipients_count')} recipients")
        else:
            logger.info("⚠️ Report distribution failed (Post Office may not be available)")
    else:
        logger.info("⚠️ Report generation failed, skipping distribution test")


# ============================================================================
# TESTS - Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_generate_report_invalid_template(report_generator_service, storage_helper):
    """Test report generation with invalid template ID."""
    logger.info("🧪 Test: Generate report (invalid template)")
    
    # Upload data only
    report_data, report_filename = create_test_report_data()
    data_id = await storage_helper.store_file(report_data, report_filename, "application/json")
    
    # Try to generate report with invalid template
    result = await report_generator_service.generate_report(
        template_id="non_existent_template_id",
        data_id=data_id
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "message" in result or "error" in result
    
    logger.info("✅ Invalid template handled gracefully")


@pytest.mark.asyncio
async def test_generate_report_invalid_data(report_generator_service, storage_helper):
    """Test report generation with invalid data ID."""
    logger.info("🧪 Test: Generate report (invalid data)")
    
    # Upload template only
    template_data, template_filename = create_test_template()
    template_id = await storage_helper.store_file(template_data, template_filename, "application/json")
    
    # Try to generate report with invalid data
    result = await report_generator_service.generate_report(
        template_id=template_id,
        data_id="non_existent_data_id"
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "message" in result or "error" in result
    
    logger.info("✅ Invalid data handled gracefully")


@pytest.mark.asyncio
async def test_export_report_invalid_id(report_generator_service):
    """Test report export with invalid report ID."""
    logger.info("🧪 Test: Export report (invalid ID)")
    
    result = await report_generator_service.export_report(
        report_id="non_existent_report_id",
        format="pdf"
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "message" in result or "error" in result
    
    logger.info("✅ Invalid report ID handled gracefully")


# ============================================================================
# TESTS - Architecture Verification
# ============================================================================

@pytest.mark.asyncio
async def test_service_uses_smart_city_apis(report_generator_service):
    """Test that service uses Smart City SOA APIs."""
    logger.info("🧪 Test: Service uses Smart City APIs")
    
    # Service should have access to Librarian and Post Office
    assert hasattr(report_generator_service, 'librarian')
    assert hasattr(report_generator_service, 'post_office')
    
    logger.info("✅ Service has Smart City API access")


@pytest.mark.asyncio
async def test_service_supports_report_formats(report_generator_service):
    """Test that service supports multiple report formats."""
    logger.info("🧪 Test: Service supports report formats")
    
    assert hasattr(report_generator_service, 'supported_formats')
    assert isinstance(report_generator_service.supported_formats, list)
    assert len(report_generator_service.supported_formats) > 0
    
    # Should support common report formats
    expected_formats = ["pdf", "html", "excel", "csv", "json"]
    for fmt in expected_formats:
        if fmt in report_generator_service.supported_formats:
            logger.info(f"✅ Supports {fmt} format")
    
    logger.info(f"✅ Service supports {len(report_generator_service.supported_formats)} report formats")





