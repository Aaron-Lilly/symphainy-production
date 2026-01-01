#!/usr/bin/env python3
"""
Word Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for Word processing operations.
Provides minimal business logic coordination for Word capabilities.

WHAT (Infrastructure): I coordinate Word processing operations
HOW (Abstraction): I provide lightweight coordination for Word adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)

class WordProcessingAbstraction:
    """
    Word Processing Infrastructure Abstraction
    
    Lightweight coordination layer for Word processing operations.
    Provides minimal business logic coordination for Word capabilities.
    """
    
    def __init__(self, python_docx_adapter, di_container=None):
        """
        Initialize Word Processing Abstraction.
        
        Args:
            python_docx_adapter: Python-DOCX adapter
            di_container: Dependency injection container
        """
        self.python_docx_adapter = python_docx_adapter
        self.di_container = di_container
        self.service_name = "word_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Word Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse Word file using Word adapter.
        
        Args:
            request: File parsing request with file_data (bytes)
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Extract text and metadata using bytes directly
            text_result = await asyncio.wait_for(
                self.python_docx_adapter.extract_text_from_bytes(request.file_data),
                timeout=30.0
            )
            
            metadata_result = await asyncio.wait_for(
                self.python_docx_adapter.extract_metadata_from_bytes(request.file_data),
                timeout=10.0
            )
            
            if not text_result.get("success"):
                return FileParsingResult(
                    success=False,
                    text_content="",
                    structured_data=None,
                    metadata={},
                    error=text_result.get("error", "Unknown error"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            return FileParsingResult(
                success=True,
                text_content=text_result.get("text", ""),
                structured_data=None,
                metadata={
                    "file_type": "word",
                    "paragraph_count": text_result.get("paragraph_count", 0),
                    **metadata_result.get("metadata", {})
                },
                error=None,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except asyncio.TimeoutError:
            error_msg = "Word parsing timed out"
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
            self.logger.error(f"❌ Word file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from Word file."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.text_content if result.success else ""
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from Word file."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.metadata if result.success else {}
