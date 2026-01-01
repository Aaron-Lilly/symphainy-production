#!/usr/bin/env python3
"""
Resource Allocation Abstraction

Infrastructure abstraction for resource allocation and infrastructure management.
Implements ResourceAllocationProtocol using ResourceAdapter.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import uuid

from ..abstraction_contracts.resource_allocation_protocol import (
    ResourceAllocationProtocol, ResourceRequest, ResourceAllocation,
    ResourceSpec, ResourceMetrics, AllocationStatus, ResourceType
)
from ..infrastructure_adapters.resource_adapter import ResourceAdapter

class ResourceAllocationAbstraction(ResourceAllocationProtocol):
    """Resource allocation abstraction using ResourceAdapter."""
    
    def __init__(self, resource_adapter: ResourceAdapter, di_container=None, **kwargs):
        """
        Initialize resource allocation abstraction.
        
        Args:
            resource_adapter: Resource adapter instance
            di_container: Dependency injection container
        """
        self.resource_adapter = resource_adapter
        self.di_container = di_container
        self.service_name = "resource_allocation_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Resource allocations
        self.allocations = {}
        
        # Initialize resource monitoring
        self._initialize_resource_monitoring()
    
    def _initialize_resource_monitoring(self):
        """Initialize resource monitoring."""
        try:
            self.logger.info("✅ Resource allocation abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize resource monitoring: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_system_resources(self) -> Dict[str, Any]:
        """
        Get current system resource usage.
        
        Returns:
            Dict: System resource information
        """
        try:
            result = self.resource_adapter.get_system_resources()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get system resources: {e}")
            raise  # Re-raise for service layer to handle

        """
        Allocate resources for a task.
        
        Args:
            request: Resource allocation request
            
        Returns:
            Optional[ResourceAllocation]: Resource allocation or None if failed
        """
        try:
            # Convert ResourceRequest to ResourceAdapter format
            resource_request = {
                "cpu": 0,
                "memory": 0,
                "disk": 0
            }
            
            for spec in request.resource_specs:
                if spec.resource_type == ResourceType.CPU:
                    resource_request["cpu"] = spec.amount
                elif spec.resource_type == ResourceType.MEMORY:
                    resource_request["memory"] = spec.amount
                elif spec.resource_type == ResourceType.DISK:
                    resource_request["disk"] = spec.amount
            
            # Allocate resources using adapter
            result = self.resource_adapter.allocate_resources(resource_request)
            
            if result.get("allocated", False):
                # Create resource allocation
                allocation_id = result.get("allocation_id", str(uuid.uuid4()))
                allocation = ResourceAllocation(
                    allocation_id=allocation_id,
                    resource_specs=request.resource_specs,
                    status=AllocationStatus.ALLOCATED,
                    allocated_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(seconds=request.duration) if request.duration else None
                )
                
                # Store allocation
                self.allocations[allocation_id] = allocation
                
                self.logger.info(f"✅ Resources allocated: {allocation_id}")
                
                return allocation
            else:
                self.logger.warning(f"Failed to allocate resources: {result.get('reason', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to allocate resources: {e}")
            raise  # Re-raise for service layer to handle

        """
        Deallocate resources.
        
        Args:
            allocation_id: Resource allocation ID
            
        Returns:
            bool: Success status
        """
        try:
            # Deallocate using adapter
            success = self.resource_adapter.deallocate_resources(allocation_id)
            
            if success:
                # Update allocation status
                if allocation_id in self.allocations:
                    self.allocations[allocation_id].status = AllocationStatus.UNAVAILABLE
                
                self.logger.info(f"✅ Resources deallocated: {allocation_id}")
                
            else:
                self.logger.warning(f"Failed to deallocate resources: {allocation_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deallocate resources {allocation_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get resource allocation status.
        
        Args:
            allocation_id: Resource allocation ID
            
        Returns:
            Optional[ResourceAllocation]: Resource allocation
        """
        try:
            result = self.allocations.get(allocation_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get allocation status {allocation_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get list of active resource allocations.
        
        Returns:
            List[ResourceAllocation]: Active allocations
        """
        try:
            active_allocations = [
                allocation for allocation in self.allocations.values()
                if allocation.status == AllocationStatus.ALLOCATED
            ]
            
            return active_allocations
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get active allocations: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get resource usage metrics.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            List[ResourceMetrics]: Resource metrics
        """
        try:
            # Get system resources
            system_resources = await self.get_system_resources()
            
            # Convert to ResourceMetrics
            metrics = []
            
            if resource_type == ResourceType.CPU:
                metrics.append(ResourceMetrics(
                    resource_type=ResourceType.CPU,
                    current_usage=system_resources.get("cpu", {}).get("percent", 0),
                    total_capacity=100.0,
                    utilization_percent=system_resources.get("cpu", {}).get("percent", 0),
                    timestamp=datetime.now()
                ))
            
            elif resource_type == ResourceType.MEMORY:
                memory_data = system_resources.get("memory", {})
                metrics.append(ResourceMetrics(
                    resource_type=ResourceType.MEMORY,
                    current_usage=memory_data.get("available", 0),
                    total_capacity=memory_data.get("total", 0),
                    utilization_percent=memory_data.get("percent", 0),
                    timestamp=datetime.now()
                ))
            
            elif resource_type == ResourceType.DISK:
                disk_data = system_resources.get("disk", {})
                metrics.append(ResourceMetrics(
                    resource_type=ResourceType.DISK,
                    current_usage=disk_data.get("available", 0),
                    total_capacity=disk_data.get("total", 0),
                    utilization_percent=disk_data.get("percent", 0),
                    timestamp=datetime.now()
                ))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get resource metrics for {resource_type}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get resource usage history.
        
        Args:
            resource_type: Type of resource
            hours: Number of hours to retrieve
            
        Returns:
            List[ResourceMetrics]: Resource history
        """
        try:
            # Get resource history from adapter
            history_data = self.resource_adapter.get_resource_history(hours)
            
            # Convert to ResourceMetrics
            metrics = []
            for data_point in history_data:
                if resource_type.value in data_point:
                    resource_data = data_point[resource_type.value]
                    metrics.append(ResourceMetrics(
                        resource_type=resource_type,
                        current_usage=resource_data.get("available", 0),
                        total_capacity=resource_data.get("total", 0),
                        utilization_percent=resource_data.get("percent", 0),
                        timestamp=datetime.fromisoformat(data_point.get("timestamp", datetime.now().isoformat()))
                    ))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get resource history for {resource_type}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Optimize resource allocation.
        
        Returns:
            Dict: Optimization recommendations
        """
        try:
            result = self.resource_adapter.optimize_resources()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to optimize resources: {e}")
            raise  # Re-raise for service layer to handle

        """
        Set resource limits.
        
        Args:
            limits: Resource limits
            
        Returns:
            bool: Success status
        """
        try:
            success = self.resource_adapter.set_resource_limits(limits)
            
            if success:
                self.logger.info("✅ Resource limits updated")
                
            else:
                self.logger.warning("Failed to update resource limits")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to set resource limits: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get current resource limits.
        
        Returns:
            Dict: Resource limits
        """
        try:
            result = self.resource_adapter.get_resource_limits()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get resource limits: {e}")
            raise  # Re-raise for service layer to handle

        """
        Monitor resources over time.
        
        Args:
            duration: Monitoring duration in seconds
            interval: Sampling interval in seconds
            
        Returns:
            List: Resource monitoring data
        """
        try:
            result = self.resource_adapter.monitor_resources(duration, interval)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to monitor resources: {e}")
            raise  # Re-raise for service layer to handle

        """
        Reserve resources for future use.
        
        Args:
            request: Resource reservation request
            
        Returns:
            Optional[ResourceAllocation]: Resource reservation or None if failed
        """
        try:
            # Create reservation allocation
            allocation_id = str(uuid.uuid4())
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                resource_specs=request.resource_specs,
                status=AllocationStatus.RESERVED,
                allocated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=request.duration) if request.duration else None
            )
            
            # Store reservation
            self.allocations[allocation_id] = allocation
            
            self.logger.info(f"✅ Resources reserved: {allocation_id}")
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"❌ Failed to reserve resources: {e}")
            raise  # Re-raise for service layer to handle

        """
        Release resource reservation.
        
        Args:
            allocation_id: Resource allocation ID
            
        Returns:
            bool: Success status
        """
        try:
            # Update allocation status
            if allocation_id in self.allocations:
                self.allocations[allocation_id].status = AllocationStatus.AVAILABLE
                self.logger.info(f"✅ Resource reservation released: {allocation_id}")
                
                return True
            else:
                self.logger.warning(f"Resource allocation not found: {allocation_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to release reservation {allocation_id}: {e}")
            raise  # Re-raise for service layer to handle
