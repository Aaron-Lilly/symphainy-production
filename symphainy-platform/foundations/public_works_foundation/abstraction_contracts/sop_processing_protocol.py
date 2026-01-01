#!/usr/bin/env python3
"""
SOP Processing Protocol

Defines the interface contract for SOP processing capabilities.
Used by infrastructure abstractions to ensure consistent SOP processing.

WHAT (Protocol Role): I define the interface contract for SOP processing
HOW (Protocol Implementation): I specify the required methods and data structures
"""

from typing import Protocol
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SOPStructure:
    """SOP structure data class."""
    title: str
    description: str
    steps: List[Dict[str, Any]]
    version: str
    metadata: Dict[str, Any]


@dataclass
class SOPValidationResult:
    """SOP validation result data class."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    validation_timestamp: datetime


class SOPProcessingProtocol(Protocol):
    """
    Protocol for SOP processing capabilities.
    
    Defines the interface contract that all SOP processing implementations
    must follow to ensure consistent SOP processing across the platform.
    """
    
    async def extract_sop_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract SOP structure from text.
        
        Args:
            text: SOP text content
            
        Returns:
            Dict with extracted SOP structure
        """
        ...
    
    async def normalize_sop_steps(self, steps: List[str]) -> List[Dict[str, Any]]:
        """
        Normalize SOP steps for consistent structure.
        
        Args:
            steps: List of raw step strings
            
        Returns:
            List of normalized step dictionaries
        """
        ...
    
    async def validate_sop_structure(self, sop_data: Dict[str, Any]) -> SOPValidationResult:
        """
        Validate SOP structure.
        
        Args:
            sop_data: SOP data to validate
            
        Returns:
            SOPValidationResult with validation results
        """
        ...
    
    async def enhance_sop_content(self, sop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance SOP content with additional information.
        
        Args:
            sop_data: SOP data to enhance
            
        Returns:
            Dict with enhanced SOP data
        """
        ...
    
    async def get_sop_metadata(self, sop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get SOP metadata information.
        
        Args:
            sop_data: SOP data to analyze
            
        Returns:
            Dict with SOP metadata
        """
        ...


