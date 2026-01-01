#!/usr/bin/env python3
"""
Excel Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for Excel processing operations.
Provides minimal business logic coordination for Excel capabilities.

WHAT (Infrastructure): I coordinate Excel processing operations
HOW (Abstraction): I provide lightweight coordination for Excel adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)

class ExcelProcessingAbstraction:
    """
    Excel Processing Infrastructure Abstraction
    
    Lightweight coordination layer for Excel processing operations.
    Provides minimal business logic coordination for Excel capabilities.
    """
    
    def __init__(self, excel_adapter, di_container=None):
        """
        Initialize Excel Processing Abstraction.
        
        Args:
            excel_adapter: Excel processing adapter
            di_container: Dependency injection container
        """
        self.excel_adapter = excel_adapter
        self.di_container = di_container
        self.service_name = "excel_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Excel Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse Excel file using Excel adapter.
        
        Args:
            request: File parsing request
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Wrap adapter call with timeout protection
            result = await asyncio.wait_for(
                self.excel_adapter.parse_file(request.file_data, request.filename),
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
            
            # Convert adapter result to FileParsingResult
            return FileParsingResult(
                success=True,
                text_content=result.get("text", ""),
                structured_data={
                    "tables": result.get("tables", []),
                    "records": result.get("records", []),
                    "data": result.get("data", [])
                },
                metadata=result.get("metadata", {}),
                error=None,
                timestamp=result.get("timestamp", datetime.utcnow().isoformat())
            )
            
        except asyncio.TimeoutError:
            error_msg = "Excel parsing timed out after 30 seconds"
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
            self.logger.error(f"❌ Excel file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from Excel file."""
        result = await self.excel_adapter.extract_text(file_data, filename)
        return result.get("text", "") if result.get("success") else ""
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from Excel file."""
        result = await self.excel_adapter.parse_file(file_data, filename)
        return result.get("metadata", {}) if result.get("success") else {}

