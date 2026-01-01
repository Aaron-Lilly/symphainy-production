#!/usr/bin/env python3
"""
Workflow Visualization Adapter

Lightweight infrastructure adapter for workflow visualization capabilities.
Wraps specific visualization libraries and provides consistent interface.

WHAT (Infrastructure Adapter Role): I provide lightweight workflow visualization infrastructure
HOW (Infrastructure Adapter Implementation): I wrap specific visualization libraries
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class WorkflowVisualizationAdapter:
    """
    Lightweight infrastructure adapter for workflow visualization.
    
    Wraps specific visualization libraries and provides consistent interface
    for creating flowcharts, swimlane diagrams, Gantt charts, and network diagrams.
    """
    
    def __init__(self, **kwargs):
        """Initialize workflow visualization adapter."""
        self.logger = logging.getLogger("WorkflowVisualizationAdapter")
        self.logger.info("✅ Workflow Visualization Adapter initialized")
    
    async def create_flowchart(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create flowchart visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with flowchart visualization data
        """
        try:
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            flowchart_data = {
                "type": "flowchart",
                "title": workflow_data.get("name", "Workflow"),
                "nodes": self._format_flowchart_nodes(nodes),
                "edges": self._format_flowchart_edges(edges),
                "layout": "hierarchical",
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                }
            }
            
            return {
                "success": True,
                "visualization_data": flowchart_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Flowchart creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def create_swimlane_diagram(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create swimlane diagram visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with swimlane diagram data
        """
        try:
            # Group nodes by responsible party
            swimlanes = self._group_nodes_by_responsible(workflow_data.get("nodes", []))
            
            swimlane_data = {
                "type": "swimlane",
                "title": workflow_data.get("name", "Workflow"),
                "swimlanes": swimlanes,
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "swimlane_count": len(swimlanes)
                }
            }
            
            return {
                "success": True,
                "visualization_data": swimlane_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Swimlane diagram creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def create_gantt_chart(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Gantt chart visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with Gantt chart data
        """
        try:
            tasks = self._extract_tasks_for_gantt(workflow_data.get("nodes", []))
            
            gantt_data = {
                "type": "gantt",
                "title": workflow_data.get("name", "Workflow"),
                "tasks": tasks,
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "task_count": len(tasks)
                }
            }
            
            return {
                "success": True,
                "visualization_data": gantt_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Gantt chart creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def create_network_diagram(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create network diagram visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with network diagram data
        """
        try:
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            network_data = {
                "type": "network",
                "title": workflow_data.get("name", "Workflow"),
                "nodes": self._format_network_nodes(nodes),
                "edges": self._format_network_edges(edges),
                "layout": "force_directed",
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                }
            }
            
            return {
                "success": True,
                "visualization_data": network_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Network diagram creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "created_at": datetime.utcnow().isoformat()
            }
    
    def _format_flowchart_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format nodes for flowchart visualization."""
        formatted_nodes = []
        
        for i, node in enumerate(nodes):
            formatted_node = {
                "id": node.get("id", f"node_{i}"),
                "label": node.get("name", node.get("label", f"Node {i}")),
                "type": node.get("type", "task"),
                "position": {"x": i * 200, "y": 100},
                "properties": node.get("properties", {})
            }
            formatted_nodes.append(formatted_node)
        
        return formatted_nodes
    
    def _format_flowchart_edges(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format edges for flowchart visualization."""
        formatted_edges = []
        
        for i, edge in enumerate(edges):
            formatted_edge = {
                "id": edge.get("id", f"edge_{i}"),
                "source": edge.get("source", edge.get("from", "")),
                "target": edge.get("target", edge.get("to", "")),
                "label": edge.get("label", ""),
                "type": edge.get("type", "success")
            }
            formatted_edges.append(formatted_edge)
        
        return formatted_edges
    
    def _group_nodes_by_responsible(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group nodes by responsible party for swimlane diagram."""
        swimlanes = {}
        
        for node in nodes:
            responsible = node.get("properties", {}).get("responsible", "Unassigned")
            if responsible not in swimlanes:
                swimlanes[responsible] = []
            swimlanes[responsible].append(node)
        
        return [
            {
                "lane_name": lane_name,
                "nodes": lane_nodes
            }
            for lane_name, lane_nodes in swimlanes.items()
        ]
    
    def _extract_tasks_for_gantt(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tasks for Gantt chart visualization."""
        tasks = []
        
        for node in nodes:
            if node.get("type") == "task":
                task = {
                    "id": node.get("id", ""),
                    "name": node.get("name", ""),
                    "start_date": node.get("properties", {}).get("start_date", "2024-01-01"),
                    "duration": node.get("properties", {}).get("duration", 1),
                    "responsible": node.get("properties", {}).get("responsible", "Unassigned")
                }
                tasks.append(task)
        
        return tasks
    
    def _format_network_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format nodes for network diagram visualization."""
        return self._format_flowchart_nodes(nodes)
    
    def _format_network_edges(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format edges for network diagram visualization."""
        return self._format_flowchart_edges(edges)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check adapter health."""
        try:
            return {
                "healthy": True,
                "adapter": "WorkflowVisualizationAdapter",
                "capabilities": [
                    "create_flowchart",
                    "create_swimlane_diagram",
                    "create_gantt_chart",
                    "create_network_diagram"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


