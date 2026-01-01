#!/usr/bin/env python3
"""
Word Processing Protocol - Abstraction Contract

Defines the contract for Word document processing operations.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define how Word documents should be processed
HOW (Infrastructure Implementation): I provide the interface for Word processing logic
"""

from typing import Protocol
from typing import Dict, Any, Optional

class WordProcessingProtocol(Protocol):
    """
    Protocol for Word document processing operations.
    
    This protocol defines the interface for processing Word documents
    including text extraction and metadata extraction.
    """
    
    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content from Word document.
        
        Args:
            file_path: Path to the Word document.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted text and metadata.
                            Expected keys: "success" (bool), "text" (str), "paragraph_count" (int), "error" (str, if any).
        """
        ...
    
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from Word document.
        
        Args:
            file_path: Path to the Word document.
            
        Returns:
            Dict[str, Any]: A dictionary containing the document metadata.
                            Expected keys: "success" (bool), "metadata" (dict), "error" (str, if any).
        """
        ...






