#!/usr/bin/env python3
"""
Image Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for image processing operations (OCR).
Provides minimal business logic coordination for image capabilities.

WHAT (Infrastructure): I coordinate image processing operations
HOW (Abstraction): I provide lightweight coordination for image adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)

class ImageProcessingAbstraction:
    """
    Image Processing Infrastructure Abstraction
    
    Lightweight coordination layer for image processing operations (OCR).
    Provides minimal business logic coordination for image capabilities.
    """
    
    def __init__(self, pytesseract_adapter=None, opencv_adapter=None, di_container=None):
        """
        Initialize Image Processing Abstraction.
        
        Args:
            pytesseract_adapter: PyTesseract OCR adapter
            opencv_adapter: OpenCV image processor (for enhancement)
            di_container: Dependency injection container
        """
        self.pytesseract_adapter = pytesseract_adapter
        self.opencv_adapter = opencv_adapter
        self.di_container = di_container
        self.service_name = "image_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Image Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse image file using OCR adapter.
        
        Args:
            request: File parsing request with file_data (bytes)
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Determine extension from filename
            extension = "png"
            if request.filename.endswith(".jpg") or request.filename.endswith(".jpeg"):
                extension = "jpg"
            elif request.filename.endswith(".gif"):
                extension = "gif"
            elif request.filename.endswith(".bmp"):
                extension = "bmp"
            elif request.filename.endswith(".tiff"):
                extension = "tiff"
            
            # Extract text using OCR - uses bytes directly
            if self.pytesseract_adapter:
                result = await asyncio.wait_for(
                    self.pytesseract_adapter.extract_text_from_bytes(request.file_data),
                    timeout=60.0  # OCR can be slow
                )
                
                if result.get("success"):
                    return FileParsingResult(
                        success=True,
                        text_content=result.get("text", ""),
                        structured_data=None,
                        metadata={
                            "file_type": "image",
                            "ocr_confidence": result.get("confidence", 0),
                            "image_format": extension
                        },
                        error=None,
                        timestamp=datetime.utcnow().isoformat()
                    )
                else:
                    return FileParsingResult(
                        success=False,
                        text_content="",
                        structured_data=None,
                        metadata={},
                        error=result.get("error", "OCR extraction failed"),
                        timestamp=datetime.utcnow().isoformat()
                    )
            else:
                return FileParsingResult(
                    success=False,
                    text_content="",
                    structured_data=None,
                    metadata={},
                    error="PyTesseract adapter not available",
                    timestamp=datetime.utcnow().isoformat()
                )
            
        except asyncio.TimeoutError:
            error_msg = "Image parsing timed out"
            self.logger.error(f"❌ {error_msg}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=error_msg,
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            self.logger.error(f"❌ Image file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from image file using OCR."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.text_content if result.success else ""
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from image file."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.metadata if result.success else {}
