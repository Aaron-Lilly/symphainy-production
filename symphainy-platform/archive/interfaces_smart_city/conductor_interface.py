#!/usr/bin/env python3
"""
Conductor Interface

Defines the contracts for Conductor service operations.
This interface matches the existing ConductorService APIs.

WHAT (Interface Role): I define the contracts for workflow orchestration
HOW (Interface Implementation): I provide clear, typed interfaces for consumers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Workflow status levels."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowPriority(str, Enum):
    """Workflow priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task status levels."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# Request Models
class CreateWorkflowRequest(BaseModel):
    """Request to create a new workflow."""
    workflow_name: str = Field(..., description="Name of the workflow")
    workflow_template: str = Field(..., description="Template to use for the workflow")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Workflow parameters")
    priority: Optional[WorkflowPriority] = Field(WorkflowPriority.NORMAL, description="Workflow priority")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant workflows")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Workflow metadata")


class ExecuteWorkflowRequest(BaseModel):
    """Request to execute a workflow."""
    workflow_id: str = Field(..., description="ID of the workflow to execute")
    execution_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution context")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant execution")


class GetWorkflowStatusRequest(BaseModel):
    """Request to get workflow status."""
    workflow_id: str = Field(..., description="ID of the workflow")
    include_tasks: Optional[bool] = Field(False, description="Include task details in response")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class PauseWorkflowRequest(BaseModel):
    """Request to pause a workflow."""
    workflow_id: str = Field(..., description="ID of the workflow to pause")
    reason: Optional[str] = Field("user_request", description="Reason for pausing")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class ResumeWorkflowRequest(BaseModel):
    """Request to resume a workflow."""
    workflow_id: str = Field(..., description="ID of the workflow to resume")
    execution_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Resume execution context")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


# Response Models
class CreateWorkflowResponse(BaseModel):
    """Response for workflow creation."""
    success: bool = Field(..., description="Workflow creation success status")
    workflow_id: Optional[str] = Field(None, description="Created workflow ID")
    workflow_name: Optional[str] = Field(None, description="Workflow name")
    workflow_status: Optional[WorkflowStatus] = Field(None, description="Initial workflow status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    message: str = Field(..., description="Response message")


class ExecuteWorkflowResponse(BaseModel):
    """Response for workflow execution."""
    success: bool = Field(..., description="Workflow execution success status")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    execution_id: Optional[str] = Field(None, description="Execution ID")
    workflow_status: Optional[WorkflowStatus] = Field(None, description="Current workflow status")
    started_at: Optional[str] = Field(None, description="Execution start timestamp")
    message: str = Field(..., description="Response message")


class GetWorkflowStatusResponse(BaseModel):
    """Response for workflow status."""
    success: bool = Field(..., description="Status retrieval success status")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    workflow_name: Optional[str] = Field(None, description="Workflow name")
    workflow_status: Optional[WorkflowStatus] = Field(None, description="Current workflow status")
    progress_percentage: Optional[float] = Field(None, description="Workflow progress percentage")
    tasks: Optional[List[Dict[str, Any]]] = Field(None, description="Task details if requested")
    started_at: Optional[str] = Field(None, description="Workflow start timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    message: str = Field(..., description="Response message")


class PauseWorkflowResponse(BaseModel):
    """Response for workflow pause."""
    success: bool = Field(..., description="Workflow pause success status")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    workflow_status: Optional[WorkflowStatus] = Field(None, description="Current workflow status")
    paused_at: Optional[str] = Field(None, description="Pause timestamp")
    reason: Optional[str] = Field(None, description="Pause reason")
    message: str = Field(..., description="Response message")


class ResumeWorkflowResponse(BaseModel):
    """Response for workflow resume."""
    success: bool = Field(..., description="Workflow resume success status")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    workflow_status: Optional[WorkflowStatus] = Field(None, description="Current workflow status")
    resumed_at: Optional[str] = Field(None, description="Resume timestamp")
    message: str = Field(..., description="Response message")


# Interface Definition
class IConductor:
    """
    Conductor Interface

    Defines the contracts for Conductor service operations.
    This interface matches the existing ConductorService APIs.
    """

    # Workflow Management
    async def create_workflow(self, request: CreateWorkflowRequest) -> CreateWorkflowResponse:
        """Create a new workflow from template."""
        pass

    async def execute_workflow(self, request: ExecuteWorkflowRequest) -> ExecuteWorkflowResponse:
        """Execute a workflow."""
        pass

    async def get_workflow_status(self, request: GetWorkflowStatusRequest) -> GetWorkflowStatusResponse:
        """Get workflow execution status."""
        pass

    async def pause_workflow(self, request: PauseWorkflowRequest) -> PauseWorkflowResponse:
        """Pause a running workflow."""
        pass

    async def resume_workflow(self, request: ResumeWorkflowRequest) -> ResumeWorkflowResponse:
        """Resume a paused workflow."""
        pass























