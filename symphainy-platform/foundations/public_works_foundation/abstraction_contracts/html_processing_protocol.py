#!/usr/bin/env python3
"""
HTML Processing Protocol - Abstraction Contract

Defines the contract for HTML document processing operations.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define how HTML documents should be processed
HOW (Infrastructure Implementation): I provide the interface for HTML processing logic
"""

from typing import Protocol
from typing import Dict, Any, Optional

class HTMLProcessingProtocol(Protocol):
    """
    Protocol for HTML document processing operations.
    
    This protocol defines the interface for processing HTML documents
    including content extraction and element analysis.
    """
    
    async def parse_html(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract text and metadata.
        
        Args:
            html_content: The HTML content as string.
            
        Returns:
            Dict[str, Any]: A dictionary containing the parsed content.
                            Expected keys: "success" (bool), "text" (str), "metadata" (dict), "link_count" (int), "image_count" (int), "error" (str, if any).
        """
        ...
    
    async def extract_links(self, html_content: str) -> Dict[str, Any]:
        """
        Extract links from HTML content.
        
        Args:
            html_content: The HTML content as string.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted links.
                            Expected keys: "success" (bool), "links" (list), "link_count" (int), "error" (str, if any).
        """
        ...
    
    async def extract_images(self, html_content: str) -> Dict[str, Any]:
        """
        Extract images from HTML content.
        
        Args:
            html_content: The HTML content as string.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted images.
                            Expected keys: "success" (bool), "images" (list), "image_count" (int), "error" (str, if any).
        """
        ...






