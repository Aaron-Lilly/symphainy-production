#!/usr/bin/env python3
"""
Text Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for text processing operations.
Provides minimal business logic coordination for text capabilities.

WHAT (Infrastructure): I coordinate text processing operations
HOW (Abstraction): I provide lightweight coordination for text adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)

class TextProcessingAbstraction:
    """
    Text Processing Infrastructure Abstraction
    
    Lightweight coordination layer for text processing operations.
    Provides minimal business logic coordination for text capabilities.
    """
    
    def __init__(self, text_adapter, di_container=None):
        """
        Initialize Text Processing Abstraction.
        
        Args:
            text_adapter: Text processing adapter
            di_container: Dependency injection container
        """
        self.text_adapter = text_adapter
        self.di_container = di_container
        self.service_name = "text_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Text Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse text file using text adapter.
        
        Args:
            request: File parsing request
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Wrap adapter call with timeout protection
            result = await asyncio.wait_for(
                self.text_adapter.parse_file(request.file_data, request.filename),
                timeout=10.0  # 10 second timeout (text parsing is usually fast)
            )
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    text_content="",
                    structured_data=None,
                    metadata={},
                    error=result.get("error", "Unknown error"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Convert adapter result to FileParsingResult
            return FileParsingResult(
                success=True,
                text_content=result.get("text", ""),
                structured_data=None,
                metadata=result.get("metadata", {}),
                error=None,
                timestamp=result.get("timestamp", datetime.utcnow().isoformat())
            )
            
        except asyncio.TimeoutError:
            error_msg = "Text parsing timed out after 10 seconds"
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
            self.logger.error(f"❌ Text file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from text file."""
        result = await self.text_adapter.extract_text(file_data, filename)
        return result.get("text", "") if result.get("success") else ""
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from text file."""
        result = await self.text_adapter.parse_file(file_data, filename)
        return result.get("metadata", {}) if result.get("success") else {}

