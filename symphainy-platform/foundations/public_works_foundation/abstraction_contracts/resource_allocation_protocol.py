#!/usr/bin/env python3
"""
Resource Allocation Protocol

Abstraction contract for resource allocation and infrastructure management.
Defines interfaces for resource monitoring, allocation, and optimization.
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    """Resource type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"


class AllocationStatus(Enum):
    """Resource allocation status enumeration."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    UNAVAILABLE = "unavailable"


@dataclass
class ResourceSpec:
    """Resource specification."""
    resource_type: ResourceType
    amount: float
    unit: str
    properties: Dict[str, Any] = None


@dataclass
class ResourceAllocation:
    """Resource allocation."""
    allocation_id: str
    resource_specs: List[ResourceSpec]
    status: AllocationStatus
    allocated_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


@dataclass
class ResourceRequest:
    """Resource allocation request."""
    resource_specs: List[ResourceSpec]
    duration: Optional[int] = None  # Duration in seconds
    priority: int = 0
    metadata: Dict[str, Any] = None


@dataclass
class ResourceMetrics:
    """Resource usage metrics."""
    resource_type: ResourceType
    current_usage: float
    total_capacity: float
    utilization_percent: float
    timestamp: datetime


class ResourceAllocationProtocol(Protocol):
    """Protocol for resource allocation operations."""
    
    async def get_system_resources(self) -> Dict[str, Any]:
        """
        Get current system resource usage.
        
        Returns:
            Dict: System resource information
        """
        ...
    
    async def allocate_resources(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """
        Allocate resources for a task.
        
        Args:
            request: Resource allocation request
            
        Returns:
            Optional[ResourceAllocation]: Resource allocation or None if failed
        """
        ...
    
    async def deallocate_resources(self, allocation_id: str) -> bool:
        """
        Deallocate resources.
        
        Args:
            allocation_id: Resource allocation ID
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_allocation_status(self, allocation_id: str) -> Optional[ResourceAllocation]:
        """
        Get resource allocation status.
        
        Args:
            allocation_id: Resource allocation ID
            
        Returns:
            Optional[ResourceAllocation]: Resource allocation
        """
        ...
    
    async def get_active_allocations(self) -> List[ResourceAllocation]:
        """
        Get list of active resource allocations.
        
        Returns:
            List[ResourceAllocation]: Active allocations
        """
        ...
    
    async def get_resource_metrics(self, resource_type: ResourceType) -> List[ResourceMetrics]:
        """
        Get resource usage metrics.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            List[ResourceMetrics]: Resource metrics
        """
        ...
    
    async def get_resource_history(self, resource_type: ResourceType, hours: int = 24) -> List[ResourceMetrics]:
        """
        Get resource usage history.
        
        Args:
            resource_type: Type of resource
            hours: Number of hours to retrieve
            
        Returns:
            List[ResourceMetrics]: Resource history
        """
        ...
    
    async def optimize_resources(self) -> Dict[str, Any]:
        """
        Optimize resource allocation.
        
        Returns:
            Dict: Optimization recommendations
        """
        ...
    
    async def set_resource_limits(self, limits: Dict[str, Any]) -> bool:
        """
        Set resource limits.
        
        Args:
            limits: Resource limits
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_resource_limits(self) -> Dict[str, Any]:
        """
        Get current resource limits.
        
        Returns:
            Dict: Resource limits
        """
        ...
    
    async def monitor_resources(self, duration: int = 60, interval: int = 5) -> List[Dict[str, Any]]:
        """
        Monitor resources over time.
        
        Args:
            duration: Monitoring duration in seconds
            interval: Sampling interval in seconds
            
        Returns:
            List: Resource monitoring data
        """
        ...
    
    async def reserve_resources(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """
        Reserve resources for future use.
        
        Args:
            request: Resource reservation request
            
        Returns:
            Optional[ResourceAllocation]: Resource reservation or None if failed
        """
        ...
    
    async def release_reservation(self, allocation_id: str) -> bool:
        """
        Release resource reservation.
        
        Args:
            allocation_id: Resource allocation ID
            
        Returns:
            bool: Success status
        """
        ...



