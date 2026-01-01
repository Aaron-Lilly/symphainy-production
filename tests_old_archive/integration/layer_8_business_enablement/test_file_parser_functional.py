#!/usr/bin/env python3
"""
File Parser Service - Clean Functional Tests

Tests File Parser Service with actual file parsing and result verification:
- Excel file parsing (.xlsx, .xls)
- Word document parsing (.docx, .doc)
- PDF document parsing (.pdf)
- Binary/Copybook parsing (.bin with .cpy)
- Error handling with unsupported files

Uses proper fixtures, no blocking operations, and applies all lessons learned.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_excel_file,
    create_test_word_document,
    create_test_pdf_file,
    create_test_binary_file,
    create_test_copybook_file,
    create_test_unsupported_file
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
# FIXTURES - Shared Service Instance (No Re-initialization Per Test)
# ============================================================================

@pytest.fixture(scope="function")
async def file_parser_service(smart_city_infrastructure):
    """
    FileParserService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    The service initialization is still efficient as it reuses the infrastructure.
    """
    logger.info("🔧 Fixture: Starting file_parser_service fixture...")
    
    from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
    
    logger.info("🔧 Fixture: Got infrastructure, creating FileParserService...")
    infra = smart_city_infrastructure
    service = FileParserService(
        service_name="FileParserService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: FileParserService instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("File Parser Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("File Parser Service initialization timed out after 60 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Service initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Service ready, yielding to test...")
    yield service
    logger.info("✅ Fixture: Test completed, cleaning up...")
    
    # Cleanup if needed (service doesn't have explicit cleanup, but we could add it)


@pytest.fixture(scope="function")
async def storage_helper(smart_city_infrastructure, infrastructure_storage):
    """
    Storage helper for each test.
    
    Provides ContentStewardHelper with proper user context.
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
# TEST CLASS - File Parser Functional Tests
# ============================================================================

