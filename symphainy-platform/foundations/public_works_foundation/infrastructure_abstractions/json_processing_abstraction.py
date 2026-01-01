#!/usr/bin/env python3
"""
JSON Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for JSON processing operations.
Provides minimal business logic coordination for JSON capabilities.

WHAT (Infrastructure): I coordinate JSON processing operations
HOW (Abstraction): I provide lightweight coordination for JSON adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)

class JsonProcessingAbstraction:
    """
    JSON Processing Infrastructure Abstraction
    
    Lightweight coordination layer for JSON processing operations.
    Provides minimal business logic coordination for JSON capabilities.
    """
    
    def __init__(self, json_adapter, di_container=None):
        """
        Initialize JSON Processing Abstraction.
        
        Args:
            json_adapter: JSON processing adapter
            di_container: Dependency injection container
        """
        self.json_adapter = json_adapter
        self.di_container = di_container
        self.service_name = "json_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ JSON Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse JSON file using JSON adapter.
        
        Args:
            request: File parsing request
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Wrap adapter call with timeout protection
            result = await asyncio.wait_for(
                self.json_adapter.parse_file(request.file_data, request.filename),
                timeout=10.0  # 10 second timeout (JSON is usually fast)
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
                structured_data={
                    "data": result.get("data"),
                    "records": result.get("records", [])
                },
                metadata=result.get("metadata", {}),
                error=None,
                timestamp=result.get("timestamp", datetime.utcnow().isoformat())
            )
            
        except asyncio.TimeoutError:
            error_msg = "JSON parsing timed out after 10 seconds"
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
            self.logger.error(f"❌ JSON file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from JSON file."""
        result = await self.json_adapter.extract_text(file_data, filename)
        return result.get("text", "") if result.get("success") else ""
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from JSON file."""
        result = await self.json_adapter.parse_file(file_data, filename)
        return result.get("metadata", {}) if result.get("success") else {}

