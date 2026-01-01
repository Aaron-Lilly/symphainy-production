#!/usr/bin/env python3
"""
Text Extraction Abstraction - Lightweight Infrastructure Coordination

Lightweight coordination of text extraction adapters.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I coordinate text extraction adapters
HOW (Infrastructure Implementation): I provide simple text extraction coordination

================================================================================
ARCHIVED: This abstraction is archived. File parsing now uses file type-specific
abstractions (pdf_processing, word_processing, etc.) that implement FileParsingProtocol.

Unique Capabilities (not provided by new abstractions):
- Page-level extraction: extract_text(page_number=5)
- Page range extraction: extract_text(start_page=10, end_page=20)
- Document structure analysis: analyze_document_structure()

If page-level extraction is needed in the future, we can either:
1. Add page support to FileParsingRequest.options
2. Create new page-specific abstractions
3. Fix and use this archived abstraction

This abstraction is kept for reference only.
================================================================================
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.document_text_extraction_protocol import DocumentTextExtractionProtocol

logger = logging.getLogger(__name__)

# ============================================================================
# ARCHIVED: Legacy abstraction - kept for reference only
# ============================================================================
# File parsing now uses file type-specific abstractions (pdf_processing, etc.)
# that implement FileParsingProtocol. This abstraction is not instantiated
# or used anywhere in the codebase.
# ============================================================================
class TextExtractionAbstraction(DocumentTextExtractionProtocol):
    """
    Lightweight text extraction abstraction.
    
    Simple coordination of text extraction adapters with minimal business logic.
    """
    
    def __init__(self, text_extractor, di_container=None):
        """Initialize text extraction abstraction."""
        self.text_extractor = text_extractor
        self.di_container = di_container
        self.service_name = "text_extraction_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Text Extraction Abstraction initialized")
    
    async def extract_text(self, 
                          file_path: str = None,
                          page_number: int = None,
                          start_page: int = None,
                          end_page: int = None) -> Dict[str, Any]:
        """Extract text from document."""
        try:
            if page_number is not None:
                result = await self.text_extractor.extract_text_from_page(file_path, page_number)
            elif start_page is not None and end_page is not None:
                result = await self.text_extractor.extract_text_from_page_range(file_path, start_page, end_page)
            elif file_data is not None:
                result = await self.text_extractor.extract_text_from_bytes(file_data)
            else:
                result = await self.text_extractor.extract_text_from_file(file_path)
            
            return result
                
        except Exception as e:
            self.logger.error(f"❌ Text extraction failed: {e}")
            raise  # Re-raise for service layer to handle

        """Extract metadata from document."""
        try:
            if file_data is not None:
                result = await self.text_extractor.extract_metadata_from_bytes(file_data)
            else:
                result = await self.text_extractor.extract_metadata(file_path)
            
            return result
                
        except Exception as e:
            self.logger.error(f"❌ Metadata extraction failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def analyze_document_structure(self, file_path: str = None, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze document structure and content."""
        try:
            if file_data is not None:
                result = await self.text_extractor.get_document_info_from_bytes(file_data)
            else:
                result = await self.text_extractor.get_document_info(file_path)
            
            return result
                
        except Exception as e:
            self.logger.error(f"❌ Document analysis failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_text_extraction_capabilities(self) -> Dict[str, Any]:
        """Get text extraction capabilities."""
        try:
            result = await self.text_extractor.get_extractor_info()
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to get extraction capabilities: {e}")
            raise  # Re-raise for service layer to handle
