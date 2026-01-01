#!/usr/bin/env python3
"""
BPMN Processing Protocol

Defines the interface contract for BPMN processing capabilities.
Used by infrastructure abstractions to ensure consistent BPMN processing.

WHAT (Protocol Role): I define the interface contract for BPMN processing
HOW (Protocol Implementation): I specify the required methods and data structures
"""

from typing import Protocol
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class BPMNElement:
    """BPMN element data class."""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]


@dataclass
class BPMNProcess:
    """BPMN process data class."""
    id: str
    name: str
    is_executable: bool
    elements: List[BPMNElement]
    flows: List[Dict[str, Any]]


@dataclass
class BPMNProcessingResult:
    """BPMN processing result data class."""
    success: bool
    bpmn_data: Optional[Dict[str, Any]]
    bpmn_xml: Optional[str]
    error: Optional[str]
    processed_at: datetime


class BPMNProcessingProtocol(Protocol):
    """
    Protocol for BPMN processing capabilities.
    
    Defines the interface contract that all BPMN processing implementations
    must follow to ensure consistent BPMN processing across the platform.
    """
    
    async def parse_bpmn_xml(self, xml_content: str) -> BPMNProcessingResult:
        """
        Parse BPMN XML content.
        
        Args:
            xml_content: BPMN XML content
            
        Returns:
            BPMNProcessingResult with parsed BPMN data
        """
        ...
    
    async def generate_bpmn_xml(self, workflow_data: Dict[str, Any]) -> BPMNProcessingResult:
        """
        Generate BPMN XML from workflow data.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            BPMNProcessingResult with generated BPMN XML
        """
        ...
    
    async def validate_bpmn_structure(self, xml_content: str) -> Dict[str, Any]:
        """
        Validate BPMN XML structure.
        
        Args:
            xml_content: BPMN XML content
            
        Returns:
            Dict with validation results
        """
        ...
    
    async def extract_workflow_from_bpmn(self, bpmn_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract workflow data from BPMN.
        
        Args:
            bpmn_data: BPMN data dictionary
            
        Returns:
            Dict with extracted workflow data
        """
        ...
    
    async def convert_workflow_to_bpmn(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert workflow data to BPMN format.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with BPMN formatted workflow data
        """
        ...
    
    async def get_bpmn_element_types(self) -> List[str]:
        """
        Get list of supported BPMN element types.
        
        Returns:
            List of supported BPMN element types
        """
        ...


