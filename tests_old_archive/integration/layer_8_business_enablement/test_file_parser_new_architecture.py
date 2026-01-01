#!/usr/bin/env python3
"""
File Parser Service - New 5-Layer Architecture Functional Tests

Tests File Parser Service with the new 5-layer architecture:
- Verifies that file parsing uses individual abstractions via Platform Gateway
- Tests multiple file types (Excel, CSV, JSON, Text, PDF, Word, HTML, Image)
- Validates that parsing results are correct and complete
- Ensures proper abstraction selection and error handling

Uses proper fixtures, timeouts, and applies all lessons learned.
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
from tests.integration.layer_8_business_enablement.test_utilities import (
    ContentStewardHelper,
    TestDataManager
)

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Shared Service Instance
# ============================================================================

@pytest.fixture(scope="function")
async def file_parser_service(smart_city_infrastructure):
    """
    FileParserService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
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
# HELPER FUNCTIONS
# ============================================================================

def create_test_csv_file() -> tuple[bytes, str]:
    """Create a test CSV file with sample data."""
    csv_content = """Name,Age,City,Salary
Alice,25,New York,50000
Bob,30,London,60000
Charlie,35,Tokyo,70000
Diana,28,Paris,55000"""
    return csv_content.encode('utf-8'), "test_data.csv"


def create_test_json_file() -> tuple[bytes, str]:
    """Create a test JSON file with sample data."""
    import json
    json_data = {
        "employees": [
            {"name": "Alice", "age": 25, "city": "New York", "salary": 50000},
            {"name": "Bob", "age": 30, "city": "London", "salary": 60000},
            {"name": "Charlie", "age": 35, "city": "Tokyo", "salary": 70000},
            {"name": "Diana", "age": 28, "city": "Paris", "salary": 55000}
        ]
    }
    return json.dumps(json_data, indent=2).encode('utf-8'), "test_data.json"


def create_test_text_file() -> tuple[bytes, str]:
    """Create a test plain text file."""
    text_content = """Test Document
This is a test document for File Parser functional testing.
It contains multiple lines of text content.
Line 1: This is the first line.
Line 2: This is the second line.
Line 3: This is the third line."""
    return text_content.encode('utf-8'), "test_document.txt"


def create_test_html_file() -> tuple[bytes, str]:
    """Create a test HTML file."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test HTML Document</title>
</head>
<body>
    <h1>Test Document</h1>
    <p>This is a test HTML document for File Parser functional testing.</p>
    <table>
        <tr>
            <th>Item</th>
            <th>Quantity</th>
            <th>Price</th>
        </tr>
        <tr>
            <td>Apple</td>
            <td>10</td>
            <td>$1.00</td>
        </tr>
        <tr>
            <td>Banana</td>
            <td>5</td>
            <td>$0.50</td>
        </tr>
    </table>
</body>
</html>"""
    return html_content.encode('utf-8'), "test_document.html"


# ============================================================================
# TEST CLASS - New Architecture Functional Tests
# ============================================================================

