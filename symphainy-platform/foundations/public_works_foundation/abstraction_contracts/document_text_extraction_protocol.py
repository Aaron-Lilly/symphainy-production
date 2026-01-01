#!/usr/bin/env python3
"""
Document Text Extraction Protocol - Abstraction Contract

Defines the contract for document text extraction operations across different extraction engines.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define how document text should be extracted
HOW (Infrastructure Implementation): I provide the interface for text extraction logic
"""

from typing import Protocol
from typing import Dict, Any, Optional, List
from datetime import datetime

class DocumentTextExtractionProtocol(Protocol):
    """
    Protocol for document text extraction operations.
    
    This protocol defines how document text should be extracted
    across different extraction engines and technologies.
    """
    
    async def extract_text(self, 
                          file_path: str = None,
                          file_data: bytes = None,
                          page_number: int = None,
                          start_page: int = None,
                          end_page: int = None) -> Dict[str, Any]:
        """
        Extract text from document.
        
        Args:
            file_path: Path to document file
            file_data: Document data as bytes
            page_number: Specific page to extract (optional)
            start_page: Start page for range extraction (optional)
            end_page: End page for range extraction (optional)
            
        Returns:
            Dict[str, Any]: Text extraction result
        """
        ...
    
    async def extract_metadata(self, 
                              file_path: str = None,
                              file_data: bytes = None) -> Dict[str, Any]:
        """
        Extract metadata from document.
        
        Args:
            file_path: Path to document file
            file_data: Document data as bytes
            
        Returns:
            Dict[str, Any]: Metadata extraction result
        """
        ...
    
    async def analyze_document(self, 
                              file_path: str = None,
                              file_data: bytes = None) -> Dict[str, Any]:
        """
        Analyze document structure and content.
        
        Args:
            file_path: Path to document file
            file_data: Document data as bytes
            
        Returns:
            Dict[str, Any]: Document analysis result
        """
        ...
    
    async def get_extraction_capabilities(self) -> Dict[str, Any]:
        """
        Get text extraction capabilities.
        
        Returns:
            Dict[str, Any]: Capabilities information
        """
        ...




















