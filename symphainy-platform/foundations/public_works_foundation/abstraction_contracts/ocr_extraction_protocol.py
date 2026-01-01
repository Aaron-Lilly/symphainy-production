#!/usr/bin/env python3
"""
OCR Extraction Protocol - Layer 2

Technology-agnostic interface for OCR text extraction operations.
Defines the contract that OCR adapters must implement.

WHAT (Infrastructure): I define OCR extraction capabilities
HOW (Protocol): I specify the interface for OCR operations
"""

from typing import Protocol
from typing import Dict, Any, Optional, List
from datetime import datetime

class OCRExtractionProtocol(Protocol):
    """
    OCR Extraction Protocol
    
    Technology-agnostic interface for OCR text extraction operations.
    Defines the contract that OCR adapters must implement.
    """
    
    async def extract_text(self, image_path: str, language: str = "eng", 
                          config: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image file
            language: OCR language (default: eng)
            config: OCR configuration string
            
        Returns:
            Dict containing extracted text and metadata
        """
        ...
    
    async def extract_text_with_boxes(self, image_path: str, language: str = "eng") -> Dict[str, Any]:
        """
        Extract text with bounding boxes using OCR.
        
        Args:
            image_path: Path to image file
            language: OCR language (default: eng)
            
        Returns:
            Dict containing text, boxes, and metadata
        """
        ...
    
    async def get_supported_languages(self) -> Dict[str, Any]:
        """
        Get list of supported OCR languages.
        
        Returns:
            Dict containing supported languages
        """
        ...
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get adapter capabilities.
        
        Returns:
            Dict containing adapter capabilities
        """
        ...