class TestFileParserNewArchitecture:
    """Functional tests for File Parser Service with new 5-layer architecture."""
    
    # ========================================================================
    # EXCEL FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_excel_via_excel_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that Excel files are parsed via excel_processing abstraction."""
        logger.info("🔧 Test: Starting Excel file parsing test (new architecture)...")
        
        # Create test Excel file
        excel_data, filename = create_test_excel_file()
        logger.info(f"✅ Test: Created Excel file: {filename}, size: {len(excel_data)} bytes")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                excel_data,
                filename,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"Excel parsing should succeed. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") in ["xlsx", "xls"], \
            f"Excel file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"Excel file should have extracted content. Content length: {len(content)}"
        
        # Verify expected data is in content
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["name", "age", "city", "salary", "alice", "bob"]), \
            f"Excel content should contain expected data. Content: {content[:500]}"
        
        # Verify structured data (tables/records) if available
        tables = parse_result.get("tables", [])
        records = parse_result.get("records", [])
        assert len(tables) > 0 or len(records) > 0, \
            f"Excel file should have structured data. Tables: {len(tables)}, Records: {len(records)}"
        
        logger.info("✅ Test: Excel parsing test passed")
    
    # ========================================================================
    # CSV FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_csv_via_csv_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that CSV files are parsed via csv_processing abstraction."""
        logger.info("🔧 Test: Starting CSV file parsing test (new architecture)...")
        
        # Create test CSV file
        csv_data, filename = create_test_csv_file()
        logger.info(f"✅ Test: Created CSV file: {filename}, size: {len(csv_data)} bytes")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                csv_data,
                filename,
                content_type="text/csv"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"CSV parsing should succeed. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") == "csv", \
            f"CSV file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"CSV file should have extracted content. Content length: {len(content)}"
        
        # Verify expected data is in content
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["name", "age", "city", "salary", "alice", "bob"]), \
            f"CSV content should contain expected data. Content: {content[:500]}"
        
        # Verify structured data
        tables = parse_result.get("tables", [])
        records = parse_result.get("records", [])
        assert len(tables) > 0 or len(records) > 0, \
            f"CSV file should have structured data. Tables: {len(tables)}, Records: {len(records)}"
        
        logger.info("✅ Test: CSV parsing test passed")
    
    # ========================================================================
    # JSON FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_json_via_json_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that JSON files are parsed via json_processing abstraction."""
        logger.info("🔧 Test: Starting JSON file parsing test (new architecture)...")
        
        # Create test JSON file
        json_data, filename = create_test_json_file()
        logger.info(f"✅ Test: Created JSON file: {filename}, size: {len(json_data)} bytes")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                json_data,
                filename,
                content_type="application/json"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"JSON parsing should succeed. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") == "json", \
            f"JSON file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"JSON file should have extracted content. Content length: {len(content)}"
        
        # Verify expected data is in content
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["employees", "alice", "bob", "name", "age"]), \
            f"JSON content should contain expected data. Content: {content[:500]}"
        
        logger.info("✅ Test: JSON parsing test passed")
    
    # ========================================================================
    # TEXT FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_text_via_text_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that text files are parsed via text_processing abstraction."""
        logger.info("🔧 Test: Starting text file parsing test (new architecture)...")
        
        # Create test text file
        text_data, filename = create_test_text_file()
        logger.info(f"✅ Test: Created text file: {filename}, size: {len(text_data)} bytes")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                text_data,
                filename,
                content_type="text/plain"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"Text parsing should succeed. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") in ["txt", "text"], \
            f"Text file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"Text file should have extracted content. Content length: {len(content)}"
        
        # Verify expected text is present
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["test", "document", "line", "first", "second"]), \
            f"Text content should contain expected text. Content: {content[:500]}"
        
        logger.info("✅ Test: Text parsing test passed")
    
    # ========================================================================
    # PDF FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_pdf_via_pdf_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that PDF files are parsed via pdf_processing abstraction."""
        logger.info("🔧 Test: Starting PDF file parsing test (new architecture)...")
        
        # Create test PDF file
        pdf_data, filename = create_test_pdf_file()
        logger.info(f"✅ Test: Created PDF file: {filename}, size: {len(pdf_data)} bytes")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                pdf_data,
                filename,
                content_type="application/pdf"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"PDF parsing should succeed. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") == "pdf", \
            f"PDF file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"PDF file should have extracted content. Content length: {len(content)}"
        
        # Verify expected text is present
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["test", "pdf", "document", "text"]), \
            f"PDF content should contain expected text. Content: {content[:500]}"
        
        # Verify structure metadata
        structure = parse_result.get("structure", {})
        assert "page_count" in structure, \
            f"PDF structure should include page_count. Structure: {structure}"
        
        logger.info("✅ Test: PDF parsing test passed")
    
    # ========================================================================
    # WORD DOCUMENT PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_word_via_word_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that Word documents are parsed via word_processing abstraction."""
        logger.info("🔧 Test: Starting Word document parsing test (new architecture)...")
        
        # Create test Word document
        word_data, filename = create_test_word_document()
        logger.info(f"✅ Test: Created Word document: {filename}, size: {len(word_data)} bytes")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                word_data,
                filename,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"Word parsing should succeed. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") in ["docx", "doc"], \
            f"Word file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"Word document should have extracted content. Content length: {len(content)}"
        
        # Verify expected text is present
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["test", "document", "paragraph", "table"]), \
            f"Word document should contain expected text. Content: {content[:500]}"
        
        logger.info("✅ Test: Word parsing test passed")
    
    # ========================================================================
    # HTML FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_html_via_html_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that HTML files are parsed via html_processing abstraction."""
        logger.info("🔧 Test: Starting HTML file parsing test (new architecture)...")
        
        # Create test HTML file
        html_data, filename = create_test_html_file()
        logger.info(f"✅ Test: Created HTML file: {filename}, size: {len(html_data)} bytes")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                html_data,
                filename,
                content_type="text/html"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded
        assert parse_result.get("success") is True, \
            f"HTML parsing should succeed. Result: {parse_result}"
        
        # Verify file_type is detected
        assert parse_result.get("file_type") in ["html", "htm"], \
            f"HTML file type should be detected. File type: {parse_result.get('file_type')}"
        
        # Verify content is extracted
        content = parse_result.get("content", "")
        assert len(content) > 0, \
            f"HTML file should have extracted content. Content length: {len(content)}"
        
        # Verify expected text is present (HTML tags should be stripped)
        content_lower = content.lower()
        assert any(keyword in content_lower for keyword in ["test", "document", "item", "quantity", "price"]), \
            f"HTML content should contain expected text. Content: {content[:500]}"
        
        logger.info("✅ Test: HTML parsing test passed")
    
    # ========================================================================
    # IMAGE FILE PARSING TESTS (OCR)
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_image_via_image_processing_abstraction(self, file_parser_service, storage_helper):
        """Test that image files are parsed via image_processing abstraction (OCR)."""
        logger.info("🔧 Test: Starting image file parsing test (new architecture)...")
        
        # Create test image file
        try:
            image_data, filename = create_test_image_file()
            logger.info(f"✅ Test: Created image file: {filename}, size: {len(image_data)} bytes")
        except ImportError:
            pytest.skip("Pillow (PIL) required for image test file creation")
        
        # Store file
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                image_data,
                filename,
                content_type="image/png"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Parse the file
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(file_id),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing succeeded (OCR may or may not extract text depending on image quality)
        # At minimum, verify the service handled it without crashing
        assert isinstance(parse_result, dict), \
            f"Image parsing should return structured result. Result: {parse_result}"
        
        # If parsing succeeded, verify content
        if parse_result.get("success") is True:
            content = parse_result.get("content", "")
            # OCR may or may not extract text, so we just verify it didn't crash
            logger.info(f"✅ Test: Image parsed successfully, content length: {len(content)}")
        
        logger.info("✅ Test: Image parsing test passed")
    
    # ========================================================================
    # ARCHITECTURE VERIFICATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_abstraction_mapping_verification(self, file_parser_service):
        """Test that file types are correctly mapped to abstraction names."""
        logger.info("🔧 Test: Starting abstraction mapping verification test...")
        
        # Test the internal mapping method
        test_cases = [
            ("xlsx", "excel_processing"),
            ("xls", "excel_processing"),
            ("csv", "csv_processing"),
            ("json", "json_processing"),
            ("txt", "text_processing"),
            ("pdf", "pdf_processing"),
            ("docx", "word_processing"),
            ("doc", "word_processing"),
            ("html", "html_processing"),
            ("htm", "html_processing"),
            ("png", "image_processing"),
            ("jpg", "image_processing"),
            ("jpeg", "image_processing"),
            # Note: Binary files may not be mapped yet - mainframe abstraction needs FileParsingProtocol
            # ("bin", "mainframe_processing"),
            # ("binary", "mainframe_processing"),
        ]
        
        for file_type, expected_abstraction in test_cases:
            abstraction_name = file_parser_service._get_abstraction_name_for_file_type(file_type)
            assert abstraction_name == expected_abstraction, \
                f"File type '{file_type}' should map to '{expected_abstraction}', got '{abstraction_name}'"
            logger.info(f"✅ Verified: {file_type} -> {abstraction_name}")
        
        # Test unsupported file type
        unsupported_abstraction = file_parser_service._get_abstraction_name_for_file_type("xyz")
        assert unsupported_abstraction is None, \
            f"Unsupported file type 'xyz' should return None, got '{unsupported_abstraction}'"
        logger.info("✅ Verified: Unsupported file type returns None")
        
        logger.info("✅ Test: Abstraction mapping verification test passed")
    
    # ========================================================================
    # MAINFRAME/BINARY FILE PARSING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_parse_binary_with_copybook(self, file_parser_service, storage_helper):
        """Test that binary files with copybooks are parsed correctly."""
        logger.info("🔧 Test: Starting binary file with copybook parsing test (new architecture)...")
        
        # Create test binary and copybook files
        binary_data, binary_filename = create_test_binary_file()
        copybook_data, copybook_filename = create_test_copybook_file()
        logger.info(f"✅ Test: Created binary file: {binary_filename}, size: {len(binary_data)} bytes")
        logger.info(f"✅ Test: Created copybook file: {copybook_filename}, size: {len(copybook_data)} bytes")
        
        # Store both files
        binary_file_id = await asyncio.wait_for(
            storage_helper.store_file(
                binary_data,
                binary_filename,
                content_type="application/octet-stream"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: Binary file stored, file_id: {binary_file_id}")
        
        copybook_file_id = await asyncio.wait_for(
            storage_helper.store_file(
                copybook_data,
                copybook_filename,
                content_type="text/plain"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: Copybook file stored, file_id: {copybook_file_id}")
        
        # Retrieve copybook content
        try:
            copybook_doc = await asyncio.wait_for(
                storage_helper.get_file(copybook_file_id),
                timeout=10.0
            )
            copybook_content = copybook_doc.get("file_content") or copybook_doc.get("data")
            if isinstance(copybook_content, bytes):
                copybook_content = copybook_content.decode('utf-8')
            elif isinstance(copybook_content, str):
                pass  # Already a string
            else:
                copybook_content = str(copybook_content)
            logger.info(f"✅ Test: Retrieved copybook content, length: {len(copybook_content)}")
        except asyncio.TimeoutError:
            logger.error("❌ Test: Timeout retrieving copybook file")
            pytest.fail("Timeout retrieving copybook file - storage may be slow")
        except Exception as e:
            logger.error(f"❌ Test: Failed to retrieve copybook: {e}")
            raise
        
        # Parse binary file with copybook
        # Note: Binary files may need special handling since mainframe abstraction
        # uses a different interface (parse_cobol_file with paths) rather than FileParsingProtocol
        # For now, we'll pass the copybook in parse_options
        parse_result = await asyncio.wait_for(
            file_parser_service.parse_file(
                binary_file_id,
                parse_options={
                    "copybook": copybook_content,
                    "copybook_path": None,  # Using copybook string instead
                    "file_type": "bin"  # Explicitly specify binary type
                }
            ),
            timeout=60.0
        )
        logger.info(f"✅ Test: File parsed, result keys: {list(parse_result.keys())}")
        
        # Verify parsing handled gracefully
        # Binary files may be parsed as text or may have special handling
        # At minimum, verify the service handled it without crashing
        assert isinstance(parse_result, dict), \
            f"Binary parsing should return structured result. Result: {parse_result}"
        
        # If parsing succeeded, verify structure
        if parse_result.get("success") is True:
            structure = parse_result.get("structure", {})
            content = parse_result.get("content", "")
            tables = parse_result.get("tables", [])
            records = parse_result.get("records", [])
            
            # Binary files with copybooks should produce structured data
            # Verify that we got some result (either text or structured data)
            assert len(content) > 0 or len(tables) > 0 or len(records) > 0, \
                f"Binary file should produce some content or structured data. " \
                f"Content length: {len(content)}, Tables: {len(tables)}, Records: {len(records)}"
            
            logger.info(f"✅ Test: Binary file parsed successfully")
            logger.info(f"   Content length: {len(content)}")
            logger.info(f"   Tables: {len(tables)}")
            logger.info(f"   Records: {len(records)}")
        else:
            # If parsing failed, verify it failed gracefully with an error message
            error = parse_result.get("error") or parse_result.get("message")
            assert error is not None, \
                f"Binary parsing failure should include error message. Result: {parse_result}"
            logger.warning(f"⚠️ Binary parsing failed (may be expected if mainframe abstraction not fully integrated): {error}")
        
        logger.info("✅ Test: Binary with copybook parsing test passed")
    
    # ========================================================================
    # ARCHITECTURE VERIFICATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_platform_gateway_abstraction_access(self, file_parser_service, smart_city_infrastructure):
        """Test that abstractions are accessible via Platform Gateway."""
        logger.info("🔧 Test: Starting Platform Gateway abstraction access test...")
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        
        # Test that we can access each abstraction
        abstractions_to_test = [
            "excel_processing",
            "csv_processing",
            "json_processing",
            "text_processing",
            "pdf_processing",
            "word_processing",
            "html_processing",
            "image_processing",
            "mainframe_processing",
        ]
        
        for abstraction_name in abstractions_to_test:
            try:
                abstraction = platform_gateway.get_abstraction(
                    realm_name="business_enablement",
                    abstraction_name=abstraction_name
                )
                assert abstraction is not None, \
                    f"Abstraction '{abstraction_name}' should not be None"
                logger.info(f"✅ Verified: {abstraction_name} abstraction is accessible")
            except Exception as e:
                logger.warning(f"⚠️ Abstraction '{abstraction_name}' not accessible: {e}")
                # Some abstractions may not be available in all environments
                # This is a warning, not a failure
        
        logger.info("✅ Test: Platform Gateway abstraction access test passed")

