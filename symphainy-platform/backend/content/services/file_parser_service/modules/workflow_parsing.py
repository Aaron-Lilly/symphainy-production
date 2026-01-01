#!/usr/bin/env python3
"""
Workflow Parsing Module - File Parser Service

Handles workflow document parsing (BPMN, JSON, Draw.io).
Extracts nodes, edges, gateways, and workflow structure.
"""

import asyncio
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from datetime import datetime


class WorkflowParsing:
    """Handles workflow document parsing."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def parse(
        self,
        file_data: bytes,
        file_type: str,
        filename: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse workflow file into structured format.
        
        Supports:
        - BPMN (.bpmn) - XML-based workflow format
        - JSON workflow format (.json) - React Flow, custom JSON
        - Draw.io (.drawio) - XML-based diagram format
        
        Args:
            file_data: File data as bytes
            file_type: File extension (e.g., "bpmn", "json", "drawio")
            filename: Original filename
            parse_options: Optional parsing options
            user_context: Optional user context
        
        Returns:
            Parsed result dictionary with structured workflow data
        """
        try:
            # Start telemetry tracking
            await self.service.log_operation_with_telemetry("workflow_parse_start", success=True, metadata={
                "file_type": file_type,
                "filename": filename
            })
            
            file_type_lower = file_type.lower() if file_type else ""
            
            # Route to appropriate parser
            if file_type_lower == "bpmn":
                parsed_result = await self._parse_bpmn(file_data, filename)
            elif file_type_lower == "json":
                parsed_result = await self._parse_json_workflow(file_data, filename)
            elif file_type_lower == "drawio":
                parsed_result = await self._parse_drawio(file_data, filename)
            else:
                error_msg = f"Unsupported workflow file type: {file_type}"
                self.service.logger.warning(f"⚠️ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "workflow_parse")
                await self.service.record_health_metric("workflow_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "unsupported_file_type"
                })
                await self.service.log_operation_with_telemetry("workflow_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "unsupported_file_type",
                    "parsing_type": "workflow"
                }
            
            # Record health metric (success)
            await self.service.record_health_metric("workflow_files_parsed", 1.0, {
                "file_type": file_type,
                "node_count": len(parsed_result.get("structure", {}).get("nodes", [])),
                "edge_count": len(parsed_result.get("structure", {}).get("edges", [])),
                "success": True
            })
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "workflow_parse_complete",
                success=True,
                details={
                    "file_type": file_type,
                    "node_count": len(parsed_result.get("structure", {}).get("nodes", [])),
                    "edge_count": len(parsed_result.get("structure", {}).get("edges", []))
                }
            )
            
            self.service.logger.info(f"✅ Workflow file parsed successfully: {file_type} (nodes: {len(parsed_result.get('structure', {}).get('nodes', []))}, edges: {len(parsed_result.get('structure', {}).get('edges', []))})")
            
            return parsed_result
            
        except Exception as e:
            # Use enhanced error handling with audit
            self.service.logger.error(f"❌ Workflow parsing failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.service.handle_error_with_audit(e, "workflow_parse")
            await self.service.record_health_metric("workflow_files_parsed", 0.0, {
                "file_type": file_type,
                "success": False,
                "error": str(e)
            })
            await self.service.log_operation_with_telemetry("workflow_parse_complete", success=False, details={
                "file_type": file_type,
                "error": str(e)
            })
            return {
                "success": False,
                "message": f"Workflow parsing exception: {e}",
                "file_type": file_type,
                "error": str(e),
                "parsing_type": "workflow"
            }
    
    async def _parse_bpmn(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse BPMN XML file.
        
        Extracts:
        - Processes
        - Tasks
        - Gateways (exclusive, parallel, inclusive)
        - Events (start, end, intermediate)
        - Sequence flows (edges)
        
        Args:
            file_data: BPMN XML file data as bytes
            filename: Original filename
        
        Returns:
            Parsed result dictionary with workflow structure
        """
        try:
            # Try to use BPMN Processing Abstraction via Platform Gateway
            try:
                bpmn_abstraction = self.service.platform_gateway.get_abstraction(
                    realm_name=self.service.realm_name,
                    abstraction_name="BPMNProcessingAbstraction"
                )
                
                if bpmn_abstraction:
                    # Use abstraction if available
                    from foundations.public_works_foundation.abstraction_contracts.bpmn_processing_protocol import BPMNProcessingRequest
                    
                    xml_content = file_data.decode("utf-8")
                    request = BPMNProcessingRequest(
                        xml_content=xml_content,
                        options={}
                    )
                    
                    result = await bpmn_abstraction.parse_bpmn_xml(request)
                    
                    if result.success:
                        # Convert abstraction result to workflow structure
                        nodes = []
                        edges = []
                        
                        # Add tasks as nodes
                        for task in result.tasks or []:
                            nodes.append({
                                "id": task.get("id", ""),
                                "type": "task",
                                "label": task.get("name", ""),
                                "data": task
                            })
                        
                        # Add gateways as nodes
                        for gateway in result.gateways or []:
                            nodes.append({
                                "id": gateway.get("id", ""),
                                "type": "gateway",
                                "label": gateway.get("name", ""),
                                "data": gateway
                            })
                        
                        # Add events as nodes
                        for event in result.events or []:
                            nodes.append({
                                "id": event.get("id", ""),
                                "type": "event",
                                "label": event.get("name", ""),
                                "data": event
                            })
                        
                        # Add flows as edges
                        for flow in result.flows or []:
                            edges.append({
                                "id": flow.get("id", ""),
                                "source": flow.get("sourceRef", ""),
                                "target": flow.get("targetRef", ""),
                                "label": flow.get("name", ""),
                                "data": flow
                            })
                        
                        return {
                            "success": True,
                            "parsing_type": "workflow",
                            "file_type": "bpmn",
                            "structure": {
                                "nodes": nodes,
                                "edges": edges,
                                "processes": result.processes or [],
                                "metadata": {
                                    "process_count": len(result.processes or []),
                                    "task_count": len(result.tasks or []),
                                    "gateway_count": len(result.gateways or []),
                                    "event_count": len(result.events or []),
                                    "flow_count": len(result.flows or [])
                                }
                            },
                            "parsed_at": result.processed_at.isoformat() if hasattr(result.processed_at, 'isoformat') else datetime.utcnow().isoformat()
                        }
            except Exception as e:
                self.service.logger.warning(f"⚠️ BPMN abstraction not available, using fallback parser: {e}")
            
            # Fallback: Parse BPMN XML directly
            xml_content = file_data.decode("utf-8")
            root = ET.fromstring(xml_content)
            
            # BPMN namespaces
            bpmn_ns = "http://www.omg.org/spec/BPMN/20100524/MODEL"
            ns = {"bpmn": bpmn_ns}
            
            nodes = []
            edges = []
            
            # Extract tasks
            for task in root.findall(".//bpmn:task", ns):
                nodes.append({
                    "id": task.get("id", ""),
                    "type": "task",
                    "label": task.get("name", ""),
                    "data": {
                        "id": task.get("id", ""),
                        "name": task.get("name", "")
                    }
                })
            
            # Extract gateways
            for gateway in root.findall(".//bpmn:exclusiveGateway", ns) + root.findall(".//bpmn:parallelGateway", ns) + root.findall(".//bpmn:inclusiveGateway", ns):
                gateway_type = gateway.tag.split("}")[-1] if "}" in gateway.tag else gateway.tag
                nodes.append({
                    "id": gateway.get("id", ""),
                    "type": "gateway",
                    "label": gateway.get("name", ""),
                    "data": {
                        "id": gateway.get("id", ""),
                        "name": gateway.get("name", ""),
                        "type": gateway_type
                    }
                })
            
            # Extract events
            for event in root.findall(".//bpmn:startEvent", ns) + root.findall(".//bpmn:endEvent", ns) + root.findall(".//bpmn:intermediateCatchEvent", ns):
                event_type = event.tag.split("}")[-1] if "}" in event.tag else event.tag
                nodes.append({
                    "id": event.get("id", ""),
                    "type": "event",
                    "label": event.get("name", ""),
                    "data": {
                        "id": event.get("id", ""),
                        "name": event.get("name", ""),
                        "type": event_type
                    }
                })
            
            # Extract sequence flows (edges)
            for flow in root.findall(".//bpmn:sequenceFlow", ns):
                edges.append({
                    "id": flow.get("id", ""),
                    "source": flow.get("sourceRef", ""),
                    "target": flow.get("targetRef", ""),
                    "label": flow.get("name", ""),
                    "data": {
                        "id": flow.get("id", ""),
                        "name": flow.get("name", ""),
                        "sourceRef": flow.get("sourceRef", ""),
                        "targetRef": flow.get("targetRef", "")
                    }
                })
            
            return {
                "success": True,
                "parsing_type": "workflow",
                "file_type": "bpmn",
                "structure": {
                    "nodes": nodes,
                    "edges": edges,
                    "metadata": {
                        "node_count": len(nodes),
                        "edge_count": len(edges)
                    }
                },
                "parsed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.service.logger.error(f"❌ BPMN parsing failed: {e}")
            return {
                "success": False,
                "error": f"BPMN parsing failed: {str(e)}",
                "parsing_type": "workflow",
                "file_type": "bpmn"
            }
    
    async def _parse_json_workflow(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse JSON workflow format.
        
        Supports:
        - React Flow format: {nodes: [...], edges: [...]}
        - Custom JSON workflow format
        
        Args:
            file_data: JSON file data as bytes
            filename: Original filename
        
        Returns:
            Parsed result dictionary with workflow structure
        """
        try:
            workflow_data = json.loads(file_data.decode("utf-8"))
            
            # Handle React Flow format
            if "nodes" in workflow_data and "edges" in workflow_data:
                nodes = workflow_data.get("nodes", [])
                edges = workflow_data.get("edges", [])
                
                # Normalize nodes to consistent format
                normalized_nodes = []
                for node in nodes:
                    normalized_nodes.append({
                        "id": node.get("id", ""),
                        "type": node.get("type", "default"),
                        "label": node.get("data", {}).get("label", "") if isinstance(node.get("data"), dict) else node.get("label", ""),
                        "data": node
                    })
                
                # Normalize edges to consistent format
                normalized_edges = []
                for edge in edges:
                    normalized_edges.append({
                        "id": edge.get("id", ""),
                        "source": edge.get("source", ""),
                        "target": edge.get("target", ""),
                        "label": edge.get("label", "") or edge.get("data", {}).get("label", "") if isinstance(edge.get("data"), dict) else "",
                        "data": edge
                    })
                
                return {
                    "success": True,
                    "parsing_type": "workflow",
                    "file_type": "json",
                    "structure": {
                        "nodes": normalized_nodes,
                        "edges": normalized_edges,
                        "metadata": workflow_data.get("metadata", {}),
                        "workflow_metadata": {
                            "node_count": len(normalized_nodes),
                            "edge_count": len(normalized_edges)
                        }
                    },
                    "parsed_at": datetime.utcnow().isoformat()
                }
            
            # Handle custom format - try to extract nodes and edges
            else:
                # Look for common patterns
                nodes = workflow_data.get("workflow", {}).get("nodes", []) or workflow_data.get("tasks", []) or []
                edges = workflow_data.get("workflow", {}).get("edges", []) or workflow_data.get("connections", []) or []
                
                return {
                    "success": True,
                    "parsing_type": "workflow",
                    "file_type": "json",
                    "structure": {
                        "nodes": nodes,
                        "edges": edges,
                        "metadata": workflow_data.get("metadata", {}),
                        "workflow_metadata": {
                            "node_count": len(nodes),
                            "edge_count": len(edges)
                        }
                    },
                    "parsed_at": datetime.utcnow().isoformat()
                }
            
        except json.JSONDecodeError as e:
            self.service.logger.error(f"❌ JSON workflow parsing failed: Invalid JSON: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON format: {str(e)}",
                "parsing_type": "workflow",
                "file_type": "json"
            }
        except Exception as e:
            self.service.logger.error(f"❌ JSON workflow parsing failed: {e}")
            return {
                "success": False,
                "error": f"JSON workflow parsing failed: {str(e)}",
                "parsing_type": "workflow",
                "file_type": "json"
            }
    
    async def _parse_drawio(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse Draw.io XML file.
        
        Draw.io files are XML-based diagrams that can represent workflows.
        Extracts shapes (nodes) and connections (edges).
        
        Args:
            file_data: Draw.io XML file data as bytes
            filename: Original filename
        
        Returns:
            Parsed result dictionary with workflow structure
        """
        try:
            xml_content = file_data.decode("utf-8")
            root = ET.fromstring(xml_content)
            
            nodes = []
            edges = []
            
            # Draw.io stores diagram data in mxfile > diagram > mxGraphModel > root
            # Find mxGraphModel
            mx_graph_model = root.find(".//mxGraphModel")
            if mx_graph_model is None:
                return {
                    "success": False,
                    "error": "Invalid Draw.io format: mxGraphModel not found",
                    "parsing_type": "workflow",
                    "file_type": "drawio"
                }
            
            root_elem = mx_graph_model.find("root")
            if root_elem is None:
                return {
                    "success": False,
                    "error": "Invalid Draw.io format: root element not found",
                    "parsing_type": "workflow",
                    "file_type": "drawio"
                }
            
            # Extract mxCells (shapes and connections)
            for mx_cell in root_elem.findall("mxCell"):
                cell_id = mx_cell.get("id", "")
                cell_value = mx_cell.get("value", "")
                cell_style = mx_cell.get("style", "")
                parent = mx_cell.get("parent", "")
                source = mx_cell.get("source", "")
                target = mx_cell.get("target", "")
                
                # If it has source and target, it's an edge
                if source and target:
                    edges.append({
                        "id": cell_id,
                        "source": source,
                        "target": target,
                        "label": cell_value,
                        "data": {
                            "id": cell_id,
                            "value": cell_value,
                            "style": cell_style
                        }
                    })
                # Otherwise, it's a node (shape)
                elif parent == "1":  # Top-level shapes (not in groups)
                    node_type = "default"
                    # Try to determine type from style
                    if "shape=" in cell_style:
                        if "process" in cell_style.lower():
                            node_type = "task"
                        elif "decision" in cell_style.lower() or "rhombus" in cell_style.lower():
                            node_type = "gateway"
                        elif "start" in cell_style.lower() or "end" in cell_style.lower():
                            node_type = "event"
                    
                    nodes.append({
                        "id": cell_id,
                        "type": node_type,
                        "label": cell_value,
                        "data": {
                            "id": cell_id,
                            "value": cell_value,
                            "style": cell_style
                        }
                    })
            
            return {
                "success": True,
                "parsing_type": "workflow",
                "file_type": "drawio",
                "structure": {
                    "nodes": nodes,
                    "edges": edges,
                    "metadata": {
                        "node_count": len(nodes),
                        "edge_count": len(edges)
                    }
                },
                "parsed_at": datetime.utcnow().isoformat()
            }
            
        except ET.ParseError as e:
            self.service.logger.error(f"❌ Draw.io XML parsing failed: Invalid XML: {e}")
            return {
                "success": False,
                "error": f"Invalid XML format: {str(e)}",
                "parsing_type": "workflow",
                "file_type": "drawio"
            }
        except Exception as e:
            self.service.logger.error(f"❌ Draw.io parsing failed: {e}")
            return {
                "success": False,
                "error": f"Draw.io parsing failed: {str(e)}",
                "parsing_type": "workflow",
                "file_type": "drawio"
            }
