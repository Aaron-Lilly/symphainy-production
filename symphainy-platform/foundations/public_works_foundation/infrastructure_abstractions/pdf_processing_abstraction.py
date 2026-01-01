#!/usr/bin/env python3
"""
PDF Processing Infrastructure Abstraction - Layer 3

Lightweight coordination layer for PDF processing operations.
Provides minimal business logic coordination for PDF capabilities.

WHAT (Infrastructure): I coordinate PDF processing operations
HOW (Abstraction): I provide lightweight coordination for PDF adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..abstraction_contracts.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)

class PdfProcessingAbstraction:
    """
    PDF Processing Infrastructure Abstraction
    
    Lightweight coordination layer for PDF processing operations.
    Provides minimal business logic coordination for PDF capabilities.
    """
    
    def __init__(self, pdfplumber_adapter=None, pypdf2_adapter=None, di_container=None):
        """
        Initialize PDF Processing Abstraction.
        
        Args:
            pdfplumber_adapter: Pdfplumber adapter (preferred for tables)
            pypdf2_adapter: PyPDF2 adapter (fallback for text)
            di_container: Dependency injection container
        """
        self.pdfplumber_adapter = pdfplumber_adapter
        self.pypdf2_adapter = pypdf2_adapter
        self.di_container = di_container
        self.service_name = "pdf_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ PDF Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse PDF file using PDF adapters.
        
        Parsing strategy is determined by content_type in request.options:
        - "structured": Focus on pdfplumber (table extraction) - best for forms, invoices, structured data
        - "unstructured": Focus on PyPDF2 (text extraction) - best for documents, articles, plain text
        - "hybrid" or None: Use both adapters (default) - best for documents with both text and tables
        
        Args:
            request: File parsing request with file_data (bytes) and optional options dict
            
        Returns:
            FileParsingResult: Processing result
        """
        try:
            # Determine parsing strategy based on content_type
            content_type = None
            if request.options:
                content_type = request.options.get("content_type")
                if content_type:
                    content_type = str(content_type).lower().strip()
            
            # Log parsing strategy
            if content_type == "structured":
                self.logger.info("📊 PDF parsing strategy: STRUCTURED (focus on table extraction)")
            elif content_type == "unstructured":
                self.logger.info("📄 PDF parsing strategy: UNSTRUCTURED (focus on text extraction)")
            elif content_type == "hybrid":
                self.logger.info("🔀 PDF parsing strategy: HYBRID (extract both tables and text)")
            else:
                self.logger.info("🔄 PDF parsing strategy: DEFAULT (extract both tables and text)")
                content_type = "hybrid"  # Default to hybrid behavior
            
            tables_result = None
            text_result = None
            tables_text = ""
            
            # Step 1: Extract tables (for structured or hybrid content)
            should_extract_tables = content_type in ["structured", "hybrid", None]
            if should_extract_tables and self.pdfplumber_adapter:
                try:
                    tables_result = await asyncio.wait_for(
                        self.pdfplumber_adapter.extract_tables_from_bytes(request.file_data),
                        timeout=30.0
                    )
                    
                    if tables_result.get("success") and tables_result.get("table_count", 0) > 0:
                        # Extract text from tables
                        for table in tables_result.get("tables", []):
                            for row in table.get("rows", []):
                                tables_text += " ".join(str(cell) for cell in row) + "\n"
                        tables_text = tables_text.strip()
                        self.logger.info(f"✅ Pdfplumber extracted {tables_result.get('table_count', 0)} tables")
                    elif content_type == "structured":
                        # For structured content, warn if no tables found
                        self.logger.warning("⚠️ Structured PDF parsing found no tables - may need text extraction fallback")
                except Exception as e:
                    self.logger.warning(f"⚠️ Pdfplumber table extraction failed: {e}")
                    if content_type == "structured":
                        # For structured content, this is a more serious issue
                        self.logger.error(f"❌ Structured PDF parsing failed: {e}")
            
            # Step 2: Extract text (for unstructured or hybrid content)
            should_extract_text = content_type in ["unstructured", "hybrid", None]
            # Also extract text if structured parsing found no tables (fallback)
            if content_type == "structured" and (not tables_result or tables_result.get("table_count", 0) == 0):
                should_extract_text = True
                self.logger.info("📄 Falling back to text extraction for structured PDF (no tables found)")
            
            if should_extract_text and self.pypdf2_adapter:
                try:
                    text_result = await asyncio.wait_for(
                        self.pypdf2_adapter.extract_text_from_bytes(request.file_data),
                        timeout=30.0
                    )
                    
                    if text_result.get("success"):
                        self.logger.info(f"✅ PyPDF2 extracted text ({len(text_result.get('text', ''))} chars)")
                except Exception as e:
                    self.logger.warning(f"⚠️ PyPDF2 text extraction failed: {e}")
                    if content_type == "unstructured":
                        # For unstructured content, this is a more serious issue
                        self.logger.error(f"❌ Unstructured PDF parsing failed: {e}")
            
            # Step 3: Combine results intelligently
            # Prefer tables_text if available, otherwise use PyPDF2 text
            # If both available, combine them (tables first, then general text)
            final_text = ""
            if tables_text:
                final_text = tables_text
                if text_result and text_result.get("success") and text_result.get("text"):
                    # Append general text if it's different from table text
                    general_text = text_result.get("text", "").strip()
                    if general_text and general_text not in tables_text:
                        final_text += "\n\n" + general_text
            elif text_result and text_result.get("success"):
                final_text = text_result.get("text", "").strip()
            
            # Determine which extractor to report
            extractor_used = []
            if tables_result and tables_result.get("success") and tables_result.get("table_count", 0) > 0:
                extractor_used.append("pdfplumber")
            if text_result and text_result.get("success"):
                extractor_used.append("pypdf2")
            
            # Get page count from either result
            page_count = 1
            if tables_result and tables_result.get("tables"):
                page_count = max([t.get("page_number", 0) for t in tables_result.get("tables", [])], default=0) + 1
            elif text_result:
                page_count = text_result.get("page_count", 1)
            
            # Return combined result
            if final_text or (tables_result and tables_result.get("table_count", 0) > 0):
                return FileParsingResult(
                    success=True,
                    text_content=final_text,
                    structured_data={
                        "tables": tables_result.get("tables", []) if tables_result else [],
                        "table_count": tables_result.get("table_count", 0) if tables_result else 0
                    } if tables_result and tables_result.get("table_count", 0) > 0 else None,
                    metadata={
                        "file_type": "pdf",
                        "content_type": content_type or "hybrid",  # Record the content type used
                        "parsing_strategy": content_type or "hybrid",  # Record the strategy
                        "extractor": "+".join(extractor_used) if extractor_used else "none",
                        "page_count": page_count,
                        **(text_result.get("metadata", {}) if text_result else {})
                    },
                    error=None,
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Both adapters failed or returned no content
            # Provide context-aware error message
            if content_type == "structured":
                error_msg = "Structured PDF parsing failed: No tables found and text extraction unavailable or failed"
            elif content_type == "unstructured":
                error_msg = "Unstructured PDF parsing failed: Text extraction unavailable or failed"
            else:
                error_msg = "PDF parsing failed: Both adapters failed or returned no content"
            
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={
                    "file_type": "pdf",
                    "content_type": content_type or "hybrid",
                    "parsing_strategy": content_type or "hybrid",
                    "extractor": "none"
                },
                error=error_msg,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except asyncio.TimeoutError:
            error_msg = "PDF parsing timed out"
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
            self.logger.error(f"❌ PDF file parsing failed: {e}")
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from PDF file."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.text_content if result.success else ""
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from PDF file."""
        request = FileParsingRequest(file_data=file_data, filename=filename)
        result = await self.parse_file(request)
        return result.metadata if result.success else {}

