#!/usr/bin/env python3
"""
SOP Enhancement Protocol

Defines the interface contract for SOP content enhancement capabilities.
Used by infrastructure abstractions to ensure consistent SOP enhancement.

WHAT (Protocol Role): I define the interface contract for SOP enhancement
HOW (Protocol Implementation): I specify the methods that all SOP enhancement implementations must follow
"""

from typing import Protocol
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class EnhancementResult:
    """SOP enhancement result data class."""
    success: bool
    enhanced_content: str
    metadata: Dict[str, Any]
    error: str = None


class SOPEnhancementProtocol(Protocol):
    """
    Protocol for SOP content enhancement capabilities.
    
    Defines the interface contract that all SOP enhancement implementations
    must follow to ensure consistent SOP enhancement across the platform.
    """
    
    async def enhance_sop_content(self, sop_text: str) -> EnhancementResult:
        """
        Enhance SOP content with better structure and clarity.
        
        Args:
            sop_text: Original SOP text content
            
        Returns:
            EnhancementResult with enhanced content and metadata
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the SOP enhancement service.
        
        Returns:
            Dict with health status information
        """
        ...


