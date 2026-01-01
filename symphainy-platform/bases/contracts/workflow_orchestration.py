#!/usr/bin/env python3
"""
Workflow Orchestration Contract Data Structures

Data structures (dataclasses, enums) used for workflow orchestration abstraction contracts.
These define the shape of data passed to/from workflow orchestration abstractions.

Moved from foundations/public_works_foundation/abstraction_contracts/workflow_orchestration_protocol.py
to make them accessible to all realms without architectural violations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeType(Enum):
    """Workflow node type enumeration."""
    TASK = "task"
    GATEWAY = "gateway"
    EVENT = "event"
    START = "start"
    END = "end"


class GatewayType(Enum):
    """Gateway type enumeration."""
    EXCLUSIVE = "exclusive"
    PARALLEL = "parallel"
    INCLUSIVE = "inclusive"


@dataclass
class WorkflowNode:
    """Workflow node definition."""
    id: str
    name: str
    type: NodeType
    gateway_type: Optional[GatewayType] = None
    properties: Dict[str, Any] = None
    position: Tuple[float, float] = None


@dataclass
class WorkflowEdge:
    """Workflow edge definition."""
    id: str
    source: str
    target: str
    condition: Optional[str] = None
    properties: Dict[str, Any] = None


@dataclass
class WorkflowDefinition:
    """Workflow definition."""
    id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    properties: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class WorkflowExecution:
    """Workflow execution instance."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_node: Optional[str] = None
    execution_data: Dict[str, Any] = None
    error: Optional[str] = None


@dataclass
class WorkflowExecutionRequest:
    """Workflow execution request."""
    workflow_id: str
    input_data: Dict[str, Any] = None
    execution_options: Dict[str, Any] = None
    priority: int = 0

