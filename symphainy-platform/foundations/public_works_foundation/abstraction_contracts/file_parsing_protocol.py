#!/usr/bin/env python3
"""
File Parsing Protocol - Abstraction Contract

Common interface for all file parsing abstractions.
This protocol ensures consistent behavior across all file type parsers.

WHAT (Infrastructure Role): I define the contract for file parsing abstractions
HOW (Infrastructure Implementation): I provide a Protocol that all file parsers must implement
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class FileParsingRequest:
    """Request for file parsing."""
    file_data: bytes
    filename: str
    options: Optional[Dict[str, Any]] = None

@dataclass
class FileParsingResult:
    """Result from file parsing."""
    success: bool
    text_content: str
    structured_data: Optional[Any] = None  # Tables, records, etc.
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None

class FileParsingProtocol(Protocol):
    """Protocol for file parsing abstractions."""
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse file and return structured result.
        
        Args:
            request: File parsing request with file_data, filename, and options
            
        Returns:
            FileParsingResult: Parsing result with text, structured data, and metadata
        """
        ...
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """
        Extract plain text from file.
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            
        Returns:
            str: Extracted text content
        """
        ...
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from file.
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            
        Returns:
            Dict[str, Any]: Extracted metadata
        """
        ...

