#!/usr/bin/env python3
"""
Workflow Visualization Abstraction

Infrastructure abstraction for workflow visualization capabilities.
Implements WorkflowVisualizationProtocol using WorkflowVisualizationAdapter.

WHAT (Infrastructure Abstraction Role): I provide unified workflow visualization infrastructure
HOW (Infrastructure Abstraction Implementation): I coordinate workflow visualization adapters
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..abstraction_contracts.workflow_visualization_protocol import (
    WorkflowVisualizationProtocol, VisualizationType, VisualizationData, 
    VisualizationResult
)
from ..infrastructure_adapters.workflow_visualization_adapter import WorkflowVisualizationAdapter

class WorkflowVisualizationAbstraction(WorkflowVisualizationProtocol):
    """Workflow visualization abstraction using workflow visualization adapter."""
    
    def __init__(self, workflow_visualization_adapter: WorkflowVisualizationAdapter, di_container=None, **kwargs):
        """
        Initialize workflow visualization abstraction.
        
        Args:
            workflow_visualization_adapter: Workflow visualization adapter instance
            di_container: DI Container for utilities
        """
        self.workflow_visualization_adapter = workflow_visualization_adapter
        self.di_container = di_container
        self.service_name = "workflow_visualization_abstraction"
        
        # Get logger from DI container if available, otherwise use module logger
        if self.di_container and hasattr(self.di_container, 'get_logger'):
            self.logger = self.di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("WorkflowVisualizationAbstraction")
        
        # Initialize abstraction
        self._initialize_abstraction()
    
    def _initialize_abstraction(self):
        """Initialize the workflow visualization abstraction."""
        try:
            self.logger.info("✅ Workflow Visualization Abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow visualization abstraction: {e}")
            raise  # Re-raise for service layer to handle

        """
        Create flowchart visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with flowchart data
        """
    async def create_workflow_flowchart(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """Create workflow flowchart visualization."""
        try:
            # Get utilities from DI container
            error_handler = None
            telemetry = None
            if self.di_container and hasattr(self.di_container, 'get_utility'):
                try:
                    error_handler = self.di_container.get_utility('error_handler')
                    telemetry = self.di_container.get_utility('telemetry')
                except Exception as e:
                    self.logger.error(f"❌ Error getting utilities: {e}")
                    pass

            # Use adapter to create flowchart
            result = await self.workflow_visualization_adapter.create_flowchart(workflow_data)
            
            if result.get("success"):
                visualization_data = VisualizationData(
                    type=VisualizationType.FLOWCHART,
                    title=result["visualization_data"].get("title", "Workflow"),
                    nodes=result["visualization_data"].get("nodes", []),
                    edges=result["visualization_data"].get("edges", []),
                    metadata=result["visualization_data"].get("metadata", {}),
                    created_at=datetime.utcnow()
                )
                
                visualization_result = VisualizationResult(
                    success=True,
                    visualization_data=visualization_data,
                    error=None,
                    created_at=datetime.utcnow()
                )
                
                return visualization_result
            else:
                return VisualizationResult(
                    success=False,
                    visualization_data=None,
                    error=result.get("error", "Flowchart creation failed"),
                    created_at=datetime.utcnow()
                )
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create workflow flowchart: {e}")
            raise  # Re-raise for service layer to handle
    
    async def create_swimlane_diagram(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create swimlane diagram visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with swimlane diagram data
        """
        try:
            # Get utilities from DI container
            error_handler = None
            telemetry = None
            if self.di_container and hasattr(self.di_container, 'get_utility'):
                pass
            
            result = await self.workflow_visualization_adapter.create_swimlane_diagram(workflow_data)
            
            if result.get("success"):
                visualization_data = VisualizationData(
                    type=VisualizationType.SWIMLANE,
                    title=result["visualization_data"].get("title", "Workflow"),
                    nodes=result["visualization_data"].get("swimlanes", []),
                    edges=[],
                    metadata=result["visualization_data"].get("metadata", {}),
                    created_at=datetime.utcnow()
                )
                
                visualization_result = VisualizationResult(
                    success=True,
                    visualization_data=visualization_data,
                    error=None,
                    created_at=datetime.utcnow()
                )
                
                return visualization_result
            else:
                return VisualizationResult(
                    success=False,
                    visualization_data=None,
                    error=result.get("error", "Swimlane diagram creation failed"),
                    created_at=datetime.utcnow()
                )
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create swimlane diagram: {e}")
            raise  # Re-raise for service layer to handle
    
    async def create_gantt_chart(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create Gantt chart visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with Gantt chart data
        """
        try:
            # Get utilities from DI container
            error_handler = None
            telemetry = None
            if self.di_container and hasattr(self.di_container, 'get_utility'):
                pass
            
            result = await self.workflow_visualization_adapter.create_gantt_chart(workflow_data)
            
            if result.get("success"):
                visualization_data = VisualizationData(
                    type=VisualizationType.GANTT,
                    title=result["visualization_data"].get("title", "Workflow"),
                    nodes=result["visualization_data"].get("tasks", []),
                    edges=[],
                    metadata=result["visualization_data"].get("metadata", {}),
                    created_at=datetime.utcnow()
                )
                
                visualization_result = VisualizationResult(
                    success=True,
                    visualization_data=visualization_data,
                    error=None,
                    created_at=datetime.utcnow()
                )
                
                return visualization_result
            else:
                return VisualizationResult(
                    success=False,
                    visualization_data=None,
                    error=result.get("error", "Gantt chart creation failed"),
                    created_at=datetime.utcnow()
                )
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create Gantt chart: {e}")
            raise  # Re-raise for service layer to handle
    
    async def create_network_diagram(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create network diagram visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with network diagram data
        """
        try:
            # Get utilities from DI container
            error_handler = None
            telemetry = None
            if self.di_container and hasattr(self.di_container, 'get_utility'):
                pass
            
            result = await self.workflow_visualization_adapter.create_network_diagram(workflow_data)
            
            if result.get("success"):
                visualization_data = VisualizationData(
                    type=VisualizationType.NETWORK,
                    title=result["visualization_data"].get("title", "Workflow"),
                    nodes=result["visualization_data"].get("nodes", []),
                    edges=result["visualization_data"].get("edges", []),
                    metadata=result["visualization_data"].get("metadata", {}),
                    created_at=datetime.utcnow()
                )
                
                visualization_result = VisualizationResult(
                    success=True,
                    visualization_data=visualization_data,
                    error=None,
                    created_at=datetime.utcnow()
                )
                
                return visualization_result
            else:
                return VisualizationResult(
                    success=False,
                    visualization_data=None,
                    error=result.get("error", "Network diagram creation failed"),
                    created_at=datetime.utcnow()
                )
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create network diagram: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_supported_visualization_types(self) -> List[str]:
        """
        Get list of supported visualization types.
        
        Returns:
            List of supported visualization types
        """
        # Get utilities from DI container
        error_handler = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            types = [
                VisualizationType.FLOWCHART,
                VisualizationType.SWIMLANE,
                VisualizationType.GANTT,
                VisualizationType.NETWORK
            ]
            return types
            
        """
        Validate workflow data for visualization.
        
        Args:
            workflow_data: Workflow data to validate
            
        Returns:
            Dict with validation results
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check required fields
            if not workflow_data.get("name"):
                validation_result["errors"].append("Workflow name is required")
                validation_result["valid"] = False
            
            if not workflow_data.get("nodes"):
                validation_result["errors"].append("Workflow nodes are required")
                validation_result["valid"] = False
            
            # Check node structure
            nodes = workflow_data.get("nodes", [])
            for i, node in enumerate(nodes):
                if not node.get("id"):
                    validation_result["errors"].append(f"Node {i} missing ID")
                    validation_result["valid"] = False
                
                if not node.get("name") and not node.get("label"):
                    validation_result["warnings"].append(f"Node {i} missing name/label")
            
            
            return validation_result
            
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        # Get utilities from DI container
        error_handler = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            adapter_health = await self.workflow_visualization_adapter.health_check()
            
            health_result = {
                "healthy": adapter_health.get("healthy", False),
                "adapter": adapter_health,
                "abstraction": {
                    "name": "WorkflowVisualizationAbstraction",
                    "status": "active"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_result
            