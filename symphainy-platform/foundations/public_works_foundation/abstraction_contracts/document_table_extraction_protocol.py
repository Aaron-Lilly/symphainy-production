#!/usr/bin/env python3
"""
Document Table Extraction Protocol - Abstraction Contract

Defines the contract for document table extraction operations across different extraction engines.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define how document tables should be extracted
HOW (Infrastructure Implementation): I provide the interface for table extraction logic
"""

from typing import Protocol
from typing import Dict, Any, Optional, List
from datetime import datetime

class DocumentTableExtractionProtocol(Protocol):
    """
    Protocol for document table extraction operations.
    
    This protocol defines how document tables should be extracted
    across different extraction engines and technologies.
    """
    
    async def extract_tables(self, 
                             file_path: str = None,
                             file_data: bytes = None,
                             page_number: int = None,
                             start_page: int = None,
                             end_page: int = None) -> Dict[str, Any]:
        """
        Extract tables from document.
        
        Args:
            file_path: Path to document file
            file_data: Document data as bytes
            page_number: Specific page to extract (optional)
            start_page: Start page for range extraction (optional)
            end_page: End page for range extraction (optional)
            
        Returns:
            Dict[str, Any]: Table extraction result
        """
        ...
    
    async def analyze_table_structure(self, 
                                     file_path: str = None,
                                     file_data: bytes = None) -> Dict[str, Any]:
        """
        Analyze table structure and content.
        
        Args:
            file_path: Path to document file
            file_data: Document data as bytes
            
        Returns:
            Dict[str, Any]: Table structure analysis result
        """
        ...
    
    async def get_table_statistics(self, 
                                  file_path: str = None,
                                  file_data: bytes = None) -> Dict[str, Any]:
        """
        Get table statistics from document.
        
        Args:
            file_path: Path to document file
            file_data: Document data as bytes
            
        Returns:
            Dict[str, Any]: Table statistics result
        """
        ...
    
    async def get_extraction_capabilities(self) -> Dict[str, Any]:
        """
        Get table extraction capabilities.
        
        Returns:
            Dict[str, Any]: Capabilities information
        """
        ...




















