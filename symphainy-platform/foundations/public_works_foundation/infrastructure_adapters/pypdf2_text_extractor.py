#!/usr/bin/env python3
"""
PyPDF2 Text Extractor Adapter - Raw Technology Client

Raw PyPDF2 client wrapper for PDF text extraction operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw PyPDF2 text extraction operations
HOW (Infrastructure Implementation): I use real PyPDF2 client with no business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

try:
    import PyPDF2
    from PyPDF2 import PdfReader
except ImportError:
    class PdfReader:
        def __init__(self, file): pass
        def pages(self): return []
        @property
        def metadata(self): return {}

logger = logging.getLogger(__name__)

class PyPDF2TextExtractor:
    """
    Raw PyPDF2 client wrapper for text extraction - no business logic.
    
    This adapter provides direct access to PyPDF2 text extraction operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self):
        """Initialize PyPDF2 text extractor adapter."""
        self.extractor_name = "pypdf2_text_extractor"
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"✅ {self.extractor_name} initialized")
    
    # ============================================================================
    # RAW TEXT EXTRACTION OPERATIONS
    # ============================================================================
    
    async def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """Raw text extraction from file path - no business logic."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Extract text from all pages
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Get metadata
                metadata = pdf_reader.metadata or {}
                
                return {
                    "success": True,
                    "text": text.strip(),
                    "page_count": len(pdf_reader.pages),
                    "metadata": metadata,
                    "extractor": self.extractor_name,
                    "extraction_timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 text extraction failed from file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text_from_bytes(self, file_data: bytes) -> Dict[str, Any]:
        """Raw text extraction from bytes - no business logic."""
        try:
            import io
            
            # Create file-like object from bytes
            file_like = io.BytesIO(file_data)
            pdf_reader = PdfReader(file_like)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Get metadata
            metadata = pdf_reader.metadata or {}
            
            return {
                "success": True,
                "text": text.strip(),
                "page_count": len(pdf_reader.pages),
                "metadata": metadata,
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 text extraction failed from bytes: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text_from_page(self, file_path: str, page_number: int) -> Dict[str, Any]:
        """Raw text extraction from specific page - no business logic."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Validate page number
                if page_number < 0 or page_number >= len(pdf_reader.pages):
                    return {
                        "success": False,
                        "error": f"Page number {page_number} out of range (0-{len(pdf_reader.pages)-1})",
                        "text": "",
                        "extractor": self.extractor_name
                    }
                
                # Extract text from specific page
                page = pdf_reader.pages[page_number]
                text = page.extract_text()
                
                return {
                    "success": True,
                    "text": text.strip() if text else "",
                    "page_number": page_number,
                    "total_pages": len(pdf_reader.pages),
                    "extractor": self.extractor_name,
                    "extraction_timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 text extraction failed from page {page_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text_from_page_range(self, file_path: str, start_page: int, end_page: int) -> Dict[str, Any]:
        """Raw text extraction from page range - no business logic."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Validate page range
                total_pages = len(pdf_reader.pages)
                if start_page < 0 or end_page >= total_pages or start_page > end_page:
                    return {
                        "success": False,
                        "error": f"Invalid page range {start_page}-{end_page} (total pages: {total_pages})",
                        "text": "",
                        "extractor": self.extractor_name
                    }
                
                # Extract text from page range
                text = ""
                for page_num in range(start_page, end_page + 1):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return {
                    "success": True,
                    "text": text.strip(),
                    "start_page": start_page,
                    "end_page": end_page,
                    "pages_extracted": end_page - start_page + 1,
                    "total_pages": total_pages,
                    "extractor": self.extractor_name,
                    "extraction_timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 text extraction failed from page range {start_page}-{end_page}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # RAW METADATA EXTRACTION OPERATIONS
    # ============================================================================
    
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Raw metadata extraction - no business logic."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                metadata = pdf_reader.metadata or {}
                
                return {
                    "success": True,
                    "metadata": metadata,
                    "page_count": len(pdf_reader.pages),
                    "extractor": self.extractor_name,
                    "extraction_timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 metadata extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {},
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_metadata_from_bytes(self, file_data: bytes) -> Dict[str, Any]:
        """Raw metadata extraction from bytes - no business logic."""
        try:
            import io
            
            # Create file-like object from bytes
            file_like = io.BytesIO(file_data)
            pdf_reader = PdfReader(file_like)
            metadata = pdf_reader.metadata or {}
            
            return {
                "success": True,
                "metadata": metadata,
                "page_count": len(pdf_reader.pages),
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 metadata extraction from bytes failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {},
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # RAW DOCUMENT ANALYSIS OPERATIONS
    # ============================================================================
    
    async def get_document_info(self, file_path: str) -> Dict[str, Any]:
        """Raw document info extraction - no business logic."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Get basic document info
                metadata = pdf_reader.metadata or {}
                page_count = len(pdf_reader.pages)
                
                # Analyze first few pages for text content
                text_samples = []
                for i, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
                    page_text = page.extract_text()
                    if page_text:
                        text_samples.append({
                            "page": i,
                            "text_length": len(page_text),
                            "text_preview": page_text[:100] + "..." if len(page_text) > 100 else page_text
                        })
                
                return {
                    "success": True,
                    "page_count": page_count,
                    "metadata": metadata,
                    "text_samples": text_samples,
                    "has_text_content": any(sample["text_length"] > 0 for sample in text_samples),
                    "extractor": self.extractor_name,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 document info extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extractor": self.extractor_name,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_document_info_from_bytes(self, file_data: bytes) -> Dict[str, Any]:
        """Raw document info extraction from bytes - no business logic."""
        try:
            import io
            
            # Create file-like object from bytes
            file_like = io.BytesIO(file_data)
            pdf_reader = PdfReader(file_like)
            
            # Get basic document info
            metadata = pdf_reader.metadata or {}
            page_count = len(pdf_reader.pages)
            
            # Analyze first few pages for text content
            text_samples = []
            for i, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
                page_text = page.extract_text()
                if page_text:
                    text_samples.append({
                        "page": i,
                        "text_length": len(page_text),
                        "text_preview": page_text[:100] + "..." if len(page_text) > 100 else page_text
                    })
            
            return {
                "success": True,
                "page_count": page_count,
                "metadata": metadata,
                "text_samples": text_samples,
                "has_text_content": any(sample["text_length"] > 0 for sample in text_samples),
                "extractor": self.extractor_name,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 document info extraction from bytes failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extractor": self.extractor_name,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_extraction(self) -> Dict[str, Any]:
        """Test PyPDF2 extraction capability - no business logic."""
        try:
            # Test with a simple PDF creation and extraction
            import io
            
            # Create a simple test PDF in memory
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Create PDF in memory
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, "Test PDF for PyPDF2 extraction")
            c.save()
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            # Test extraction
            result = await self.extract_text_from_bytes(pdf_bytes)
            
            return {
                "success": True,
                "message": "PyPDF2 text extraction test successful",
                "test_result": result,
                "extractor": self.extractor_name,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 extraction test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extractor": self.extractor_name,
                "test_timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_extractor_info(self) -> Dict[str, Any]:
        """Get PyPDF2 extractor information - no business logic."""
        return {
            "extractor_name": self.extractor_name,
            "extractor_type": "text_extraction",
            "library": "PyPDF2",
            "version": PyPDF2.__version__ if hasattr(PyPDF2, '__version__') else "unknown",
            "capabilities": [
                "text_extraction",
                "metadata_extraction", 
                "page_range_extraction",
                "document_analysis"
            ],
            "supported_formats": ["pdf"],
            "timestamp": datetime.utcnow().isoformat()
        }




















