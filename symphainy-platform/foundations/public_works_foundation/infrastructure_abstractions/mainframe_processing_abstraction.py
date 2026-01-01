#!/usr/bin/env python3
"""
Mainframe Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for mainframe processing operations (COBOL, binary, copybooks).
Provides minimal business logic coordination for mainframe capabilities.

WHAT (Infrastructure): I coordinate mainframe processing operations
HOW (Abstraction): I provide lightweight coordination for mainframe adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# Note: CobolProcessingProtocol is archived, but we keep the import for type hints
# The adapter implements the protocol interface even though the protocol is archived
from typing import Protocol
from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

# Type hint for mainframe adapter (implements parse_file method)
class MainframeAdapterProtocol(Protocol):
    """Protocol for mainframe adapter interface."""
    async def parse_file(self, file_data: bytes, filename: str, copybook_data: bytes) -> Dict[str, Any]:
        ...

logger = logging.getLogger(__name__)

class MainframeProcessingAbstraction:
    """
    Mainframe Processing Infrastructure Abstraction
    
    Lightweight coordination layer for mainframe processing operations (COBOL, binary, copybooks).
    Provides minimal business logic coordination for mainframe capabilities.
    """
    
    def __init__(self, mainframe_adapter: MainframeAdapterProtocol, di_container=None):
        """
        Initialize Mainframe Processing Abstraction.
        
        Args:
            mainframe_adapter: Mainframe processing adapter
            di_container: Dependency injection container
        """
        self.mainframe_adapter = mainframe_adapter
        # Legacy alias for backward compatibility
        self.cobol_adapter = mainframe_adapter
        self.di_container = di_container
        self.service_name = "mainframe_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Mainframe Processing Abstraction initialized")
    
    # ============================================================================
    # ARCHIVED: Legacy file path-based method
    # ============================================================================
    # ARCHIVED: This method is kept for reference but should not be used.
    # Use parse_file() with FileParsingRequest instead.
    # ============================================================================
    async def parse_cobol_file(self, binary_path: str, copybook_path: str) -> Dict[str, Any]:
        """
        Parse mainframe binary file using mainframe adapter.
        
        Args:
            binary_path: Path to binary mainframe file
            copybook_path: Path to copybook file
            
        Returns:
            Dict containing parsed data and metadata
        """
        try:
            result = await self.mainframe_adapter.parse_cobol_file(binary_path, copybook_path)
            
            if not result.get("success"):
                return result
            
            # Add abstraction-level metadata
            result["abstraction"] = "mainframe_processing"
            result["processing_timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Mainframe file parsing failed: {e}")
            raise  # Re-raise for service layer to handle
    
    # ============================================================================
    # NEW: FileParsingProtocol implementation
    # ============================================================================
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse mainframe binary file using mainframe adapter.
        
        Args:
            request: File parsing request with file_data (bytes) and options (copybook)
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Get copybook from options
            copybook_data = None
            # CRITICAL DEBUG: Log request options to debug copybook passing
            print(f"🔍🔍🔍 MainframeProcessingAbstraction.parse_file: request.options={request.options}")
            print(f"🔍🔍🔍 MainframeProcessingAbstraction.parse_file: request.options type={type(request.options)}")
            self.logger.warning(f"🔍🔍🔍 MainframeProcessingAbstraction.parse_file: request.options={request.options}")
            self.logger.warning(f"🔍🔍🔍 MainframeProcessingAbstraction.parse_file: request.options type={type(request.options)}")
            if request.options:
                has_copybook = "copybook" in request.options
                copybook_length = len(str(request.options.get("copybook", "")))
                self.logger.warning(f"🔍🔍🔍 MainframeProcessingAbstraction.parse_file: has_copybook={has_copybook}, copybook_length={copybook_length}, keys={list(request.options.keys()) if isinstance(request.options, dict) else 'NOT_A_DICT'}")
            if request.options:
                copybook = request.options.get("copybook")  # String or bytes
                if copybook:
                    if isinstance(copybook, str):
                        copybook_data = copybook.encode('utf-8')
                    elif isinstance(copybook, bytes):
                        copybook_data = copybook
                    else:
                        return FileParsingResult(
                            success=False,
                            text_content="",
                            structured_data=None,
                            metadata={},
                            error="Copybook must be string or bytes. Provide 'copybook' in options.",
                            timestamp=datetime.utcnow().isoformat()
                        )
            
            if not copybook_data:
                return FileParsingResult(
                    success=False,
                    text_content="",
                    structured_data=None,
                    metadata={},
                    error="Copybook required. Provide 'copybook' (string or bytes) in options.",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Call adapter with bytes
            result = await asyncio.wait_for(
                self.mainframe_adapter.parse_file(
                    request.file_data,
                    request.filename,
                    copybook_data
                ),
                timeout=60.0
            )
            
            # Convert to FileParsingResult
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    text_content="",
                    structured_data=None,
                    metadata={},
                    error=result.get("error", "Unknown error"),
                    timestamp=result.get("timestamp", datetime.utcnow().isoformat())
                )
            
            # Preserve validation_rules from adapter (88-level fields and level-01 metadata records)
            metadata = result.get("metadata", {}).copy()
            if "validation_rules" in result:
                metadata["validation_rules"] = result["validation_rules"]
            
            return FileParsingResult(
                success=True,
                text_content=result.get("text", ""),
                structured_data={
                    "tables": result.get("tables", []),
                    "records": result.get("records", []),
                    "data": result.get("data", [])
                },
                metadata=metadata,  # Includes validation_rules if present
                error=None,
                timestamp=result.get("timestamp", datetime.utcnow().isoformat())
            )
            
        except asyncio.TimeoutError:
            error_msg = "Mainframe parsing timed out after 60 seconds"
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
            self.logger.error(f"❌ Mainframe file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
