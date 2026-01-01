#!/usr/bin/env python3
"""
Image Processing Protocol - Layer 2

Technology-agnostic interface for image processing operations.
Defines the contract that image processing adapters must implement.

WHAT (Infrastructure): I define image processing capabilities
HOW (Protocol): I specify the interface for image processing operations
"""

from typing import Protocol
from typing import Dict, Any, Optional, List
from datetime import datetime

class ImageProcessingProtocol(Protocol):
    """
    Image Processing Protocol
    
    Technology-agnostic interface for image processing operations.
    Defines the contract that image processing adapters must implement.
    """
    
    async def enhance_image(self, image_path: str, enhancement_type: str = "standard") -> Dict[str, Any]:
        """
        Enhance image for better processing results.
        
        Args:
            image_path: Path to input image
            enhancement_type: Type of enhancement (standard, aggressive, gentle)
            
        Returns:
            Dict containing enhanced image path and metadata
        """
        ...
    
    async def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get image information and metadata.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing image information
        """
        ...
    
    async def detect_text_regions(self, image_path: str) -> Dict[str, Any]:
        """
        Detect text regions in image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing detected text regions
        """
        ...
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get adapter capabilities.
        
        Returns:
            Dict containing adapter capabilities
        """
        ...






