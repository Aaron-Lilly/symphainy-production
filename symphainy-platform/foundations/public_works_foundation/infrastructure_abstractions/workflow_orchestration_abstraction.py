#!/usr/bin/env python3
"""
Workflow Orchestration Abstraction

Infrastructure abstraction for workflow orchestration using Redis Graph.
Implements WorkflowOrchestrationProtocol using RedisGraphAdapter.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import uuid

from ..abstraction_contracts.workflow_orchestration_protocol import WorkflowOrchestrationProtocol
from bases.contracts.workflow_orchestration import (
    WorkflowDefinition, WorkflowExecution,
    WorkflowExecutionRequest, WorkflowStatus, NodeType, GatewayType
)
from ..infrastructure_adapters.redis_graph_adapter import RedisGraphAdapter

class WorkflowOrchestrationAbstraction(WorkflowOrchestrationProtocol):
    """Workflow orchestration abstraction using Redis Graph."""
    
    def __init__(self, redis_graph_adapter: RedisGraphAdapter, di_container=None, **kwargs):
        """
        Initialize workflow orchestration abstraction.
        
        Args:
            redis_graph_adapter: Redis Graph adapter instance
            di_container: DI Container for utilities (optional)
        """
        self.redis_graph_adapter = redis_graph_adapter
        self.di_container = di_container
        self.service_name = "workflow_orchestration_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("WorkflowOrchestrationAbstraction")
        
        # Workflow registry
        self.workflows = {}
        self.executions = {}
        
        # Initialize workflow graphs
        self._initialize_workflow_graphs()
    
    def _initialize_workflow_graphs(self):
        """Initialize workflow graphs."""
        try:
            # Create workflow graphs
            self.redis_graph_adapter.create_graph("workflow_orchestration")
            self.redis_graph_adapter.create_graph("workflow_executions")
            
            self.logger.info("✅ Workflow orchestration abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow graphs: {e}")
            raise  # Re-raise for service layer to handle
    
    async def create_workflow(self, definition: WorkflowDefinition) -> str:
        """
        Create a new workflow.
        
        Args:
            definition: Workflow definition
            
        Returns:
            str: Workflow ID
        """
        try:
            # Store workflow definition
            self.workflows[definition.id] = definition
            
            # Create workflow graph nodes
            for node in definition.nodes:
                self.redis_graph_adapter.create_node(
                    "workflow_orchestration",
                    f"workflow_{definition.id}_{node.id}",
                    labels=[node.type.value],
                    properties={
                        "workflow_id": definition.id,
                        "node_id": node.id,
                        "name": node.name,
                        "type": node.type.value,
                        "properties": node.properties or {}
                    }
                )
            
            # Create workflow graph edges
            for edge in definition.edges:
                self.redis_graph_adapter.create_relationship(
                    "workflow_orchestration",
                    f"workflow_{definition.id}_{edge.source}",
                    f"workflow_{definition.id}_{edge.target}",
                    "FLOWS_TO",
                    properties={
                        "workflow_id": definition.id,
                        "edge_id": edge.id,
                        "condition": edge.condition,
                        "properties": edge.properties or {}
                    }
                )
            
            self.logger.info(f"✅ Workflow {definition.id} created")
            
            return definition.id
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow {definition.id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_workflow(self, workflow_id: str, definition: WorkflowDefinition) -> bool:
        """
        Update an existing workflow.
        
        Args:
            workflow_id: Workflow ID
            definition: Updated workflow definition
            
        Returns:
            bool: Success status
        """
        try:
            # Update workflow definition
            self.workflows[workflow_id] = definition
            
            # Update workflow graph (simplified - in real implementation would be more complex)
            self.logger.info(f"✅ Workflow {workflow_id} updated")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update workflow {workflow_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            bool: Success status
        """
        try:
            # Remove from registry
            if workflow_id in self.workflows:
                del self.workflows[workflow_id]
            
            # Delete workflow nodes from graph
            query = f"MATCH (n {{workflow_id: '{workflow_id}'}}) DETACH DELETE n"
            self.redis_graph_adapter.execute_query("workflow_orchestration", query)
            
            self.logger.info(f"✅ Workflow {workflow_id} deleted")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """
        Get workflow definition.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Optional[WorkflowDefinition]: Workflow definition
        """
        try:
            workflow = self.workflows.get(workflow_id)
            
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow {workflow_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def list_workflows(self, limit: int = 100, offset: int = 0) -> List[WorkflowDefinition]:
        """
        List workflows.
        
        Args:
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip
            
        Returns:
            List[WorkflowDefinition]: Workflow definitions
        """
        try:
            workflow_list = list(self.workflows.values())
            result = workflow_list[offset:offset + limit]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to list workflows: {e}")
            raise  # Re-raise for service layer to handle
    
    async def execute_workflow(self, request: WorkflowExecutionRequest) -> str:
        """
        Execute a workflow.
        
        Args:
            request: Workflow execution request
            
        Returns:
            str: Execution ID
        """
        try:
            # Create execution instance
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=request.workflow_id,
                status=WorkflowStatus.RUNNING,
                started_at=datetime.now(),
                execution_data=request.input_data or {}
            )
            
            # Store execution
            self.executions[execution_id] = execution
            
            # Create execution graph nodes
            workflow = await self.get_workflow(request.workflow_id)
            if workflow:
                for node in workflow.nodes:
                    self.redis_graph_adapter.create_node(
                        "workflow_executions",
                        f"execution_{execution_id}_{node.id}",
                        labels=["EXECUTION_NODE"],
                        properties={
                            "execution_id": execution_id,
                            "workflow_id": request.workflow_id,
                            "node_id": node.id,
                            "status": "PENDING",
                            "execution_data": request.input_data or {}
                        }
                    )
            
            self.logger.info(f"✅ Workflow execution {execution_id} started")
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute workflow {request.workflow_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_execution_status(self, execution_id: str) -> WorkflowStatus:
        """
        Get workflow execution status.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            WorkflowStatus: Current execution status
        """
        try:
            execution = self.executions.get(execution_id)
            status = execution.status if execution else WorkflowStatus.FAILED
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get execution status {execution_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_execution_result(self, execution_id: str) -> Dict[str, Any]:
        """
        Get workflow execution result.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Dict: Execution result
        """
        try:
            execution = self.executions.get(execution_id)
            result = {
                "execution_id": execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "current_node": execution.current_node,
                "execution_data": execution.execution_data,
                "error": execution.error
            } if execution else {"error": "Execution not found"}
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get execution result {execution_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def pause_execution(self, execution_id: str) -> bool:
        """
        Pause workflow execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            bool: Success status
        """
        try:
            execution = self.executions.get(execution_id)
            success = False
            if execution:
                execution.status = WorkflowStatus.PAUSED
                self.logger.info(f"✅ Execution {execution_id} paused")
                success = True
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to pause execution {execution_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def resume_execution(self, execution_id: str) -> bool:
        """
        Resume workflow execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            bool: Success status
        """
        try:
            execution = self.executions.get(execution_id)
            success = False
            if execution:
                execution.status = WorkflowStatus.RUNNING
                self.logger.info(f"✅ Execution {execution_id} resumed")
                success = True
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to resume execution {execution_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel workflow execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            bool: Success status
        """
        try:
            execution = self.executions.get(execution_id)
            success = False
            if execution:
                execution.status = WorkflowStatus.CANCELLED
                execution.completed_at = datetime.now()
                self.logger.info(f"✅ Execution {execution_id} cancelled")
                success = True
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to cancel execution {execution_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_active_executions(self) -> List[WorkflowExecution]:
        """
        Get list of active workflow executions.
        
        Returns:
            List[WorkflowExecution]: Active executions
        """
        try:
            active_executions = [
                execution for execution in self.executions.values()
                if execution.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]
            ]
            
            return active_executions
            
        except Exception as e:
            self.logger.error(f"Failed to get active executions: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_execution_history(self, workflow_id: str, limit: int = 100) -> List[WorkflowExecution]:
        """
        Get workflow execution history.
        
        Args:
            workflow_id: Workflow ID
            limit: Maximum number of executions to return
            
        Returns:
            List[WorkflowExecution]: Execution history
        """
        try:
            workflow_executions = [
                execution for execution in self.executions.values()
                if execution.workflow_id == workflow_id
            ]
            result = workflow_executions[-limit:]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get execution history for {workflow_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def validate_workflow(self, definition: WorkflowDefinition) -> Dict[str, Any]:
        """
        Validate workflow definition.
        
        Args:
            definition: Workflow definition
            
        Returns:
            Dict: Validation result
        """
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check for required fields
            if not definition.id:
                validation_result["errors"].append("Workflow ID is required")
                validation_result["valid"] = False
            
            if not definition.name:
                validation_result["errors"].append("Workflow name is required")
                validation_result["valid"] = False
            
            # Check nodes
            if not definition.nodes:
                validation_result["errors"].append("Workflow must have at least one node")
                validation_result["valid"] = False
            
            # Check for start and end nodes
            has_start = any(node.type == NodeType.START for node in definition.nodes)
            has_end = any(node.type == NodeType.END for node in definition.nodes)
            
            if not has_start:
                validation_result["warnings"].append("Workflow should have a start node")
            
            if not has_end:
                validation_result["warnings"].append("Workflow should have an end node")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Failed to validate workflow: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_workflow_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow metrics.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Dict: Workflow metrics
        """
        try:
            # Get execution history
            executions = await self.get_execution_history(workflow_id)
            
            # Calculate metrics
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
            failed_executions = len([e for e in executions if e.status == WorkflowStatus.FAILED])
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            metrics = {
                "workflow_id": workflow_id,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow metrics for {workflow_id}: {e}")
            raise  # Re-raise for service layer to handle
