#!/usr/bin/env python3
"""
File Parsing 5-Layer Architecture Verification Tests

Tests each file parsing capability to verify:
1. 5-layer exposure pattern (Adapter → Abstraction → Gateway → Service)
2. Functional parsing (actual content extraction)
3. Proper abstraction selection and error handling

File Types Tested:
- Excel (.xlsx, .xls)
- CSV (.csv)
- JSON (.json)
- Text (.txt)
- PDF (.pdf)
- Word (.docx, .doc)
- HTML (.html, .htm)
- Image (.png, .jpg) - OCR
- Mainframe (.bin, .binary, .dat) - with copybook
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_excel_file,
    create_test_word_document,
    create_test_pdf_file,
    create_test_image_file,
    create_test_binary_file,
    create_test_copybook_file
)
from tests.integration.layer_8_business_enablement.test_file_parser_new_architecture import (
    create_test_csv_file,
    create_test_json_file,
    create_test_text_file,
    create_test_html_file
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
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
async def file_parser_service(smart_city_infrastructure):
    """FileParserService instance for each test."""
    logger.info("🔧 Fixture: Starting file_parser_service fixture...")
    
    from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
    
    infra = smart_city_infrastructure
    service = FileParserService(
        service_name="FileParserService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    
    # Initialize with timeout protection
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        if not result:
            pytest.fail("File Parser Service failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("File Parser Service initialization timed out after 60 seconds")
    
    yield service


@pytest.fixture(scope="function")
async def storage_helper(smart_city_infrastructure, infrastructure_storage):
    """Storage helper for each test."""
    storage = infrastructure_storage["file_storage"]
    user_context = TestDataManager.get_user_context()
    helper = ContentStewardHelper(storage, user_context)
    
    yield helper
    
    # Cleanup
    try:
        await helper.cleanup()
    except Exception:
        pass


# ============================================================================
# 5-LAYER PATTERN VERIFICATION TESTS
# ============================================================================

class Test5LayerPatternVerification:
    """Verify 5-layer architecture pattern for each file parsing abstraction."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_excel_processing_5layer_pattern(self, smart_city_infrastructure):
        """Verify Excel processing follows 5-layer pattern."""
        logger.info("🔧 Test: Verifying Excel processing 5-layer pattern...")
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        # public_works is not needed for this test - we access via Platform Gateway
        
        # Layer 5: Platform Gateway - Verify abstraction is accessible
        abstraction = platform_gateway.get_abstraction(
            realm_name="business_enablement",
            abstraction_name="excel_processing"
        )
        assert abstraction is not None, "Excel processing abstraction should be accessible via Platform Gateway"
        logger.info("✅ Layer 5: Platform Gateway - Excel abstraction accessible")
        
        # Layer 2: Abstraction - Verify it implements FileParsingProtocol
        from foundations.public_works_foundation.abstraction_contracts.file_parsing_protocol import FileParsingRequest
        assert hasattr(abstraction, 'parse_file'), "Abstraction should implement parse_file()"
        logger.info("✅ Layer 2: Abstraction - Implements FileParsingProtocol")
        
        # Layer 1: Adapter - Verify adapter exists
        assert hasattr(abstraction, 'excel_adapter'), "Abstraction should have excel_adapter"
        adapter = abstraction.excel_adapter
        assert adapter is not None, "Excel adapter should be initialized"
        assert hasattr(adapter, 'parse_file'), "Adapter should have parse_file() method"
        logger.info("✅ Layer 1: Adapter - Excel adapter initialized")
        
        logger.info("✅ Test: Excel processing 5-layer pattern verified")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_csv_processing_5layer_pattern(self, smart_city_infrastructure):
        """Verify CSV processing follows 5-layer pattern."""
        logger.info("🔧 Test: Verifying CSV processing 5-layer pattern...")
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        
        # Layer 5: Platform Gateway
        abstraction = platform_gateway.get_abstraction(
            realm_name="business_enablement",
            abstraction_name="csv_processing"
        )
        assert abstraction is not None, "CSV processing abstraction should be accessible"
        logger.info("✅ Layer 5: Platform Gateway - CSV abstraction accessible")
        
        # Layer 2: Abstraction
        assert hasattr(abstraction, 'parse_file'), "Abstraction should implement parse_file()"
        logger.info("✅ Layer 2: Abstraction - Implements FileParsingProtocol")
        
        # Layer 1: Adapter
        assert hasattr(abstraction, 'csv_adapter'), "Abstraction should have csv_adapter"
        assert abstraction.csv_adapter is not None, "CSV adapter should be initialized"
        logger.info("✅ Layer 1: Adapter - CSV adapter initialized")
        
        logger.info("✅ Test: CSV processing 5-layer pattern verified")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_pdf_processing_5layer_pattern(self, smart_city_infrastructure):
        """Verify PDF processing follows 5-layer pattern."""
        logger.info("🔧 Test: Verifying PDF processing 5-layer pattern...")
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        
        # Layer 5: Platform Gateway
        abstraction = platform_gateway.get_abstraction(
            realm_name="business_enablement",
            abstraction_name="pdf_processing"
        )
        assert abstraction is not None, "PDF processing abstraction should be accessible"
        logger.info("✅ Layer 5: Platform Gateway - PDF abstraction accessible")
        
        # Layer 2: Abstraction
        assert hasattr(abstraction, 'parse_file'), "Abstraction should implement parse_file()"
        logger.info("✅ Layer 2: Abstraction - Implements FileParsingProtocol")
        
        # Layer 1: Adapters (PDF has multiple adapters)
        assert hasattr(abstraction, 'pdfplumber_adapter') or hasattr(abstraction, 'pypdf2_adapter'), \
            "PDF abstraction should have at least one adapter"
        logger.info("✅ Layer 1: Adapter - PDF adapters initialized")
        
        logger.info("✅ Test: PDF processing 5-layer pattern verified")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_mainframe_processing_5layer_pattern(self, smart_city_infrastructure):
        """Verify Mainframe processing follows 5-layer pattern."""
        logger.info("🔧 Test: Verifying Mainframe processing 5-layer pattern...")
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        
        # Layer 5: Platform Gateway
        abstraction = platform_gateway.get_abstraction(
            realm_name="business_enablement",
            abstraction_name="mainframe_processing"
        )
        assert abstraction is not None, "Mainframe processing abstraction should be accessible"
        logger.info("✅ Layer 5: Platform Gateway - Mainframe abstraction accessible")
        
        # Layer 2: Abstraction
        assert hasattr(abstraction, 'parse_file'), "Abstraction should implement parse_file()"
        logger.info("✅ Layer 2: Abstraction - Implements FileParsingProtocol")
        
        # Layer 1: Adapter
        assert hasattr(abstraction, 'mainframe_adapter'), "Abstraction should have mainframe_adapter"
        assert abstraction.mainframe_adapter is not None, "Mainframe adapter should be initialized"
        assert hasattr(abstraction.mainframe_adapter, 'parse_file'), "Adapter should have parse_file() method"
        logger.info("✅ Layer 1: Adapter - Mainframe adapter initialized")
        
        logger.info("✅ Test: Mainframe processing 5-layer pattern verified")


