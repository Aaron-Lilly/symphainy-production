#!/usr/bin/env python3
"""
Utilities Module - File Parser Service

Shared helper methods used across multiple modules.
Enhanced with parsing type determination for Phase 1.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class Utilities:
    """Utilities module for File Parser Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    def get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if '.' in filename:
            return filename.rsplit('.', 1)[-1].lower()
        return ''
    
    def get_parsing_type(
        self,
        file_type: str,
        parse_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Determine parsing type: structured, unstructured, hybrid, workflow, sop
        
        Rule-based (from frontend file type selection):
        - structured: xlsx, csv, json, bin (binary with copybook)
        - unstructured: pdf, docx, txt
        - hybrid: excel_with_text
        - workflow: json, bpmn, drawio
        - sop: docx, pdf, txt, md
        
        Args:
            file_type: File extension (e.g., "xlsx", "pdf")
            parse_options: Optional parsing options (may contain explicit parsing_type)
        
        Returns:
            Parsing type: "structured", "unstructured", "hybrid", "workflow", or "sop"
        """
        # Check parse_options for explicit type
        if parse_options and "parsing_type" in parse_options:
            return parse_options["parsing_type"]
        
        # Rule-based determination
        file_type_lower = file_type.lower() if file_type else ""
        
        # Check for explicit flags in parse_options first (before type-based rules)
        if parse_options:
            if parse_options.get("is_workflow"):
                return "workflow"
            if parse_options.get("is_sop"):
                return "sop"
        
        # Type-based rules
        structured_types = ["xlsx", "xls", "csv", "json", "bin", "binary"]
        unstructured_types = ["pdf", "docx", "doc", "txt", "text"]
        hybrid_types = ["excel_with_text"]
        workflow_types = ["bpmn", "drawio", "json"]  # ⭐ JSON can be workflow if content_type is workflow_sop
        sop_types = ["md", "docx", "pdf", "txt"]  # ⭐ SOP types (but need content_type check to distinguish from unstructured)
        
        if file_type_lower in structured_types:
            return "structured"
        elif file_type_lower in unstructured_types:
            return "unstructured"
        elif file_type_lower in hybrid_types:
            return "hybrid"
        elif file_type_lower in workflow_types:
            return "workflow"
        elif file_type_lower in sop_types:
            return "sop"
        else:
            return "unstructured"  # Default
    
    def get_abstraction_name_for_file_type(self, file_type: str) -> Optional[str]:
        """
        Map file type to abstraction name.
        
        Args:
            file_type: File extension (e.g., "xlsx", "pdf", "docx")
            
        Returns:
            Abstraction name (e.g., "excel_processing", "pdf_processing") or None if unsupported
        """
        file_type_lower = file_type.lower()
        
        # Map file types to abstraction names
        FILE_TYPE_TO_ABSTRACTION = {
            "xlsx": "excel_processing",
            "xls": "excel_processing",
            "docx": "word_processing",
            "doc": "word_processing",
            "pdf": "pdf_processing",
            "html": "html_processing",
            "htm": "html_processing",
            "png": "image_processing",
            "jpg": "image_processing",
            "jpeg": "image_processing",
            "gif": "image_processing",
            "bmp": "image_processing",
            "tiff": "image_processing",
            "txt": "text_processing",
            "text": "text_processing",
            "csv": "csv_processing",
            "json": "json_processing",
            "bin": "mainframe_processing",
            "binary": "mainframe_processing",
            "dat": "mainframe_processing"
        }
        
        return FILE_TYPE_TO_ABSTRACTION.get(file_type_lower)
    
    def extract_text_from_chunks(self, chunks: List[Any]) -> str:
        """Extract text from document chunks."""
        if not chunks:
            return ""
        return "\n".join(chunk.text for chunk in chunks if hasattr(chunk, 'text'))
    
    async def extract_file_metadata(
        self,
        document_data: Any,
        file_type: str
    ) -> Dict[str, Any]:
        """
        Extract metadata from file (internal helper).
        
        NOTE: This method is kept for backward compatibility but metadata extraction
        is now handled by individual file parsing abstractions. This method provides
        basic metadata only.
        """
        try:
            # Basic metadata only - detailed metadata comes from abstractions
            metadata = {
                "file_type": file_type,
                "extracted_at": datetime.utcnow().isoformat(),
                "size": len(document_data) if isinstance(document_data, (bytes, str)) else len(str(document_data)) if document_data else 0
            }
            
            return metadata
            
        except Exception as e:
            self.service.logger.error(f"❌ Metadata extraction failed: {e}")
            return {
                "file_type": file_type,
                "extracted_at": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def get_supported_formats(self) -> Dict[str, Any]:
        """
        Get list of supported file formats (SOA API).
        
        Returns:
            List of supported formats
        """
        return {
            "success": True,
            "supported_formats": self.service.supported_formats,
            "format_count": len(self.service.supported_formats)
        }

