#!/usr/bin/env python3
"""
Workflow Visualization Workflow

WHAT: Prepares workflow structures for visualization/display
HOW: Formats parsed workflow data for frontend diagram rendering

This workflow implements the workflow visualization flow:
1. Retrieve workflow structure (from file_id via data mash or provided content)
2. Format nodes/edges for diagram libraries (React Flow, BPMN.js, etc.)
3. Return visualization-ready data

Key Principle: This is for DISPLAY/VISUALIZATION, not conversion.
Separate from SOPToWorkflowWorkflow which converts SOP → Workflow.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class WorkflowVisualizationWorkflow:
    """
    Workflow for preparing workflow structures for visualization.
    
    Takes parsed workflow structure and formats it for frontend diagram rendering.
    Supports multiple diagram formats: React Flow, BPMN.js, Draw.io, etc.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow with orchestrator context.
        
        Args:
            orchestrator: OperationsJourneyOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = logger
    
    async def execute(
        self,
        workflow_file_id: Optional[str] = None,
        workflow_content: Optional[Dict[str, Any]] = None,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow visualization workflow.
        
        Args:
            workflow_file_id: Optional workflow file identifier (will fetch from data mash)
            workflow_content: Optional workflow content (structure from parsing)
            visualization_options: Optional visualization options
                - diagram_type: "react_flow" (default), "bpmn", "drawio"
                - layout: "hierarchical" (default), "force", "dagre"
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with visualization_data (nodes, edges, metadata), diagram_type, etc.
        """
        try:
            self.logger.info("📊 Starting workflow visualization workflow")
            
            # Generate visualization ID
            visualization_id = f"viz_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            
            # Default options
            options = visualization_options or {}
            diagram_type = options.get("diagram_type", "react_flow")  # react_flow, bpmn, drawio
            layout = options.get("layout", "hierarchical")  # hierarchical, force, dagre
            
            # Step 1: Get workflow content (from file_id or provided)
            if workflow_file_id and not workflow_content:
                # Fetch from data mash via Data Solution Orchestrator
                self.logger.info(f"📊 Fetching workflow content from data mash: {workflow_file_id}")
                
                # Get Data Solution Orchestrator
                curator = await self.orchestrator.get_foundation_service("CuratorFoundationService")
                if curator:
                    data_orchestrator = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                    if data_orchestrator:
                        workflow_data = await data_orchestrator.orchestrate_data_mash(
                            client_data_query={"type": "file_id:" + workflow_file_id},
                            user_context=user_context
                        )
                        if workflow_data.get("success") and workflow_data.get("client_data", {}).get("file"):
                            file_data = workflow_data["client_data"]["file"]
                            parsed_files = workflow_data["client_data"].get("parsed_files", [])
                            if parsed_files:
                                parse_result = parsed_files[0].get("metadata", {}).get("parse_result", {})
                                if parse_result.get("parsing_type") == "workflow":
                                    workflow_content = parse_result.get("structure", {})
                                    self.logger.info(f"✅ Extracted workflow structure: {len(workflow_content.get('nodes', []))} nodes")
                                else:
                                    return {
                                        "success": False,
                                        "error": f"File {workflow_file_id} is not a parsed workflow file",
                                        "visualization_id": visualization_id,
                                        "workflow_id": workflow_id
                                    }
            
            if not workflow_content:
                return {
                    "success": False,
                    "error": "Workflow content not provided and could not be fetched from data mash",
                    "visualization_id": visualization_id,
                    "workflow_id": workflow_id
                }
            
            # Step 2: Format workflow structure for visualization
            visualization_data = await self._format_for_visualization(
                workflow_content=workflow_content,
                diagram_type=diagram_type,
                layout=layout
            )
            
            # Step 3: Build result
            result = {
                "success": True,
                "visualization_id": visualization_id,
                "workflow_id": workflow_id,
                "diagram_type": diagram_type,
                "layout": layout,
                "visualization_data": visualization_data,
                "metadata": {
                    "node_count": len(visualization_data.get("nodes", [])),
                    "edge_count": len(visualization_data.get("edges", [])),
                    "workflow_file_id": workflow_file_id
                }
            }
            
            self.logger.info(f"✅ Workflow visualization complete: {visualization_id} ({len(visualization_data.get('nodes', []))} nodes, {len(visualization_data.get('edges', []))} edges)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Workflow visualization workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def _format_for_visualization(
        self,
        workflow_content: Dict[str, Any],
        diagram_type: str,
        layout: str
    ) -> Dict[str, Any]:
        """
        Format workflow structure for visualization.
        
        Args:
            workflow_content: Workflow structure from parsing
            diagram_type: Diagram type ("react_flow", "bpmn", "drawio")
            layout: Layout algorithm ("hierarchical", "force", "dagre")
        
        Returns:
            Formatted visualization data with nodes, edges, metadata
        """
        # Extract nodes and edges from workflow structure
        nodes = workflow_content.get("nodes", [])
        edges = workflow_content.get("edges", [])
        metadata = workflow_content.get("metadata", {})
        
        # Format nodes for React Flow (default format)
        formatted_nodes = []
        for node in nodes:
            formatted_node = {
                "id": node.get("id", ""),
                "type": node.get("type", "default"),
                "data": {
                    "label": node.get("label", ""),
                    **node.get("data", {})
                },
                "position": self._calculate_position(len(formatted_nodes), layout)  # Simple position calculation
            }
            formatted_nodes.append(formatted_node)
        
        # Format edges for React Flow
        formatted_edges = []
        for edge in edges:
            formatted_edge = {
                "id": edge.get("id", ""),
                "source": edge.get("source", ""),
                "target": edge.get("target", ""),
                "label": edge.get("label", ""),
                "type": "smoothstep",  # Default edge type for React Flow
                "animated": False
            }
            if edge.get("data"):
                formatted_edge["data"] = edge.get("data")
            formatted_edges.append(formatted_edge)
        
        # Build visualization data
        visualization_data = {
            "nodes": formatted_nodes,
            "edges": formatted_edges,
            "metadata": metadata,
            "diagram_type": diagram_type,
            "layout": layout
        }
        
        # Add diagram-specific formatting if needed
        if diagram_type == "bpmn":
            # Could add BPMN-specific formatting here
            visualization_data["bpmn_format"] = "xml"  # or "json"
        elif diagram_type == "drawio":
            # Could add Draw.io-specific formatting here
            visualization_data["drawio_format"] = "xml"
        
        return visualization_data
    
    def _calculate_position(self, index: int, layout: str) -> Dict[str, float]:
        """
        Calculate node position based on layout algorithm.
        
        Simple implementation - can be enhanced with proper layout algorithms.
        
        Args:
            index: Node index
            layout: Layout algorithm
        
        Returns:
            Position dict with x, y coordinates
        """
        if layout == "hierarchical":
            # Simple hierarchical layout
            row = index // 3
            col = index % 3
            return {
                "x": col * 200,
                "y": row * 150
            }
        elif layout == "force":
            # Random positions for force-directed layout (frontend will handle actual layout)
            import random
            return {
                "x": random.randint(0, 800),
                "y": random.randint(0, 600)
            }
        else:  # dagre or default
            # Simple grid layout
            row = index // 4
            col = index % 4
            return {
                "x": col * 180,
                "y": row * 120
            }








