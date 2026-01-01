"""
Test Document Processing Adapters - Layer 1

Validates that all document processing adapters can be initialized.
This catches missing dependencies at Layer 1, not Layer 2.

REQUIRED ADAPTERS (must initialize):
- PyTesseractOCRAdapter (for image OCR)
- OpenCVImageProcessor (for image enhancement)

OPTIONAL ADAPTERS (should initialize if dependencies available):
- BeautifulSoupHTMLAdapter
- PythonDocxAdapter
- PdfplumberTableExtractor
- PyPDF2TextExtractor
- CobolProcessingAdapter
- DocumentProcessingAdapter
"""

import pytest
import os

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

@pytest.mark.integration
@pytest.mark.infrastructure

class TestDocumentProcessingAdapters:
    """Test all document processing adapters can be initialized."""
    
    def test_pytesseract_adapter_initialization(self):
        """Test PyTesseractOCRAdapter can be initialized (REQUIRED)."""
        from foundations.public_works_foundation.infrastructure_adapters.pytesseract_ocr_adapter import PyTesseractOCRAdapter
        
        # This should raise RuntimeError with clear message if dependencies are missing
        try:
            adapter = PyTesseractOCRAdapter()
            assert adapter is not None, "Adapter should be initialized"
            assert adapter.pytesseract_available is True, "pytesseract must be available (REQUIRED)"
            assert adapter.np_available is True, "numpy must be available (REQUIRED)"
        except RuntimeError as e:
            error_msg = str(e)
            assert "pytesseract" in error_msg.lower() or "numpy" in error_msg.lower(),                 f"Error message should mention missing dependency: {error_msg}"
            assert "install" in error_msg.lower(),                 f"Error message should include installation instructions: {error_msg}"
            pytest.fail(f"PyTesseractOCRAdapter failed to initialize (REQUIRED): {e}")
    
    def test_opencv_adapter_initialization(self):
        """Test OpenCVImageProcessor can be initialized (REQUIRED)."""
        from foundations.public_works_foundation.infrastructure_adapters.opencv_image_processor import OpenCVImageProcessor
        
        # This should raise RuntimeError with clear message if dependencies are missing
        try:
            adapter = OpenCVImageProcessor()
            assert adapter is not None, "Adapter should be initialized"
            assert adapter.cv2_available is True, "opencv-python must be available (REQUIRED)"
            assert adapter.np_available is True, "numpy must be available (REQUIRED)"
        except RuntimeError as e:
            error_msg = str(e)
            assert "opencv" in error_msg.lower() or "numpy" in error_msg.lower(),                 f"Error message should mention missing dependency: {error_msg}"
            assert "install" in error_msg.lower(),                 f"Error message should include installation instructions: {error_msg}"
            pytest.fail(f"OpenCVImageProcessor failed to initialize (REQUIRED): {e}")
    
    def test_beautifulsoup_adapter_initialization(self):
        """Test BeautifulSoupHTMLAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.beautifulsoup_html_adapter import BeautifulSoupHTMLAdapter
        
        adapter = BeautifulSoupHTMLAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_python_docx_adapter_initialization(self):
        """Test PythonDocxAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.python_docx_adapter import PythonDocxAdapter
        
        adapter = PythonDocxAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_pdfplumber_adapter_initialization(self):
        """Test PdfplumberTableExtractor can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.pdfplumber_table_extractor import PdfplumberTableExtractor
        
        adapter = PdfplumberTableExtractor()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_pypdf2_adapter_initialization(self):
        """Test PyPDF2TextExtractor can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.pypdf2_text_extractor import PyPDF2TextExtractor
        
        adapter = PyPDF2TextExtractor()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_cobol_adapter_initialization(self):
        """Test CobolProcessingAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.cobol_processing_adapter import CobolProcessingAdapter
        
        adapter = CobolProcessingAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_document_processing_adapter_initialization(self):
        """Test DocumentProcessingAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.document_processing_adapter import DocumentProcessingAdapter
        
        adapter = DocumentProcessingAdapter()
        assert adapter is not None, "Adapter should be initialized"
