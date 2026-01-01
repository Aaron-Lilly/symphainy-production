#!/usr/bin/env python3
"""
Load Balancing Module - Traffic Cop Service

Handles service instance selection and load balancing strategies.
"""

import random
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    LoadBalancingRequest, LoadBalancingResponse, LoadBalancingStrategy,
    ServiceInstance
)


class LoadBalancing:
    """Load balancing module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def select_service(self, request: LoadBalancingRequest, user_context: Optional[Dict[str, Any]] = None) -> LoadBalancingResponse:
        """Select service instance using load balancing strategy."""
        service_name = request.service_name
        strategy = request.strategy or LoadBalancingStrategy.ROUND_ROBIN
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "select_service_start",
            success=True,
            details={"service_name": service_name, "strategy": strategy.value}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "load_balancing", "read"):
                        await self.service.record_health_metric("select_service_access_denied", 1.0, {"service_name": service_name})
                        await self.service.log_operation_with_telemetry("select_service_complete", success=False)
                        return LoadBalancingResponse(
                            success=False,
                            error="Access denied: insufficient permissions",
                            service_name=service_name
                        )
            
            self.service.traffic_metrics["load_balancing_operations"] += 1
            
            # Get available service instances
            instances = self.service.service_instances.get(service_name, [])
            if not instances:
                await self.service.record_health_metric("no_service_instances", 1.0, {"service_name": service_name})
                await self.service.log_operation_with_telemetry("select_service_complete", success=False, details={"service_name": service_name, "reason": "no_instances"})
                return LoadBalancingResponse(
                    success=False,
                    error="No service instances available",
                    service_name=service_name
                )
            
            # Select instance based on strategy
            selected_instance = await self._select_instance_by_strategy(instances, strategy)
            
            if not selected_instance:
                await self.service.record_health_metric("service_selection_failed", 1.0, {"service_name": service_name})
                await self.service.log_operation_with_telemetry("select_service_complete", success=False, details={"service_name": service_name, "reason": "selection_failed"})
                return LoadBalancingResponse(
                    success=False,
                    error="Failed to select service instance",
                    service_name=service_name
                )
            
            # Record health metric
            await self.service.record_health_metric(
                "service_selected",
                1.0,
                {"service_name": service_name, "strategy": strategy.value, "instance_id": selected_instance.id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "select_service_complete",
                success=True,
                details={"service_name": service_name, "strategy": strategy.value, "instance_id": selected_instance.id}
            )
            
            return LoadBalancingResponse(
                success=True,
                service_instance=selected_instance,
                service_name=service_name,
                strategy_used=strategy.value,
                selection_time=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "select_service")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "select_service_complete",
                success=False,
                details={"service_name": service_name, "error": str(e)}
            )
            return LoadBalancingResponse(
                success=False,
                error=str(e),
                service_name=request.service_name
            )
    
    async def _select_instance_by_strategy(self, instances: List[ServiceInstance], 
                                         strategy: LoadBalancingStrategy) -> Optional[ServiceInstance]:
        """Select instance based on load balancing strategy."""
        if not instances:
            return None
        
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return await self._round_robin_selection(instances)
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return await self._least_connections_selection(instances)
        elif strategy == LoadBalancingStrategy.WEIGHTED:
            return await self._weighted_selection(instances)
        elif strategy == LoadBalancingStrategy.HEALTH_BASED:
            return await self._health_based_selection(instances)
        elif strategy == LoadBalancingStrategy.RANDOM:
            return await self._random_selection(instances)
        else:
            return await self._round_robin_selection(instances)
    
    async def _round_robin_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin selection algorithm."""
        if not instances:
            return None
        
        # Use service name as key for counter
        service_name = instances[0].metadata.get("service_name", "default")
        counter = self.service.load_balancing_counters.get(service_name, 0)
        selected_instance = instances[counter % len(instances)]
        self.service.load_balancing_counters[service_name] = counter + 1
        
        return selected_instance
    
    async def _least_connections_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection algorithm."""
        if not instances:
            return None
        
        # Get connection counts from Redis via messaging abstraction
        min_connections = float('inf')
        selected_instance = None
        
        for instance in instances:
            connection_key = f"load_balancer:connections:{instance.id}"
            connections = await self.service.messaging_abstraction.get_data(connection_key) or 0
            
            if connections < min_connections:
                min_connections = connections
                selected_instance = instance
        
        return selected_instance or instances[0]
    
    async def _weighted_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted selection algorithm."""
        if not instances:
            return None
        
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return instances[0]
        
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for instance in instances:
            current_weight += instance.weight
            if random_value <= current_weight:
                return instance
        
        return instances[-1]
    
    async def _health_based_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Health-based selection algorithm."""
        if not instances:
            return None
        
        # Check health of instances
        best_health_score = -1
        selected_instance = None
        
        for instance in instances:
            health_score = await self._check_instance_health(instance)
            if health_score > best_health_score:
                best_health_score = health_score
                selected_instance = instance
        
        return selected_instance or instances[0]
    
    async def _random_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection algorithm."""
        if not instances:
            return None
        
        return random.choice(instances)
    
    async def _check_instance_health(self, instance: ServiceInstance) -> int:
        """Check health of a specific instance."""
        try:
            if not instance.health_check_url:
                return 100  # Assume healthy if no health check URL
            
            # Use httpx for health check
            if self.service.httpx:
                async with self.service.httpx.AsyncClient() as client:
                    response = await client.get(instance.health_check_url, timeout=5.0)
                    if response.status_code == 200:
                        return 100
                    else:
                        return 0
            
            return 50  # Default health score
            
        except Exception as e:
            self.service._log("error", f"Health check failed for {instance.id}: {e}")
            return 0
    
    async def register_service_instance(self, service_name: str, instance: ServiceInstance, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new service instance."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "register_service_instance_start",
            success=True,
            details={"service_name": service_name, "instance_id": instance.id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "load_balancing", "write"):
                        await self.service.record_health_metric("register_service_instance_access_denied", 1.0, {"service_name": service_name})
                        await self.service.log_operation_with_telemetry("register_service_instance_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to register service instance")
            
            if service_name not in self.service.service_instances:
                self.service.service_instances[service_name] = []
                self.service.load_balancing_counters[service_name] = 0
            
            self.service.service_instances[service_name].append(instance)
            
            # Store in Redis via messaging abstraction
            if self.service.messaging_abstraction:
                service_key = f"load_balancer:services:{service_name}"
                service_data = {
                    "instances": [
                        {
                            "id": inst.id,
                            "host": inst.host,
                            "port": inst.port,
                            "weight": inst.weight,
                            "health_check_url": inst.health_check_url,
                            "metadata": inst.metadata
                        }
                        for inst in self.service.service_instances[service_name]
                    ]
                }
                await self.service.messaging_abstraction.store_data(service_key, service_data)
            
            # Record health metric
            await self.service.record_health_metric(
                "service_instance_registered",
                1.0,
                {"service_name": service_name, "instance_id": instance.id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "register_service_instance_complete",
                success=True,
                details={"service_name": service_name, "instance_id": instance.id}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "register_service_instance")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "register_service_instance_complete",
                success=False,
                details={"service_name": service_name, "instance_id": instance.id, "error": str(e)}
            )
            return False
    
    async def unregister_service_instance(self, service_name: str, instance_id: str) -> bool:
        """Unregister a service instance."""
        try:
            if service_name in self.service.service_instances:
                self.service.service_instances[service_name] = [
                    inst for inst in self.service.service_instances[service_name] 
                    if inst.id != instance_id
                ]
                
                # Update Redis
                service_key = f"load_balancer:services:{service_name}"
                service_data = {
                    "instances": [
                        {
                            "id": inst.id,
                            "host": inst.host,
                            "port": inst.port,
                            "weight": inst.weight,
                            "health_check_url": inst.health_check_url,
                            "metadata": inst.metadata
                        }
                        for inst in self.service.service_instances[service_name]
                    ]
                }
                await self.service.messaging_abstraction.store_data(service_key, service_data)
                
                self.service._log("info", f"Unregistered service instance {instance_id} for {service_name}")
                return True
            
            return False
            
        except Exception as e:
            self.service._log("error", f"Failed to unregister service instance: {e}")
            return False







