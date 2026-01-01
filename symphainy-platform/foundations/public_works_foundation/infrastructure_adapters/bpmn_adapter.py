#!/usr/bin/env python3
"""
BPMN Infrastructure Adapter

Raw BPMN processing bindings for workflow visualization and modeling.
Thin wrapper around BPMN SDK with no business logic.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import logging
import uuid

try:
    from lxml import etree
    from lxml.etree import ElementTree
except ImportError:
    etree = None
    ElementTree = None


class BPMNAdapter:
    """Raw BPMN adapter for workflow visualization and modeling."""
    
    def __init__(self, **kwargs):
        """
        Initialize BPMN adapter.
        
        Args:
            **kwargs: Additional configuration
        """
        self.logger = logging.getLogger("BPMNAdapter")
        
        # BPMN namespace
        self.bpmn_namespace = "http://www.omg.org/spec/BPMN/20100524/MODEL"
        self.bpmn_di_namespace = "http://www.omg.org/spec/BPMN/20100524/DI"
        self.dc_namespace = "http://www.omg.org/spec/DD/20100524/DC"
        
        # Initialize BPMN parser
        self._initialize_bpmn_parser()
    
    def _initialize_bpmn_parser(self):
        """Initialize BPMN parser."""
        if etree is None:
            self.logger.error("lxml not installed")
            return
            
        try:
            self.logger.info("✅ BPMN adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BPMN parser: {e}")
    
    def parse_bpmn_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse BPMN file.
        
        Args:
            file_path: Path to BPMN file
            
        Returns:
            Dict: Parsed BPMN data
        """
        if etree is None:
            return {"error": "lxml not installed"}
            
        try:
            # Parse BPMN file
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Extract BPMN elements
            processes = self._extract_processes(root)
            tasks = self._extract_tasks(root)
            gateways = self._extract_gateways(root)
            events = self._extract_events(root)
            flows = self._extract_flows(root)
            
            return {
                "file_path": file_path,
                "processes": processes,
                "tasks": tasks,
                "gateways": gateways,
                "events": events,
                "flows": flows,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse BPMN file {file_path}: {e}")
            return {"error": str(e)}
    
    def _extract_processes(self, root) -> List[Dict[str, Any]]:
        """Extract process definitions from BPMN."""
        processes = []
        
        try:
            for process in root.xpath("//bpmn:process", namespaces={"bpmn": self.bpmn_namespace}):
                processes.append({
                    "id": process.get("id"),
                    "name": process.get("name"),
                    "isExecutable": process.get("isExecutable", "false") == "true"
                })
        except Exception as e:
            self.logger.error(f"Failed to extract processes: {e}")
        
        return processes
    
    def _extract_tasks(self, root) -> List[Dict[str, Any]]:
        """Extract tasks from BPMN."""
        tasks = []
        
        try:
            for task in root.xpath("//bpmn:task", namespaces={"bpmn": self.bpmn_namespace}):
                tasks.append({
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "type": "task"
                })
        except Exception as e:
            self.logger.error(f"Failed to extract tasks: {e}")
        
        return tasks
    
    def _extract_gateways(self, root) -> List[Dict[str, Any]]:
        """Extract gateways from BPMN."""
        gateways = []
        
        try:
            # Exclusive gateways
            for gateway in root.xpath("//bpmn:exclusiveGateway", namespaces={"bpmn": self.bpmn_namespace}):
                gateways.append({
                    "id": gateway.get("id"),
                    "name": gateway.get("name"),
                    "type": "exclusiveGateway"
                })
            
            # Parallel gateways
            for gateway in root.xpath("//bpmn:parallelGateway", namespaces={"bpmn": self.bpmn_namespace}):
                gateways.append({
                    "id": gateway.get("id"),
                    "name": gateway.get("name"),
                    "type": "parallelGateway"
                })
            
            # Inclusive gateways
            for gateway in root.xpath("//bpmn:inclusiveGateway", namespaces={"bpmn": self.bpmn_namespace}):
                gateways.append({
                    "id": gateway.get("id"),
                    "name": gateway.get("name"),
                    "type": "inclusiveGateway"
                })
                
        except Exception as e:
            self.logger.error(f"Failed to extract gateways: {e}")
        
        return gateways
    
    def _extract_events(self, root) -> List[Dict[str, Any]]:
        """Extract events from BPMN."""
        events = []
        
        try:
            # Start events
            for event in root.xpath("//bpmn:startEvent", namespaces={"bpmn": self.bpmn_namespace}):
                events.append({
                    "id": event.get("id"),
                    "name": event.get("name"),
                    "type": "startEvent"
                })
            
            # End events
            for event in root.xpath("//bpmn:endEvent", namespaces={"bpmn": self.bpmn_namespace}):
                events.append({
                    "id": event.get("id"),
                    "name": event.get("name"),
                    "type": "endEvent"
                })
            
            # Intermediate events
            for event in root.xpath("//bpmn:intermediateCatchEvent", namespaces={"bpmn": self.bpmn_namespace}):
                events.append({
                    "id": event.get("id"),
                    "name": event.get("name"),
                    "type": "intermediateCatchEvent"
                })
                
        except Exception as e:
            self.logger.error(f"Failed to extract events: {e}")
        
        return events
    
    def _extract_flows(self, root) -> List[Dict[str, Any]]:
        """Extract sequence flows from BPMN."""
        flows = []
        
        try:
            for flow in root.xpath("//bpmn:sequenceFlow", namespaces={"bpmn": self.bpmn_namespace}):
                flows.append({
                    "id": flow.get("id"),
                    "name": flow.get("name"),
                    "sourceRef": flow.get("sourceRef"),
                    "targetRef": flow.get("targetRef")
                })
        except Exception as e:
            self.logger.error(f"Failed to extract flows: {e}")
        
        return flows
    
    def create_bpmn_diagram(self, workflow_data: Dict[str, Any]) -> str:
        """
        Create BPMN diagram from workflow data.
        
        Args:
            workflow_data: Workflow definition
            
        Returns:
            str: BPMN XML string
        """
        if etree is None:
            return ""
            
        try:
            # Create BPMN root element
            root = etree.Element("definitions")
            root.set("xmlns", "http://www.omg.org/spec/BPMN/20100524/MODEL")
            root.set("xmlns:bpmndi", "http://www.omg.org/spec/BPMN/20100524/DI")
            root.set("xmlns:dc", "http://www.omg.org/spec/DD/20100524/DC")
            
            # Create process
            process = etree.SubElement(root, "process", 
                                     id=workflow_data.get("id", "workflow"),
                                     name=workflow_data.get("name", "Workflow"))
            
            # Add tasks
            for task in workflow_data.get("tasks", []):
                task_elem = etree.SubElement(process, "task",
                                           id=task.get("id"),
                                           name=task.get("name"))
            
            # Add flows
            for flow in workflow_data.get("flows", []):
                flow_elem = etree.SubElement(process, "sequenceFlow",
                                           id=flow.get("id"),
                                           sourceRef=flow.get("source"),
                                           targetRef=flow.get("target"))
            
            # Convert to string
            bpmn_xml = etree.tostring(root, pretty_print=True, encoding='unicode')
            
            self.logger.info("✅ BPMN diagram created")
            return bpmn_xml
            
        except Exception as e:
            self.logger.error(f"Failed to create BPMN diagram: {e}")
            return ""
    
    def validate_bpmn(self, bpmn_xml: str) -> Dict[str, Any]:
        """
        Validate BPMN XML.
        
        Args:
            bpmn_xml: BPMN XML string
            
        Returns:
            Dict: Validation result
        """
        if etree is None:
            return {"error": "lxml not installed", "valid": False}
            
        try:
            # Parse XML
            root = etree.fromstring(bpmn_xml.encode('utf-8'))
            
            # Basic validation
            processes = root.xpath("//bpmn:process", namespaces={"bpmn": self.bpmn_namespace})
            tasks = root.xpath("//bpmn:task", namespaces={"bpmn": self.bpmn_namespace})
            flows = root.xpath("//bpmn:sequenceFlow", namespaces={"bpmn": self.bpmn_namespace})
            
            return {
                "valid": True,
                "processes": len(processes),
                "tasks": len(tasks),
                "flows": len(flows),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate BPMN: {e}")
            return {"error": str(e), "valid": False}
    
    def convert_to_workflow_graph(self, bpmn_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert BPMN data to workflow graph format.
        
        Args:
            bpmn_data: Parsed BPMN data
            
        Returns:
            Dict: Workflow graph
        """
        try:
            # Create workflow graph structure
            workflow_graph = {
                "nodes": [],
                "edges": [],
                "metadata": {
                    "source": "bpmn",
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Convert tasks to nodes
            for task in bpmn_data.get("tasks", []):
                workflow_graph["nodes"].append({
                    "id": task["id"],
                    "label": task["name"],
                    "type": "task",
                    "data": task
                })
            
            # Convert gateways to nodes
            for gateway in bpmn_data.get("gateways", []):
                workflow_graph["nodes"].append({
                    "id": gateway["id"],
                    "label": gateway["name"],
                    "type": gateway["type"],
                    "data": gateway
                })
            
            # Convert events to nodes
            for event in bpmn_data.get("events", []):
                workflow_graph["nodes"].append({
                    "id": event["id"],
                    "label": event["name"],
                    "type": event["type"],
                    "data": event
                })
            
            # Convert flows to edges
            for flow in bpmn_data.get("flows", []):
                workflow_graph["edges"].append({
                    "id": flow["id"],
                    "source": flow["sourceRef"],
                    "target": flow["targetRef"],
                    "data": flow
                })
            
            return workflow_graph
            
        except Exception as e:
            self.logger.error(f"Failed to convert BPMN to workflow graph: {e}")
            return {"error": str(e)}
    
    def export_to_json(self, bpmn_data: Dict[str, Any], file_path: str) -> bool:
        """
        Export BPMN data to JSON file.
        
        Args:
            bpmn_data: BPMN data
            file_path: Output file path
            
        Returns:
            bool: Success status
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(bpmn_data, f, indent=2)
            
            self.logger.info(f"✅ BPMN data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export BPMN data: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> Dict[str, Any]:
        """
        Import BPMN data from JSON file.
        
        Args:
            file_path: Input file path
            
        Returns:
            Dict: BPMN data
        """
        try:
            with open(file_path, 'r') as f:
                bpmn_data = json.load(f)
            
            self.logger.info(f"✅ BPMN data imported from {file_path}")
            return bpmn_data
            
        except Exception as e:
            self.logger.error(f"Failed to import BPMN data: {e}")
            return {"error": str(e)}
