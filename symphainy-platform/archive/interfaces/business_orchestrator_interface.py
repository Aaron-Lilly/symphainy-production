#!/usr/bin/env python3
"""
Business Orchestrator Interface

Interface for business orchestration capabilities provided by the Business Orchestrator role.
Defines the contract for pillar coordination, workflow orchestration, and business process management.

WHAT (Business Enablement Role): I orchestrate business pillar interactions and workflows
HOW (Interface): I define the contract for business orchestration operations
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from utilities import UserContext


class OrchestrationType(Enum):
    """Types of orchestration operations."""
    PILLAR_COORDINATION = "pillar_coordination"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    SERVICE_DISCOVERY = "service_discovery"
    PROCESS_MANAGEMENT = "process_management"
    STATE_MANAGEMENT = "state_management"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class PillarType(Enum):
    """Types of business pillars."""
    CONTENT_PILLAR = "content_pillar"
    INSIGHTS_PILLAR = "insights_pillar"
    OPERATIONS_PILLAR = "operations_pillar"
    BUSINESS_OUTCOMES_PILLAR = "business_outcomes_pillar"
    DELIVERY_MANAGER = "delivery_manager"


@dataclass
class PillarCoordinationRequest:
    """Request for pillar coordination."""
    pillar_type: PillarType
    coordination_type: OrchestrationType
    coordination_data: Dict[str, Any]
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class PillarCoordinationResponse:
    """Response for pillar coordination."""
    success: bool
    coordination_id: Optional[str] = None
    pillar_status: Optional[Dict[str, Any]] = None
    coordination_result: Optional[Dict[str, Any]] = None
    message: str = "Pillar coordination completed"
    timestamp: Optional[datetime] = None


@dataclass
class WorkflowOrchestrationRequest:
    """Request for workflow orchestration."""
    workflow_name: str
    workflow_config: Dict[str, Any]
    pillar_coordination: List[PillarType]
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class WorkflowOrchestrationResponse:
    """Response for workflow orchestration."""
    success: bool
    workflow_id: Optional[str] = None
    workflow_status: Optional[WorkflowStatus] = None
    orchestration_result: Optional[Dict[str, Any]] = None
    message: str = "Workflow orchestration completed"
    timestamp: Optional[datetime] = None


@dataclass
class ServiceDiscoveryRequest:
    """Request for service discovery."""
    service_type: str
    pillar_type: Optional[PillarType] = None
    capabilities: Optional[List[str]] = None
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class ServiceDiscoveryResponse:
    """Response for service discovery."""
    success: bool
    discovered_services: Optional[List[Dict[str, Any]]] = None
    service_count: Optional[int] = None
    discovery_result: Optional[Dict[str, Any]] = None
    message: str = "Service discovery completed"
    timestamp: Optional[datetime] = None


@dataclass
class ProcessManagementRequest:
    """Request for process management."""
    process_name: str
    process_config: Dict[str, Any]
    pillar_involvement: List[PillarType]
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class ProcessManagementResponse:
    """Response for process management."""
    success: bool
    process_id: Optional[str] = None
    process_status: Optional[str] = None
    management_result: Optional[Dict[str, Any]] = None
    message: str = "Process management completed"
    timestamp: Optional[datetime] = None


@dataclass
class StateManagementRequest:
    """Request for state management."""
    state_key: str
    state_data: Dict[str, Any]
    pillar_type: Optional[PillarType] = None
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class StateManagementResponse:
    """Response for state management."""
    success: bool
    state_id: Optional[str] = None
    state_value: Optional[Dict[str, Any]] = None
    management_result: Optional[Dict[str, Any]] = None
    message: str = "State management completed"
    timestamp: Optional[datetime] = None


class IBusinessOrchestrator(ABC):
    """
    Business Orchestrator Interface
    
    Defines the contract for business orchestration capabilities, including pillar coordination,
    workflow orchestration, service discovery, process management, and state management.
    """
    
    @abstractmethod
    async def coordinate_pillars(self, request: PillarCoordinationRequest) -> PillarCoordinationResponse:
        """
        Coordinate activities between business pillars.
        
        Args:
            request: Pillar coordination request
            
        Returns:
            PillarCoordinationResponse: Coordination result
        """
        pass
    
    @abstractmethod
    async def orchestrate_workflow(self, request: WorkflowOrchestrationRequest) -> WorkflowOrchestrationResponse:
        """
        Orchestrate workflows across business pillars.
        
        Args:
            request: Workflow orchestration request
            
        Returns:
            WorkflowOrchestrationResponse: Orchestration result
        """
        pass
    
    @abstractmethod
    async def discover_services(self, request: ServiceDiscoveryRequest) -> ServiceDiscoveryResponse:
        """
        Discover services within business pillars.
        
        Args:
            request: Service discovery request
            
        Returns:
            ServiceDiscoveryResponse: Discovery result
        """
        pass
    
    @abstractmethod
    async def manage_process(self, request: ProcessManagementRequest) -> ProcessManagementResponse:
        """
        Manage business processes across pillars.
        
        Args:
            request: Process management request
            
        Returns:
            ProcessManagementResponse: Management result
        """
        pass
    
    @abstractmethod
    async def manage_state(self, request: StateManagementRequest) -> StateManagementResponse:
        """
        Manage state across business pillars.
        
        Args:
            request: State management request
            
        Returns:
            StateManagementResponse: State management result
        """
        pass
























