#!/usr/bin/env python3
"""
Text Processing Adapter - Raw Technology Client

Raw text processing wrapper for plain text document operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw text processing operations
HOW (Infrastructure Implementation): I use standard library text decoding with no business logic
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TextProcessingAdapter:
    """
    Raw text processing wrapper - no business logic.
    
    This adapter provides direct access to text decoding operations for
    plain text document processing.
    """
    
    def __init__(self):
        """Initialize Text Processing Adapter."""
        logger.info("✅ Text Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse text file from bytes.
        
        Args:
            file_data: Text file content as bytes
            filename: Original filename (for logging)
            
        Returns:
            Dict[str, Any]: A dictionary containing parsed text and metadata.
        """
        try:
            # Try UTF-8 first
            try:
                text_content = file_data.decode('utf-8')
                encoding = "utf-8"
            except UnicodeDecodeError:
                # Fallback to latin-1 (handles most encodings)
                try:
                    text_content = file_data.decode('latin-1')
                    encoding = "latin-1"
                except UnicodeDecodeError:
                    # Last resort: ignore errors
                    text_content = file_data.decode('utf-8', errors='ignore')
                    encoding = "utf-8 (with errors ignored)"
            
            return {
                "success": True,
                "text": text_content,
                "metadata": {
                    "file_type": "text",
                    "encoding": encoding,
                    "character_count": len(text_content),
                    "line_count": len(text_content.splitlines()),
                    "filename": filename
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Text file parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text content from text file.
        
        Args:
            file_data: Text file content as bytes
            filename: Original filename
            
        Returns:
            Dict[str, Any]: A dictionary containing extracted text.
        """
        result = await self.parse_file(file_data, filename)
        if result.get("success"):
            return {
                "success": True,
                "text": result.get("text", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the adapter."""
        return {
            "adapter_name": "TextProcessingAdapter",
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }

