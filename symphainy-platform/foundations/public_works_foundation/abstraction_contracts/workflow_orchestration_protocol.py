#!/usr/bin/env python3
"""
Workflow Orchestration Protocol

Abstraction contract for workflow orchestration and graph-based execution.
Defines interfaces for workflow creation, execution, and management.

Note: Data structures (dataclasses, enums) have been moved to bases/contracts/workflow_orchestration.py
for access by all realms. Import from bases.contracts.workflow_orchestration instead.
"""

from typing import Protocol, Dict, Any, List, Optional
from bases.contracts.workflow_orchestration import (
    WorkflowStatus,
    NodeType,
    GatewayType,
    WorkflowNode,
    WorkflowEdge,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionRequest
)


class WorkflowOrchestrationProtocol(Protocol):
    """Protocol for workflow orchestration operations."""
    
    async def create_workflow(self, definition: WorkflowDefinition) -> str:
        """
        Create a new workflow.
        
        Args:
            definition: Workflow definition
            
        Returns:
            str: Workflow ID
        """
        ...
    
    async def update_workflow(self, workflow_id: str, definition: WorkflowDefinition) -> bool:
        """
        Update an existing workflow.
        
        Args:
            workflow_id: Workflow ID
            definition: Updated workflow definition
            
        Returns:
            bool: Success status
        """
        ...
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """
        Get workflow definition.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Optional[WorkflowDefinition]: Workflow definition
        """
        ...
    
    async def list_workflows(self, limit: int = 100, offset: int = 0) -> List[WorkflowDefinition]:
        """
        List workflows.
        
        Args:
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip
            
        Returns:
            List[WorkflowDefinition]: Workflow definitions
        """
        ...
    
    async def execute_workflow(self, request: WorkflowExecutionRequest) -> str:
        """
        Execute a workflow.
        
        Args:
            request: Workflow execution request
            
        Returns:
            str: Execution ID
        """
        ...
    
    async def get_execution_status(self, execution_id: str) -> WorkflowStatus:
        """
        Get workflow execution status.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            WorkflowStatus: Current execution status
        """
        ...
    
    async def get_execution_result(self, execution_id: str) -> Dict[str, Any]:
        """
        Get workflow execution result.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Dict: Execution result
        """
        ...
    
    async def pause_execution(self, execution_id: str) -> bool:
        """
        Pause workflow execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            bool: Success status
        """
        ...
    
    async def resume_execution(self, execution_id: str) -> bool:
        """
        Resume workflow execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            bool: Success status
        """
        ...
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel workflow execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_active_executions(self) -> List[WorkflowExecution]:
        """
        Get list of active workflow executions.
        
        Returns:
            List[WorkflowExecution]: Active executions
        """
        ...
    
    async def get_execution_history(self, workflow_id: str, limit: int = 100) -> List[WorkflowExecution]:
        """
        Get workflow execution history.
        
        Args:
            workflow_id: Workflow ID
            limit: Maximum number of executions to return
            
        Returns:
            List[WorkflowExecution]: Execution history
        """
        ...
    
    async def validate_workflow(self, definition: WorkflowDefinition) -> Dict[str, Any]:
        """
        Validate workflow definition.
        
        Args:
            definition: Workflow definition
            
        Returns:
            Dict: Validation result
        """
        ...
    
    async def get_workflow_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow metrics.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Dict: Workflow metrics
        """
        ...