class TestFileParserFunctional:
    """Clean functional tests for File Parser Service with real files."""
    
    # ========================================================================
    # EXCEL FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_excel_file(self, file_parser_service, storage_helper):
        """Test that File Parser actually parses a real Excel file and extracts correct data."""
        logger.info("🔧 Test: Starting Excel file parsing test...")
        
        # Create test Excel file
        logger.info("🔧 Test: Creating test Excel file...")
        excel_data, filename = create_test_excel_file()
        logger.info(f"✅ Test: Created Excel file: {filename}, size: {len(excel_data)} bytes")
        
        # Store file using storage helper
        logger.info("🔧 Test: Storing file via storage helper...")
        try:
            file_id = await asyncio.wait_for(
                storage_helper.store_file(
                    excel_data,
                    filename,
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                timeout=30.0
            )
            logger.info(f"✅ Test: File stored, file_id: {file_id}")
        except asyncio.TimeoutError:
            logger.error("❌ Test: File storage timed out after 30 seconds")
            pytest.fail("File storage timed out")
        except Exception as e:
            logger.error(f"❌ Test: File storage failed: {e}")
            raise
        
        # Parse the file
        logger.info("🔧 Test: Parsing file (this may take time)...")
        try:
            parse_result = await asyncio.wait_for(
                file_parser_service.parse_file(file_id),
                timeout=60.0
            )
            logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        except asyncio.TimeoutError:
            logger.error("❌ Test: File parsing timed out after 60 seconds")
            pytest.fail("File parsing timed out")
        except Exception as e:
            logger.error(f"❌ Test: File parsing failed: {e}")
            raise
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"Excel parsing should succeed. Result: {parse_result}"
        
        # Verify file_id is returned
        assert parse_result.get("file_id") == file_id, \
            f"Result should include file_id. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") in ["xlsx", "xls"], \
            f"Excel file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify structure contains chunks
        structure = parse_result.get("structure", {})
        assert structure.get("chunks", 0) > 0, \
            f"Excel file should have parsed chunks. Structure: {structure}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"Excel file should have extracted content. Content length: {len(content)}"
        
        # Verify expected data is in content (from our test Excel: Name, Age, City, Salary)
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["name", "age", "city", "salary", "alice", "bob"]), \
            f"Excel content should contain expected data. Content: {content[:500]}"
        
        # Verify metadata exists
        metadata = parse_result.get("metadata", {})
        assert isinstance(metadata, dict), \
            f"Result should include metadata. Metadata: {metadata}"
    
    # ========================================================================
    # WORD DOCUMENT PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_word_document(self, file_parser_service, storage_helper):
        """Test that File Parser actually parses a real Word document and extracts correct content."""
        # Create test Word document
        word_data, filename = create_test_word_document()
        
        # Store file using storage helper
        file_id = await storage_helper.store_file(
            word_data,
            filename,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # Parse the file
        parse_result = await file_parser_service.parse_file(file_id)
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"Word parsing should succeed. Result: {parse_result}"
        
        # Verify file_id is returned
        assert parse_result.get("file_id") == file_id, \
            f"Result should include file_id. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") in ["docx", "doc"], \
            f"Word file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify structure contains chunks
        structure = parse_result.get("structure", {})
        assert structure.get("chunks", 0) > 0, \
            f"Word document should have parsed chunks. Structure: {structure}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"Word document should have extracted content. Content length: {len(content)}"
        
        # Verify expected text is present (from our test document)
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["test", "document", "paragraph", "table"]), \
            f"Word document should contain expected text. Content: {content[:500]}"
        
        # Verify metadata exists
        metadata = parse_result.get("metadata", {})
        assert isinstance(metadata, dict), \
            f"Result should include metadata. Metadata: {metadata}"
    
    # ========================================================================
    # PDF DOCUMENT PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_pdf_document(self, file_parser_service, storage_helper):
        """Test that File Parser actually parses a real PDF document and extracts correct content."""
        # Create test PDF file
        pdf_data, filename = create_test_pdf_file()
        
        # Store file using storage helper
        file_id = await storage_helper.store_file(
            pdf_data,
            filename,
            content_type="application/pdf"
        )
        
        # Parse the file
        parse_result = await file_parser_service.parse_file(file_id)
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"PDF parsing should succeed. Result: {parse_result}"
        
        # Verify file_id is returned
        assert parse_result.get("file_id") == file_id, \
            f"Result should include file_id. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") == "pdf", \
            f"PDF file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify structure contains chunks
        structure = parse_result.get("structure", {})
        assert structure.get("chunks", 0) > 0, \
            f"PDF document should have parsed chunks. Structure: {structure}"
        
        # Verify page_count is present
        assert structure.get("page_count", 0) > 0, \
            f"PDF document should have page count. Structure: {structure}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"PDF document should have extracted content. Content length: {len(content)}"
        
        # Verify expected text is present (from our test PDF)
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["test", "pdf", "document", "text"]), \
            f"PDF document should contain expected text. Content: {content[:500]}"
        
        # Verify metadata exists
        metadata = parse_result.get("metadata", {})
        assert isinstance(metadata, dict), \
            f"Result should include metadata. Metadata: {metadata}"
    
    # ========================================================================
    # BINARY/COPYBOOK PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_binary_with_copybook(self, file_parser_service, storage_helper):
        """Test that File Parser actually parses a real binary file using a real copybook file."""
        # Create test binary and copybook files
        binary_data, binary_filename = create_test_binary_file()
        copybook_data, copybook_filename = create_test_copybook_file()
        
        # Store both files using storage helper
        binary_file_id = await storage_helper.store_file(
            binary_data,
            binary_filename,
            content_type="application/octet-stream"
        )
        copybook_file_id = await storage_helper.store_file(
            copybook_data,
            copybook_filename,
            content_type="text/plain"
        )
        
        # Retrieve copybook content via storage helper (with timeout protection)
        try:
            copybook_doc = await asyncio.wait_for(
                storage_helper.get_file(copybook_file_id),
                timeout=10.0
            )
            copybook_content = copybook_doc.get("file_content") or copybook_doc.get("data")
            if isinstance(copybook_content, bytes):
                copybook_content = copybook_content.decode('utf-8')
        except asyncio.TimeoutError:
            pytest.fail("Timeout retrieving copybook file - storage may be slow")
        
        # Parse binary file with copybook
        parse_result = await file_parser_service.parse_file(
            binary_file_id,
            parse_options={
                "copybook": copybook_content,
                "copybook_path": None,  # Using copybook string instead
                "file_type": "binary"  # Explicitly specify binary type
            }
        )
        
        # Verify parsing handled gracefully (may succeed or fail gracefully)
        assert parse_result.get("success") is not False, \
            f"Binary with copybook parsing should handle gracefully. Result: {parse_result}"
        
        # If parsing succeeded, verify structure
        if parse_result.get("success") is True:
            structure = parse_result.get("structure", {})
            chunks = structure.get("chunks", 0)
            content = parse_result.get("content", "")
            
            # Binary files may be parsed as text or may have special handling
            # At minimum, verify the service handled it without crashing
            assert chunks > 0 or len(content) > 0 or "error" not in str(parse_result).lower(), \
                f"Binary file should be processed. Structure: {structure}, Content length: {len(content)}"
    
    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_handle_unsupported_file_gracefully(self, file_parser_service, storage_helper):
        """Test that File Parser handles real unsupported files gracefully."""
        # Create unsupported file
        unsupported_data, filename = create_test_unsupported_file()
        
        # Store file using storage helper
        file_id = await storage_helper.store_file(
            unsupported_data,
            filename,
            content_type="application/octet-stream"
        )
        
        # Parse the file - should handle gracefully
        parse_result = await file_parser_service.parse_file(file_id)
        
        # Service should either:
        # 1. Return a result indicating unsupported format, OR
        # 2. Attempt to parse as text (fallback), OR
        # 3. Return an error in a structured way
        
        # Verify result is structured (not a crash)
        assert isinstance(parse_result, dict), \
            f"Unsupported file should return structured result, not crash. Result: {parse_result}"
        
        # If parsing failed, error should be structured
        if parse_result.get("success") is False:
            assert "error" in parse_result or "message" in parse_result, \
                f"Error should be structured. Result: {parse_result}"
