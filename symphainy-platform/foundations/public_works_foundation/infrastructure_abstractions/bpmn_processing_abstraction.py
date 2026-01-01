#!/usr/bin/env python3
"""
BPMN Processing Abstraction

Infrastructure abstraction for BPMN processing capabilities.
Implements BPMNProcessingProtocol using BPMNProcessingAdapter.

WHAT (Infrastructure Abstraction Role): I provide unified BPMN processing infrastructure
HOW (Infrastructure Abstraction Implementation): I coordinate BPMN processing adapters
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..abstraction_contracts.bpmn_processing_protocol import (
    BPMNProcessingProtocol, BPMNElement, BPMNProcess, BPMNProcessingResult
)
from ..infrastructure_adapters.bpmn_processing_adapter import BPMNProcessingAdapter

class BPMNProcessingAbstraction(BPMNProcessingProtocol):
    """BPMN processing abstraction using BPMN processing adapter."""
    
    def __init__(self, bpmn_processing_adapter: BPMNProcessingAdapter, di_container=None, **kwargs):
        """
        Initialize BPMN processing abstraction.
        
        Args:
            bpmn_processing_adapter: BPMN processing adapter instance
            di_container: Dependency injection container
        """
        self.bpmn_processing_adapter = bpmn_processing_adapter
        self.di_container = di_container
        self.service_name = "bpmn_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Initialize abstraction
        self._initialize_abstraction()
    
    def _initialize_abstraction(self):
        """Initialize the BPMN processing abstraction."""
        try:
            self.logger.info("✅ BPMN Processing Abstraction initialized")
            
        except Exception as e:
            # Sync method - just use logger (error_handler is async)
            self.logger.error(f"❌ Failed to initialize BPMN processing abstraction: {e}")
    
            raise  # Re-raise for service layer to handle
    
    async def parse_bpmn_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse BPMN XML content.
        
        Args:
            xml_content: BPMN XML content
            
        Returns:
            BPMNProcessingResult with parsed BPMN data
        """
        try:
            # Use adapter to parse BPMN XML
            result = await self.bpmn_processing_adapter.parse_bpmn_xml(xml_content)
            
            if result.get("success"):
                bpmn_result = BPMNProcessingResult(
                    success=True,
                    bpmn_data=result.get("workflow_data", {}),
                    bpmn_xml=xml_content,
                    error=None,
                    processed_at=datetime.utcnow()
                )
                
                return bpmn_result
            else:
                return BPMNProcessingResult(
                    success=False,
                    bpmn_data=None,
                    bpmn_xml=None,
                    error=result.get("error", "BPMN XML parsing failed"),
                    processed_at=datetime.utcnow()
                )
                
        except Exception as e:
            self.logger.error(f"❌ BPMN XML parsing failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Generate BPMN XML from workflow data.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            BPMNProcessingResult with generated BPMN XML
        """
        try:
            # Use adapter to generate BPMN XML
            result = await self.bpmn_processing_adapter.generate_bpmn_xml(workflow_data)
            
            if result.get("success"):
                bpmn_result = BPMNProcessingResult(
                    success=True,
                    bpmn_data=workflow_data,
                    bpmn_xml=result.get("bpmn_xml", ""),
                    error=None,
                    processed_at=datetime.utcnow()
                )
                
                return bpmn_result
            else:
                return BPMNProcessingResult(
                    success=False,
                    bpmn_data=None,
                    bpmn_xml=None,
                    error=result.get("error", "BPMN XML generation failed"),
                    processed_at=datetime.utcnow()
                )
                
        except Exception as e:
            self.logger.error(f"❌ BPMN XML generation failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def validate_bpmn_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Validate BPMN XML structure.
        
        Args:
            xml_content: BPMN XML content
            
        Returns:
            Dict with validation results
        """
        try:
            # Use adapter to validate BPMN structure
            result = await self.bpmn_processing_adapter.validate_bpmn_structure(xml_content)
            
            validation_result = {
                "success": True,
                "validation_result": result,
                "validated_at": datetime.utcnow().isoformat()
            }
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"❌ BPMN structure validation failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Extract workflow data from BPMN.
        
        Args:
            bpmn_data: BPMN data dictionary
            
        Returns:
            Dict with extracted workflow data
        """
        try:
            # Extract workflow elements from BPMN data
            workflow_data = {
                "name": "Extracted Workflow",
                "description": "Workflow extracted from BPMN",
                "nodes": [],
                "edges": [],
                "metadata": {
                    "source": "bpmn",
                    "extracted_at": datetime.utcnow().isoformat()
                }
            }
            
            # Extract processes
            processes = bpmn_data.get("processes", [])
            for process in processes:
                workflow_data["name"] = process.get("name", "Extracted Workflow")
            
            # Extract tasks as nodes
            tasks = bpmn_data.get("tasks", [])
            for task in tasks:
                node = {
                    "id": task.get("id", ""),
                    "name": task.get("name", ""),
                    "type": "task",
                    "properties": {
                        "bpmn_type": task.get("type", "task")
                    }
                }
                workflow_data["nodes"].append(node)
            
            # Extract gateways as nodes
            gateways = bpmn_data.get("gateways", [])
            for gateway in gateways:
                node = {
                    "id": gateway.get("id", ""),
                    "name": gateway.get("name", ""),
                    "type": "gateway",
                    "properties": {
                        "bpmn_type": gateway.get("type", "gateway")
                    }
                }
                workflow_data["nodes"].append(node)
            
            # Extract events as nodes
            events = bpmn_data.get("events", [])
            for event in events:
                node = {
                    "id": event.get("id", ""),
                    "name": event.get("name", ""),
                    "type": "event",
                    "properties": {
                        "bpmn_type": event.get("type", "event")
                    }
                }
                workflow_data["nodes"].append(node)
            
            # Extract flows as edges
            flows = bpmn_data.get("flows", [])
            for flow in flows:
                edge = {
                    "id": flow.get("id", ""),
                    "source": flow.get("sourceRef", ""),
                    "target": flow.get("targetRef", ""),
                    "label": flow.get("name", ""),
                    "type": "sequence_flow"
                }
                workflow_data["edges"].append(edge)
            
            extraction_result = {
                "success": True,
                "workflow_data": workflow_data,
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            return extraction_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract workflow data from BPMN: {e}")
            raise  # Re-raise for service layer to handle
    
    async def convert_workflow_to_bpmn(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert workflow data to BPMN format.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with BPMN formatted workflow data
        """
        try:
            # Convert workflow to BPMN format
            bpmn_data = {
                "processes": [],
                "tasks": [],
                "gateways": [],
                "events": [],
                "flows": []
            }
            
            # Create process
            process = {
                "id": "Process_1",
                "name": workflow_data.get("name", "Workflow Process"),
                "isExecutable": "true"
            }
            bpmn_data["processes"].append(process)
            
            # Convert nodes to BPMN elements
            nodes = workflow_data.get("nodes", [])
            for node in nodes:
                node_type = node.get("type", "task")
                if node_type == "task":
                    task = {
                        "id": node.get("id", ""),
                        "name": node.get("name", ""),
                        "type": "task"
                    }
                    bpmn_data["tasks"].append(task)
                elif node_type == "gateway":
                    gateway = {
                        "id": node.get("id", ""),
                        "name": node.get("name", ""),
                        "type": node.get("properties", {}).get("bpmn_type", "gateway")
                    }
                    bpmn_data["gateways"].append(gateway)
                elif node_type == "event":
                    event = {
                        "id": node.get("id", ""),
                        "name": node.get("name", ""),
                        "type": node.get("properties", {}).get("bpmn_type", "event")
                    }
                    bpmn_data["events"].append(event)
            
            # Convert edges to flows
            edges = workflow_data.get("edges", [])
            for edge in edges:
                flow = {
                    "id": edge.get("id", ""),
                    "sourceRef": edge.get("source", ""),
                    "targetRef": edge.get("target", ""),
                    "name": edge.get("label", "")
                }
                bpmn_data["flows"].append(flow)
            
            conversion_result = {
                "success": True,
                "bpmn_data": bpmn_data,
                "converted_at": datetime.utcnow().isoformat()
            }
            
            return conversion_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to convert workflow to BPMN: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_supported_element_types(self) -> List[str]:
        """
        Get list of supported BPMN element types.
        
        Returns:
            List of supported BPMN element types
        """
        try:
            element_types = [
                "process",
                "task",
                "gateway",
                "event",
                "sequenceFlow",
                "startEvent",
                "endEvent",
                "intermediateEvent",
                "exclusiveGateway",
                "parallelGateway",
                "inclusiveGateway"
            ]
            
            return element_types
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get BPMN element types: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Get adapter health
            adapter_health = await self.bpmn_processing_adapter.health_check()
            
            health_status = {
                "healthy": adapter_health.get("healthy", False),
                "adapter": adapter_health,
                "abstraction": {
                    "name": "BPMNProcessingAbstraction",
                    "status": "active"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
