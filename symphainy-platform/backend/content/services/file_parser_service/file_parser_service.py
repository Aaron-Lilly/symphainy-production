#!/usr/bin/env python3
"""
File Parser Service - Phase 1.1a: Structured Parsing Vertical Slice

WHAT: Parses files into structured formats across multiple file types
HOW: Provides unified file parsing APIs via micro-modules with parsing type determination

Phase 1.1a: Structured parsing vertical slice - structured files only for now.
Other parsing types (unstructured, hybrid, workflow, SOP) will be added in Phase 1.1b.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase

# Import micro-modules
from .modules.initialization import Initialization
from .modules.utilities import Utilities
from .modules.file_retrieval import FileRetrieval
from .modules.file_parsing import FileParsing
from .modules.parsing_orchestrator import ParsingOrchestrator


class FileParserService(RealmServiceBase):
    """
    File Parser enabling service for Business Enablement.
    
    Phase 1.1b: Structured, Unstructured, and Hybrid parsing
    - ✅ Structured parsing (Excel, CSV, JSON, Binary + Copybook)
    - ✅ Unstructured parsing (PDF, Word, Text)
    - ✅ Hybrid parsing (structured + unstructured, 3 JSON files)
    - ⏳ Workflow parsing (will be added later)
    - ⏳ SOP parsing (will be added later)
    
    Provides unified file parsing capabilities across multiple formats:
    - PDF documents
    - Microsoft Office (Word, Excel, PowerPoint)
    - Plain text
    - HTML/XML
    - Legacy formats (COBOL, mainframe) - ✅ PRESERVED
    - Images (OCR)
    - RTF documents
    
    Integrates with Smart City services for storage, validation, and lineage tracking.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize File Parser Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        # Business Enablement uses Smart City SOA APIs, not direct infrastructure access
        self.librarian = None
        self.content_steward = None  # Primary API for file retrieval
        self.data_steward = None
        self.nurse = None  # ✅ Added for observability
        
        # Supported file formats
        self.supported_formats = [
            "pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt",
            "txt", "html", "xml", "json", "csv",
            "bin", "binary", "cpy", "copybook",  # Mainframe/Binary/COBOL - ✅ PRESERVED
            "rtf", "png", "jpg", "jpeg"
        ]
        
        # Initialize micro-modules
        self.utilities_module = Utilities(self)
        self.initialization_module = Initialization(self)
        self.file_retrieval_module = FileRetrieval(self)
        self.file_parsing_module = FileParsing(self)
        self.parsing_orchestrator_module = ParsingOrchestrator(self)  # ✅ NEW - Phase 1.1a
    
    async def initialize(self) -> bool:
        """Initialize File Parser Service."""
        await super().initialize()
        return await self.initialization_module.initialize()
    
    # SOA API Methods - delegate to modules
    async def retrieve_document(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve file via Content Steward SOA API (Smart City service)."""
        return await self.file_retrieval_module.retrieve_document(file_id)
    
    async def parse_file(
        self,
        file_id: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse file into structured format (SOA API).
        
        Phase 1.1a: Structured parsing only
        - ✅ Structured files (Excel, CSV, JSON, Binary + Copybook)
        - ⏳ Other types will return error (to be implemented in Phase 1.1b)
        
        Args:
            file_id: File identifier
            parse_options: Optional parsing options (includes copybook for binary files)
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Parsed result dictionary
        """
        return await self.file_parsing_module.parse_file(
            file_id, parse_options, user_context
        )
    
    async def detect_file_type(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Detect file type from file ID or content (SOA API)."""
        return await self.file_parsing_module.detect_file_type(file_id, user_context)
    
    async def extract_content(self, file_id: str) -> Dict[str, Any]:
        """Extract plain text content from file (SOA API)."""
        return await self.file_parsing_module.extract_content(file_id)
    
    async def extract_metadata(self, file_id: str) -> Dict[str, Any]:
        """Extract metadata from file (SOA API)."""
        return await self.file_parsing_module.extract_metadata(file_id)
    
    async def get_supported_formats(self) -> Dict[str, Any]:
        """Get list of supported file formats (SOA API)."""
        return await self.utilities_module.get_supported_formats()
    
    # Health & Metadata
    async def health_check(self) -> Dict[str, Any]:
        """Health check."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "supported_formats": len(self.supported_formats),
            "phase": "1.1b - Structured, Unstructured, and Hybrid Parsing",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities."""
        return {
            "service_name": self.service_name,
            "service_type": "enabling_service",
            "phase": "1.1b - Structured, Unstructured, and Hybrid Parsing",
            "capabilities": ["file_parsing", "format_detection", "content_extraction", "metadata_extraction"],
            "soa_apis": ["parse_file", "detect_file_type", "extract_content", "extract_metadata", "get_supported_formats"],
            "mcp_tools": [],  # Enabling services don't have MCP tools (orchestrators do)
            "supported_formats": self.supported_formats,
            "parsing_types": {
                "structured": "✅ Implemented (Phase 1.1b)",
                "unstructured": "✅ Implemented (Phase 1.1b)",
                "hybrid": "✅ Implemented (Phase 1.1b)",
                "workflow": "⏳ Coming soon",
                "sop": "⏳ Coming soon"
            }
        }

