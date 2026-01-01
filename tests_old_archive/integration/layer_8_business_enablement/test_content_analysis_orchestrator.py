#!/usr/bin/env python3
"""
Content Analysis Orchestrator - Functional Tests

Tests ContentAnalysisOrchestrator to verify it fully enables the Content Pillar:
- File upload (including mainframe binary + copybook support)
- File parsing to AI-friendly formats (parquet, JSON Structured, JSON Chunks)
- Metadata extraction
- Dashboard/file listing
- File details/preview
- Entity extraction for ContentLiaisonAgent

Uses proven patterns from enabling service tests.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_excel_file,
    create_test_json_file,
    create_test_binary_file,
    create_test_copybook_file,
    create_test_pdf_file
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
async def delivery_manager(smart_city_infrastructure):
    """
    DeliveryManagerService instance for each test.
    
    The orchestrator requires a delivery_manager, so we create one using
    the infrastructure fixtures.
    """
    logger.info("🔧 Fixture: Starting delivery_manager fixture...")
    
    from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    logger.info("🔧 Fixture: Got infrastructure, creating DeliveryManagerService...")
    infra = smart_city_infrastructure
    manager = DeliveryManagerService(
        di_container=infra["di_container"],
        platform_gateway=infra["platform_gateway"]
    )
    logger.info("✅ Fixture: DeliveryManagerService instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing delivery manager (this may take time)...")
    try:
        result = await asyncio.wait_for(manager.initialize(), timeout=90.0)
        logger.info(f"✅ Fixture: Delivery manager initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Delivery manager initialization returned False")
            pytest.fail("Delivery Manager Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Delivery manager initialization timed out after 90 seconds")
        pytest.fail("Delivery Manager Service initialization timed out after 90 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Delivery manager initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Delivery manager ready, yielding to test...")
    yield manager
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
async def content_orchestrator(delivery_manager):
    """
    ContentAnalysisOrchestrator instance for each test.
    
    Creates the orchestrator using the delivery_manager fixture.
    """
    logger.info("🔧 Fixture: Starting content_orchestrator fixture...")
    
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
    
    logger.info("🔧 Fixture: Creating ContentAnalysisOrchestrator...")
    orchestrator = ContentAnalysisOrchestrator(delivery_manager)
    logger.info("✅ Fixture: ContentAnalysisOrchestrator instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing orchestrator (this may take time)...")
    try:
        result = await asyncio.wait_for(orchestrator.initialize(), timeout=90.0)
        logger.info(f"✅ Fixture: Orchestrator initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Orchestrator initialization returned False")
            pytest.fail("Content Analysis Orchestrator failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Orchestrator initialization timed out after 90 seconds")
        pytest.fail("Content Analysis Orchestrator initialization timed out after 90 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Orchestrator initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Orchestrator ready, yielding to test...")
    yield orchestrator
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
# FUNCTIONAL TESTS - Content Pillar Requirements
# ============================================================================

@pytest.mark.asyncio
async def test_upload_file_basic(content_orchestrator):
    """Test basic file upload (Content Pillar requirement)."""
    logger.info("🧪 Test: test_upload_file_basic")
    
    # 1. Create test file
    excel_bytes, filename = create_test_excel_file()
    
    # 2. Upload file
    user_id = "test_user"
    result = await content_orchestrator.upload_file(
        file_data=excel_bytes,
        filename=filename,
        file_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        user_id=user_id
    )
    
    # 3. Assertions
    logger.info(f"✅ Upload result: {result}")
    assert result.get("success") is True, f"File upload should succeed. Result: {result}"
    assert "file_id" in result, "Result should include file_id"
    assert "uuid" in result, "Result should include uuid"
    assert result.get("ui_name") is not None, "Result should include ui_name"
    assert result.get("original_filename") == filename, "Result should include original_filename"


@pytest.mark.asyncio
async def test_upload_mainframe_binary_with_copybook(content_orchestrator):
    """Test mainframe binary file upload with copybook (Content Pillar requirement)."""
    logger.info("🧪 Test: test_upload_mainframe_binary_with_copybook")
    
    # 1. Create mainframe binary file and copybook
    binary_bytes, binary_filename = create_test_binary_file()
    copybook_bytes, copybook_filename = create_test_copybook_file()
    
    # 2. Upload binary file
    user_id = "test_user"
    binary_result = await content_orchestrator.upload_file(
        file_data=binary_bytes,
        filename=binary_filename,
        file_type="application/octet-stream",
        user_id=user_id
    )
    
    assert binary_result.get("success") is True, f"Binary file upload should succeed. Result: {binary_result}"
    binary_file_id = binary_result.get("file_id")
    logger.info(f"✅ Binary file uploaded with ID: {binary_file_id}")
    
    # 3. Upload copybook file
    copybook_result = await content_orchestrator.upload_file(
        file_data=copybook_bytes,
        filename=copybook_filename,
        file_type="text/plain",
        user_id=user_id
    )
    
    assert copybook_result.get("success") is True, f"Copybook upload should succeed. Result: {copybook_result}"
    copybook_file_id = copybook_result.get("file_id")
    logger.info(f"✅ Copybook uploaded with ID: {copybook_file_id}")
    
    # 4. Verify both files are uploaded
    assert binary_file_id is not None, "Binary file should have a file_id"
    assert copybook_file_id is not None, "Copybook should have a file_id"
    assert binary_file_id != copybook_file_id, "Binary and copybook should have different file_ids"


@pytest.mark.asyncio
async def test_parse_file_excel(content_orchestrator, storage_helper):
    """Test file parsing for Excel file (Content Pillar requirement)."""
    logger.info("🧪 Test: test_parse_file_excel")
    
    # 1. Upload file first
    excel_bytes, filename = create_test_excel_file()
    file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    logger.info(f"✅ Stored test file with ID: {file_id}")
    
    # 2. Parse file
    result = await content_orchestrator.parse_file(
        file_id=file_id,
        parse_options=None
    )
    
    # 3. Assertions
    logger.info(f"✅ Parse result: {result}")
    assert result.get("status") == "success" or result.get("success") is True, f"File parsing should succeed. Result: {result}"
    assert "data" in result or "parse_result" in result, "Result should include parsed data"
    assert result.get("resource_id") == file_id or result.get("file_id") == file_id, "Result should include file_id"


@pytest.mark.asyncio
async def test_parse_file_mainframe_with_copybook(content_orchestrator, storage_helper):
    """Test mainframe binary parsing with copybook (Content Pillar requirement)."""
    logger.info("🧪 Test: test_parse_file_mainframe_with_copybook")
    
    # 1. Upload binary and copybook files
    binary_bytes, binary_filename = create_test_binary_file()
    copybook_bytes, copybook_filename = create_test_copybook_file()
    
    binary_file_id = await storage_helper.store_file(
        file_data=binary_bytes,
        filename=binary_filename,
        content_type="application/octet-stream"
    )
    copybook_file_id = await storage_helper.store_file(
        file_data=copybook_bytes,
        filename=copybook_filename,
        content_type="text/plain"
    )
    logger.info(f"✅ Stored binary file with ID: {binary_file_id}")
    logger.info(f"✅ Stored copybook with ID: {copybook_file_id}")
    
    # 2. Parse binary file with copybook reference
    # Note: The orchestrator's parse_file may need copybook_file_id in parse_options
    parse_options = {
        "copybook_file_id": copybook_file_id
    }
    
    result = await content_orchestrator.parse_file(
        file_id=binary_file_id,
        parse_options=parse_options
    )
    
    # 3. Assertions
    logger.info(f"✅ Parse result: {result}")
    assert result.get("status") == "success" or result.get("success") is True, f"Mainframe parsing should succeed. Result: {result}"
    assert "data" in result or "parse_result" in result, "Result should include parsed data"


@pytest.mark.asyncio
async def test_process_file_complete_workflow(content_orchestrator, storage_helper):
    """Test complete file processing (parsing + metadata extraction) - Content Pillar requirement."""
    logger.info("🧪 Test: test_process_file_complete_workflow")
    
    # 1. Upload file
    excel_bytes, filename = create_test_excel_file()
    file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    logger.info(f"✅ Stored test file with ID: {file_id}")
    
    # 2. Process file (combines parsing + metadata extraction)
    user_id = "test_user"
    result = await content_orchestrator.process_file(
        file_id=file_id,
        user_id=user_id
    )
    
    # 3. Assertions
    logger.info(f"✅ Process result: {result}")
    assert result.get("success") is True, f"File processing should succeed. Result: {result}"
    assert result.get("file_id") == file_id, "Result should include file_id"
    assert "parse_result" in result, "Result should include parse_result"
    assert "file_details" in result, "Result should include file_details (metadata)"


@pytest.mark.asyncio
async def test_process_file_mainframe_with_copybook(content_orchestrator, storage_helper):
    """Test mainframe file processing with copybook (Content Pillar requirement)."""
    logger.info("🧪 Test: test_process_file_mainframe_with_copybook")
    
    # 1. Upload binary and copybook files
    binary_bytes, binary_filename = create_test_binary_file()
    copybook_bytes, copybook_filename = create_test_copybook_file()
    
    binary_file_id = await storage_helper.store_file(
        file_data=binary_bytes,
        filename=binary_filename,
        content_type="application/octet-stream"
    )
    copybook_file_id = await storage_helper.store_file(
        file_data=copybook_bytes,
        filename=copybook_filename,
        content_type="text/plain"
    )
    logger.info(f"✅ Stored binary file with ID: {binary_file_id}")
    logger.info(f"✅ Stored copybook with ID: {copybook_file_id}")
    
    # 2. Process binary file with copybook reference
    user_id = "test_user"
    result = await content_orchestrator.process_file(
        file_id=binary_file_id,
        user_id=user_id,
        copybook_file_id=copybook_file_id
    )
    
    # 3. Assertions
    logger.info(f"✅ Process result: {result}")
    assert result.get("success") is True, f"Mainframe processing should succeed. Result: {result}"
    assert result.get("file_id") == binary_file_id, "Result should include binary file_id"
    assert result.get("copybook_file_id") == copybook_file_id, "Result should include copybook_file_id"
    assert "parse_result" in result, "Result should include parse_result"
    assert "file_details" in result, "Result should include file_details"


@pytest.mark.asyncio
async def test_list_uploaded_files_dashboard(content_orchestrator, storage_helper):
    """Test file listing for dashboard view (Content Pillar requirement)."""
    logger.info("🧪 Test: test_list_uploaded_files_dashboard")
    
    # 1. Upload multiple files
    user_id = "test_user"
    file_ids = []
    
    # Upload Excel file
    excel_bytes, excel_filename = create_test_excel_file()
    excel_file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=excel_filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    file_ids.append(excel_file_id)
    
    # Upload JSON file
    json_bytes = create_test_json_file({"test": "data"})
    json_file_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="test_data.json",
        content_type="application/json"
    )
    file_ids.append(json_file_id)
    
    logger.info(f"✅ Uploaded {len(file_ids)} files")
    
    # 2. List uploaded files
    result = await content_orchestrator.list_uploaded_files(user_id=user_id)
    
    # 3. Assertions
    logger.info(f"✅ List result: {result}")
    assert result.get("success") is True, f"File listing should succeed. Result: {result}"
    assert "files" in result, "Result should include files list"
    assert isinstance(result.get("files"), list), "Files should be a list"
    assert "count" in result, "Result should include count"
    assert result.get("count") >= len(file_ids), f"Should list at least {len(file_ids)} files"


@pytest.mark.asyncio
async def test_get_file_details_preview(content_orchestrator, storage_helper):
    """Test file details/preview (Content Pillar requirement)."""
    logger.info("🧪 Test: test_get_file_details_preview")
    
    # 1. Upload file
    excel_bytes, filename = create_test_excel_file()
    file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    logger.info(f"✅ Stored test file with ID: {file_id}")
    
    # 2. Get file details
    user_id = "test_user"
    result = await content_orchestrator.get_file_details(
        file_id=file_id,
        user_id=user_id
    )
    
    # 3. Assertions
    logger.info(f"✅ File details result: {result}")
    assert result.get("success") is True, f"Get file details should succeed. Result: {result}"
    assert "file" in result, "Result should include file details"
    file_details = result.get("file", {})
    assert file_details.get("file_id") == file_id or file_details.get("uuid") == file_id, "File details should include file_id"


@pytest.mark.asyncio
async def test_extract_entities_for_liaison_agent(content_orchestrator, storage_helper):
    """Test entity extraction for ContentLiaisonAgent interaction (Content Pillar requirement)."""
    logger.info("🧪 Test: test_extract_entities_for_liaison_agent")
    
    # 1. Upload and parse a file first
    excel_bytes, filename = create_test_excel_file()
    file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    logger.info(f"✅ Stored test file with ID: {file_id}")
    
    # 2. Extract entities
    result = await content_orchestrator.extract_entities(document_id=file_id)
    
    # 3. Assertions
    logger.info(f"✅ Entity extraction result: {result}")
    assert result.get("status") == "success" or result.get("success") is True, f"Entity extraction should succeed. Result: {result}"
    assert "data" in result or "entities" in result, "Result should include entities"


@pytest.mark.asyncio
async def test_analyze_document_complete_analysis(content_orchestrator, storage_helper):
    """Test complete document analysis (Content Pillar requirement)."""
    logger.info("🧪 Test: test_analyze_document_complete_analysis")
    
    # 1. Upload file
    excel_bytes, filename = create_test_excel_file()
    file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    logger.info(f"✅ Stored test file with ID: {file_id}")
    
    # 2. Analyze document (structure + metadata + entities)
    analysis_types = ["structure", "metadata", "entities"]
    result = await content_orchestrator.analyze_document(
        document_id=file_id,
        analysis_types=analysis_types
    )
    
    # 3. Assertions
    logger.info(f"✅ Analysis result: {result}")
    assert result.get("status") == "success" or result.get("success") is True, f"Document analysis should succeed. Result: {result}"
    assert "data" in result, "Result should include analysis data"
    data = result.get("data", {})
    # Check for analysis results (structure, metadata, entities)
    assert "structure" in data or "metadata" in data or "entities" in data, "Result should include at least one analysis type"


@pytest.mark.asyncio
async def test_mvp_ui_format_compatibility(content_orchestrator, storage_helper):
    """Test that orchestrator formats results correctly for MVP UI (Content Pillar requirement)."""
    logger.info("🧪 Test: test_mvp_ui_format_compatibility")
    
    # 1. Upload file
    excel_bytes, filename = create_test_excel_file()
    file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    logger.info(f"✅ Stored test file with ID: {file_id}")
    
    # 2. Parse file (should return MVP UI format)
    result = await content_orchestrator.parse_file(
        file_id=file_id,
        parse_options=None
    )
    
    # 3. Verify MVP UI format
    logger.info(f"✅ Parse result: {result}")
    assert result.get("status") == "success", "Result should have status='success'"
    assert result.get("resource_id") == file_id or result.get("file_id") == file_id, "Result should include resource_id"
    assert "data" in result, "Result should include data"
    assert "timestamp" in result, "Result should include timestamp"
    assert result.get("orchestrator") == "ContentAnalysisOrchestrator", "Result should include orchestrator name"


# ============================================================================
# ARCHITECTURAL TESTS - Verify Orchestrator Structure
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_initialization(content_orchestrator):
    """Test that orchestrator initializes correctly."""
    logger.info("🧪 Test: test_orchestrator_initialization")
    
    assert content_orchestrator is not None, "Orchestrator should be initialized"
    assert content_orchestrator.delivery_manager is not None, "Delivery manager should be available"
    assert hasattr(content_orchestrator, 'mcp_server'), "Orchestrator should have MCP server"
    assert hasattr(content_orchestrator, 'liaison_agent') or hasattr(content_orchestrator, 'processing_agent'), "Orchestrator should have agents"


@pytest.mark.asyncio
async def test_orchestrator_delegates_to_enabling_services(content_orchestrator, storage_helper):
    """Test that orchestrator properly delegates to enabling services."""
    logger.info("🧪 Test: test_orchestrator_delegates_to_enabling_services")
    
    # 1. Upload file
    excel_bytes, filename = create_test_excel_file()
    file_id = await storage_helper.store_file(
        file_data=excel_bytes,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    logger.info(f"✅ Stored test file with ID: {file_id}")
    
    # 2. Parse file (should delegate to FileParserService)
    result = await content_orchestrator.parse_file(
        file_id=file_id,
        parse_options=None
    )
    
    # 3. Verify delegation worked
    assert result.get("status") == "success" or result.get("success") is True, f"Parsing should succeed via delegation. Result: {result}"
    
    # 4. Extract entities (should delegate to DataAnalyzerService)
    entities_result = await content_orchestrator.extract_entities(document_id=file_id)
    assert entities_result.get("status") == "success" or entities_result.get("success") is True, f"Entity extraction should succeed via delegation. Result: {entities_result}"

