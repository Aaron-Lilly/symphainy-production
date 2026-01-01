#!/usr/bin/env python3
"""
BPMN Processing Adapter

Lightweight infrastructure adapter for BPMN processing capabilities.
Wraps specific BPMN processing libraries and provides consistent interface.

WHAT (Infrastructure Adapter Role): I provide lightweight BPMN processing infrastructure
HOW (Infrastructure Adapter Implementation): I wrap specific BPMN processing libraries
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime


class BPMNProcessingAdapter:
    """
    Lightweight infrastructure adapter for BPMN processing.
    
    Wraps specific BPMN processing libraries and provides consistent interface
    for BPMN XML parsing, workflow extraction, and BPMN generation.
    """
    
    def __init__(self, **kwargs):
        """Initialize BPMN processing adapter."""
        self.logger = logging.getLogger("BPMNProcessingAdapter")
        self.logger.info("✅ BPMN Processing Adapter initialized")
    
    async def parse_bpmn_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse BPMN XML content.
        
        Args:
            xml_content: BPMN XML content
            
        Returns:
            Dict with parsed BPMN data
        """
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Extract workflow elements
            workflow_data = {
                "processes": [],
                "tasks": [],
                "gateways": [],
                "events": [],
                "flows": []
            }
            
            # Extract processes
            for process in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}process'):
                process_data = {
                    "id": process.get("id", ""),
                    "name": process.get("name", ""),
                    "isExecutable": process.get("isExecutable", "false")
                }
                workflow_data["processes"].append(process_data)
            
            # Extract tasks
            for task in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}task'):
                task_data = {
                    "id": task.get("id", ""),
                    "name": task.get("name", ""),
                    "type": "task"
                }
                workflow_data["tasks"].append(task_data)
            
            # Extract gateways
            for gateway in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}gateway'):
                gateway_data = {
                    "id": gateway.get("id", ""),
                    "name": gateway.get("name", ""),
                    "type": gateway.tag.split("}")[-1] if "}" in gateway.tag else gateway.tag
                }
                workflow_data["gateways"].append(gateway_data)
            
            # Extract events
            for event in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}event'):
                event_data = {
                    "id": event.get("id", ""),
                    "name": event.get("name", ""),
                    "type": event.tag.split("}")[-1] if "}" in event.tag else event.tag
                }
                workflow_data["events"].append(event_data)
            
            # Extract flows
            for flow in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow'):
                flow_data = {
                    "id": flow.get("id", ""),
                    "sourceRef": flow.get("sourceRef", ""),
                    "targetRef": flow.get("targetRef", ""),
                    "name": flow.get("name", "")
                }
                workflow_data["flows"].append(flow_data)
            
            return {
                "success": True,
                "workflow_data": workflow_data,
                "parsed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"BPMN XML parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "parsed_at": datetime.utcnow().isoformat()
            }
    
    async def generate_bpmn_xml(self, workflow_data: Dict[str, Any]) -> str:
        """
        Generate BPMN XML from workflow data.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            BPMN XML string
        """
        try:
            # Create BPMN XML structure
            bpmn_xml = self._create_bpmn_xml_structure(workflow_data)
            
            return {
                "success": True,
                "bpmn_xml": bpmn_xml,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"BPMN XML generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def validate_bpmn_structure(self, xml_content: str) -> Dict[str, Any]:
        """
        Validate BPMN XML structure.
        
        Args:
            xml_content: BPMN XML content
            
        Returns:
            Dict with validation results
        """
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Parse XML to check structure
            root = ET.fromstring(xml_content)
            
            # Check for required elements
            processes = root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}process')
            if not processes:
                validation_result["errors"].append("No processes found in BPMN")
                validation_result["valid"] = False
            
            # Check for tasks
            tasks = root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}task')
            if not tasks:
                validation_result["warnings"].append("No tasks found in BPMN")
            
            # Check for flows
            flows = root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow')
            if not flows:
                validation_result["warnings"].append("No sequence flows found in BPMN")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"BPMN validation failed: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def _create_bpmn_xml_structure(self, workflow_data: Dict[str, Any]) -> str:
        """Create BPMN XML structure from workflow data."""
        try:
            # Basic BPMN XML template
            bpmn_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
             xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
             id="Definitions_1"
             targetNamespace="http://bpmn.io/schema/bpmn">
    
    <process id="Process_1" isExecutable="true">
        <!-- Tasks will be added here -->
        <!-- Flows will be added here -->
    </process>
    
</definitions>'''
            
            return bpmn_xml
            
        except Exception as e:
            self.logger.error(f"BPMN XML structure creation failed: {e}")
            return ""
    
    async def health_check(self) -> Dict[str, Any]:
        """Check adapter health."""
        try:
            return {
                "healthy": True,
                "adapter": "BPMNProcessingAdapter",
                "capabilities": [
                    "parse_bpmn_xml",
                    "generate_bpmn_xml",
                    "validate_bpmn_structure"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


