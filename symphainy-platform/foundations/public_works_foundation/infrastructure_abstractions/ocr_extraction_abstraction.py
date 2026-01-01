#!/usr/bin/env python3
"""
OCR Extraction Infrastructure Abstraction - Layer 3

Lightweight coordination layer for OCR text extraction operations.
Provides minimal business logic coordination for OCR capabilities.

WHAT (Infrastructure): I coordinate OCR extraction operations
HOW (Abstraction): I provide lightweight coordination for OCR adapters
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.ocr_extraction_protocol import OCRExtractionProtocol

logger = logging.getLogger(__name__)

class OCRExtractionAbstraction:
    """
    OCR Extraction Infrastructure Abstraction
    
    Lightweight coordination layer for OCR text extraction operations.
    Provides minimal business logic coordination for OCR capabilities.
    """
    
    def __init__(self, ocr_adapter: OCRExtractionProtocol, di_container=None):
        """
        Initialize OCR Extraction Abstraction.
        
        Args:
            ocr_adapter: OCR extraction adapter
            di_container: Dependency injection container
        """
        self.ocr_adapter = ocr_adapter
        self.di_container = di_container
        self.service_name = "ocr_extraction_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ OCR Extraction Abstraction initialized")
    
    async def extract_text(self, image_path: str, language: str = "eng", 
                          config: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract text from image using OCR adapter.
        
        Args:
            image_path: Path to image file
            language: OCR language (default: eng)
            config: OCR configuration string
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            result = await self.ocr_adapter.extract_text(image_path, language, config)
            
            if not result.get("success"):
                return result
            
            # Add abstraction-level metadata
            result["abstraction"] = "ocr_extraction"
            result["processing_timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ OCR text extraction failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Extract text with bounding boxes using OCR adapter.
        
        Args:
            image_path: Path to image file
            language: OCR language (default: eng)
            
        Returns:
            Dict containing text, boxes, and metadata
        """
        try:
            result = await self.ocr_adapter.extract_text_with_boxes(image_path, language)
            
            if not result.get("success"):
                return result
            
            # Add abstraction-level metadata
            result["abstraction"] = "ocr_extraction"
            result["processing_timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ OCR text extraction with boxes failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get list of supported OCR languages.
        
        Returns:
            Dict containing supported languages
        """
        try:
            result = await self.ocr_adapter.get_supported_languages()
            
            if not result.get("success"):
                return result
            
            # Add abstraction-level metadata
            result["abstraction"] = "ocr_extraction"
            result["timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get supported languages: {e}")
            raise  # Re-raise for service layer to handle

        """Get OCR extraction capabilities."""
        try:
            result = await self.ocr_adapter.get_capabilities()
            
            # Add abstraction-level metadata
            result["abstraction"] = "ocr_extraction"
            result["timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get extraction capabilities: {e}")
            raise  # Re-raise for service layer to handle
