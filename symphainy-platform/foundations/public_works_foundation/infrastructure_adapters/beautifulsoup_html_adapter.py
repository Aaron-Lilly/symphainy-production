#!/usr/bin/env python3
"""
BeautifulSoup HTML Adapter - Raw Technology Client

Raw BeautifulSoup client wrapper for HTML operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw BeautifulSoup HTML operations
HOW (Infrastructure Implementation): I use the BeautifulSoup library with no business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

try:
    from bs4 import BeautifulSoup
except ImportError:
    class BeautifulSoup:
        def __init__(self, content, parser): pass
        def get_text(self): return ""
        @property
        def title(self): return None
        def find_all(self, tag): return []

logger = logging.getLogger(__name__)

class BeautifulSoupHTMLAdapter:
    """
    Raw BeautifulSoup HTML client wrapper - no business logic.
    
    This adapter provides direct access to BeautifulSoup operations for
    HTML document processing.
    """
    
    def __init__(self):
        """Initialize BeautifulSoup HTML Adapter."""
        logger.info("✅ BeautifulSoup HTML Adapter initialized")
    
    async def parse_html(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html_content: The HTML content as string.
            
        Returns:
            Dict[str, Any]: A dictionary containing the parsed content and metadata.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text
            text = soup.get_text()
            
            # Extract metadata
            metadata = {}
            if soup.title:
                metadata["title"] = soup.title.string
            
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    metadata[name] = content
            
            # Count elements
            link_count = len(soup.find_all('a'))
            image_count = len(soup.find_all('img'))
            
            return {
                "success": True,
                "text": text.strip(),
                "metadata": metadata,
                "link_count": link_count,
                "image_count": image_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ BeautifulSoup HTML parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "metadata": {},
                "link_count": 0,
                "image_count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_links(self, html_content: str) -> Dict[str, Any]:
        """
        Extract links from HTML content.
        
        Args:
            html_content: The HTML content as string.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted links.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                text = link.get_text().strip()
                if href:
                    links.append({
                        "href": href,
                        "text": text,
                        "title": link.get('title', '')
                    })
            
            return {
                "success": True,
                "links": links,
                "link_count": len(links),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ BeautifulSoup link extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "links": [],
                "link_count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_images(self, html_content: str) -> Dict[str, Any]:
        """
        Extract images from HTML content.
        
        Args:
            html_content: The HTML content as string.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted images.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                alt = img.get('alt', '')
                title = img.get('title', '')
                if src:
                    images.append({
                        "src": src,
                        "alt": alt,
                        "title": title,
                        "width": img.get('width'),
                        "height": img.get('height')
                    })
            
            return {
                "success": True,
                "images": images,
                "image_count": len(images),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ BeautifulSoup image extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "images": [],
                "image_count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the adapter."""
        return {
            "adapter_name": "BeautifulSoupHTMLAdapter",
            "status": "ready",
            "library_version": getattr(BeautifulSoup, '__version__', 'unknown'),
            "timestamp": datetime.utcnow().isoformat()
        }