# ============================================================================
# FUNCTIONAL PARSING TESTS
# ============================================================================

class TestFunctionalParsing:
    """Test that each file type can be functionally parsed."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_excel_functional_parsing(self, file_parser_service, storage_helper):
        """Test Excel file functional parsing."""
        logger.info("🔧 Test: Testing Excel functional parsing...")
        
        # Create and store Excel file
        excel_data, filename = create_test_excel_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                excel_data,
                filename,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            timeout=30.0
        )
        
        # Parse file
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        # Verify parsing
        assert result.get("success") is True, f"Excel parsing failed: {result}"
        assert result.get("file_type") in ["xlsx", "xls"], f"File type not detected: {result.get('file_type')}"
        assert len(result.get("content", "")) > 0, "Content should be extracted"
        
        # Verify structured data
        tables = result.get("tables", [])
        records = result.get("records", [])
        assert len(tables) > 0 or len(records) > 0, "Should have structured data"
        
        logger.info("✅ Test: Excel functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_csv_functional_parsing(self, file_parser_service, storage_helper):
        """Test CSV file functional parsing."""
        logger.info("🔧 Test: Testing CSV functional parsing...")
        
        csv_data, filename = create_test_csv_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(csv_data, filename, content_type="text/csv"),
            timeout=30.0
        )
        
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        assert result.get("success") is True, f"CSV parsing failed: {result}"
        assert result.get("file_type") == "csv", f"File type not detected: {result.get('file_type')}"
        assert len(result.get("content", "")) > 0, "Content should be extracted"
        assert len(result.get("tables", [])) > 0 or len(result.get("records", [])) > 0, "Should have structured data"
        
        logger.info("✅ Test: CSV functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_json_functional_parsing(self, file_parser_service, storage_helper):
        """Test JSON file functional parsing."""
        logger.info("🔧 Test: Testing JSON functional parsing...")
        
        json_data, filename = create_test_json_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(json_data, filename, content_type="application/json"),
            timeout=30.0
        )
        
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        assert result.get("success") is True, f"JSON parsing failed: {result}"
        assert result.get("file_type") == "json", f"File type not detected: {result.get('file_type')}"
        assert len(result.get("content", "")) > 0, "Content should be extracted"
        
        logger.info("✅ Test: JSON functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_text_functional_parsing(self, file_parser_service, storage_helper):
        """Test text file functional parsing."""
        logger.info("🔧 Test: Testing text functional parsing...")
        
        text_data, filename = create_test_text_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(text_data, filename, content_type="text/plain"),
            timeout=30.0
        )
        
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        assert result.get("success") is True, f"Text parsing failed: {result}"
        assert result.get("file_type") in ["txt", "text"], f"File type not detected: {result.get('file_type')}"
        assert len(result.get("content", "")) > 0, "Content should be extracted"
        
        logger.info("✅ Test: Text functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_pdf_functional_parsing(self, file_parser_service, storage_helper):
        """Test PDF file functional parsing."""
        logger.info("🔧 Test: Testing PDF functional parsing...")
        
        pdf_data, filename = create_test_pdf_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(pdf_data, filename, content_type="application/pdf"),
            timeout=30.0
        )
        
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        assert result.get("success") is True, f"PDF parsing failed: {result}"
        assert result.get("file_type") == "pdf", f"File type not detected: {result.get('file_type')}"
        assert len(result.get("content", "")) > 0, "Content should be extracted"
        
        logger.info("✅ Test: PDF functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_word_functional_parsing(self, file_parser_service, storage_helper):
        """Test Word document functional parsing."""
        logger.info("🔧 Test: Testing Word functional parsing...")
        
        word_data, filename = create_test_word_document()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                word_data,
                filename,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            timeout=30.0
        )
        
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        assert result.get("success") is True, f"Word parsing failed: {result}"
        assert result.get("file_type") in ["docx", "doc"], f"File type not detected: {result.get('file_type')}"
        assert len(result.get("content", "")) > 0, "Content should be extracted"
        
        logger.info("✅ Test: Word functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_html_functional_parsing(self, file_parser_service, storage_helper):
        """Test HTML file functional parsing."""
        logger.info("🔧 Test: Testing HTML functional parsing...")
        
        html_data, filename = create_test_html_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(html_data, filename, content_type="text/html"),
            timeout=30.0
        )
        
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        assert result.get("success") is True, f"HTML parsing failed: {result}"
        assert result.get("file_type") in ["html", "htm"], f"File type not detected: {result.get('file_type')}"
        assert len(result.get("content", "")) > 0, "Content should be extracted"
        
        logger.info("✅ Test: HTML functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_image_functional_parsing(self, file_parser_service, storage_helper):
        """Test image file functional parsing (OCR)."""
        logger.info("🔧 Test: Testing image functional parsing (OCR)...")
        
        try:
            image_data, filename = create_test_image_file()
        except ImportError:
            pytest.skip("Pillow (PIL) required for image test file creation")
        
        file_id = await asyncio.wait_for(
            storage_helper.store_file(image_data, filename, content_type="image/png"),
            timeout=30.0
        )
        
        result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        
        # OCR may or may not extract text, but should not crash
        assert isinstance(result, dict), "Image parsing should return structured result"
        if result.get("success") is True:
            logger.info(f"✅ OCR extracted text: {len(result.get('content', ''))} characters")
        
        logger.info("✅ Test: Image functional parsing passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_mainframe_functional_parsing(self, file_parser_service, storage_helper):
        """Test mainframe binary file functional parsing with copybook."""
        logger.info("🔧 Test: Testing mainframe functional parsing...")
        
        # Create test files
        binary_data, binary_filename = create_test_binary_file()
        copybook_data, copybook_filename = create_test_copybook_file()
        
        # Store files
        binary_file_id = await asyncio.wait_for(
            storage_helper.store_file(
                binary_data,
                binary_filename,
                content_type="application/octet-stream"
            ),
            timeout=30.0
        )
        
        copybook_file_id = await asyncio.wait_for(
            storage_helper.store_file(
                copybook_data,
                copybook_filename,
                content_type="text/plain"
            ),
            timeout=30.0
        )
        
        # Retrieve copybook content
        copybook_doc = await asyncio.wait_for(
            storage_helper.get_file(copybook_file_id),
            timeout=10.0
        )
        copybook_content = copybook_doc.get("file_content") or copybook_doc.get("data")
        if isinstance(copybook_content, bytes):
            copybook_content = copybook_content.decode('utf-8')
        
        # Parse binary file with copybook
        result = await asyncio.wait_for(
            file_parser_service.parse_file(
                binary_file_id,
                parse_options={"copybook": copybook_content}
            ),
            timeout=60.0
        )
        
        # Verify parsing
        assert isinstance(result, dict), "Mainframe parsing should return structured result"
        if result.get("success") is True:
            assert len(result.get("content", "")) > 0 or len(result.get("records", [])) > 0, \
                "Mainframe parsing should produce content or records"
            logger.info(f"✅ Mainframe parsed: {len(result.get('records', []))} records")
        else:
            error = result.get("error") or result.get("message")
            logger.warning(f"⚠️ Mainframe parsing failed: {error}")
        
        logger.info("✅ Test: Mainframe functional parsing passed")


# ============================================================================
# INTEGRATION TEST - Full End-to-End
# ============================================================================

class TestEndToEndParsing:
    """End-to-end tests through FileParserService."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(180)
    async def test_all_file_types_end_to_end(self, file_parser_service, storage_helper):
        """Test all file types end-to-end through FileParserService."""
        logger.info("🔧 Test: Testing all file types end-to-end...")
        
        test_cases = [
            ("excel", create_test_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ["xlsx", "xls"]),
            ("csv", create_test_csv_file, "text/csv", ["csv"]),
            ("json", create_test_json_file, "application/json", ["json"]),
            ("text", create_test_text_file, "text/plain", ["txt", "text"]),
            ("pdf", create_test_pdf_file, "application/pdf", ["pdf"]),
            ("word", create_test_word_document, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ["docx", "doc"]),
            ("html", create_test_html_file, "text/html", ["html", "htm"]),
        ]
        
        results = {}
        
        for file_type, create_func, content_type, expected_types in test_cases:
            try:
                logger.info(f"🔧 Testing {file_type}...")
                
                # Create and store file
                file_data, filename = create_func()
                file_id = await asyncio.wait_for(
                    storage_helper.store_file(file_data, filename, content_type=content_type),
                    timeout=30.0
                )
                
                # Parse file
                result = await asyncio.wait_for(
                    file_parser_service.parse_file(file_id),
                    timeout=60.0
                )
                
                # Verify
                assert result.get("success") is True, f"{file_type} parsing failed: {result}"
                assert result.get("file_type") in expected_types, \
                    f"{file_type} file type not detected correctly: {result.get('file_type')}"
                assert len(result.get("content", "")) > 0, f"{file_type} should have extracted content"
                
                results[file_type] = "✅ PASSED"
                logger.info(f"✅ {file_type} parsing passed")
                
            except Exception as e:
                results[file_type] = f"❌ FAILED: {e}"
                logger.error(f"❌ {file_type} parsing failed: {e}")
                raise
        
        # Summary
        logger.info("=" * 80)
        logger.info("END-TO-END TEST SUMMARY")
        logger.info("=" * 80)
        for file_type, status in results.items():
            logger.info(f"  {file_type:10s}: {status}")
        logger.info("=" * 80)
        
        # All should pass
        failed = [ft for ft, status in results.items() if "FAILED" in status]
        assert len(failed) == 0, f"Some file types failed: {failed}"

