"""
Workflow Builder Statistics Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class WorkflowBuilderStatistics:
    """
    Workflow Builder Statistics following Smart City patterns.
    Handles workflow statistics and analytics.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("WorkflowBuilderStatistics micro-module initialized")
    
    async def get_workflow_statistics(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the workflow."""
        try:
            nodes = workflow.get("nodes", [])
            edges = workflow.get("edges", [])
            total_nodes = len(nodes)
            total_edges = len(edges)
            
            # Calculate workflow statistics
            node_types = {}
            for node in nodes:
                node_type = node.get("type", "unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            # Check connectivity
            connected_nodes = set()
            for edge in edges:
                connected_nodes.add(edge.get("from_node"))
                connected_nodes.add(edge.get("to_node"))
            
            all_node_ids = {node["id"] for node in nodes}
            disconnected_nodes = all_node_ids - connected_nodes
            
            return {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "node_types": node_types,
                "connected_nodes": len(connected_nodes),
                "disconnected_nodes": len(disconnected_nodes),
                "connectivity_score": len(connected_nodes) / total_nodes if total_nodes > 0 else 0,
                "created_at": workflow.get("created_at"),
                "updated_at": workflow.get("updated_at")
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating workflow statistics: {e}")
            return {"error": str(e)}

