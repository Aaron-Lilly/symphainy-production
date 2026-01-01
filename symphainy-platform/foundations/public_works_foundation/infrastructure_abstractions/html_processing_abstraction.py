#!/usr/bin/env python3
"""
HTML Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for HTML processing operations.
Provides minimal business logic coordination for HTML capabilities.

WHAT (Infrastructure): I coordinate HTML processing operations
HOW (Abstraction): I provide lightweight coordination for HTML adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)

class HtmlProcessingAbstraction:
    """
    HTML Processing Infrastructure Abstraction
    
    Lightweight coordination layer for HTML processing operations.
    Provides minimal business logic coordination for HTML capabilities.
    """
    
    def __init__(self, beautifulsoup_adapter, di_container=None):
        """
        Initialize HTML Processing Abstraction.
        
        Args:
            beautifulsoup_adapter: BeautifulSoup HTML adapter
            di_container: Dependency injection container
        """
        self.beautifulsoup_adapter = beautifulsoup_adapter
        self.di_container = di_container
        self.service_name = "html_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ HTML Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse HTML file using HTML adapter.
        
        Args:
            request: File parsing request
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Decode bytes to string for BeautifulSoup
            try:
                html_content = request.file_data.decode('utf-8')
            except UnicodeDecodeError:
                html_content = request.file_data.decode('latin-1', errors='ignore')
            
            # Wrap adapter call with timeout protection
            result = await asyncio.wait_for(
                self.beautifulsoup_adapter.parse_html(html_content),
                timeout=30.0  # 30 second timeout
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
            
            # Extract tables from HTML (if any)
            # BeautifulSoup adapter doesn't extract tables, but we can add that later if needed
            structured_data = None
            
            return FileParsingResult(
                success=True,
                text_content=result.get("text", ""),
                structured_data=structured_data,
                metadata={
                    "file_type": "html",
                    "link_count": result.get("link_count", 0),
                    "image_count": result.get("image_count", 0),
                    **result.get("metadata", {})
                },
                error=None,
                timestamp=result.get("timestamp", datetime.utcnow().isoformat())
            )
            
        except asyncio.TimeoutError:
            error_msg = "HTML parsing timed out after 30 seconds"
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
            self.logger.error(f"❌ HTML file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from HTML file."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.text_content if result.success else ""
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from HTML file."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.metadata if result.success else {}
