#!/usr/bin/env python3
"""
Load Balancing Abstraction - Business Logic Implementation

Implements load balancing operations with business logic.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage load balancing across services
HOW (Infrastructure Implementation): I implement load balancing algorithms and service selection
"""

import logging
import random
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from ..abstraction_contracts.load_balancing_protocol import (
    LoadBalancingProtocol, LoadBalancingStrategy, ServiceInstance, LoadBalancingRequest, LoadBalancingResponse
)

logger = logging.getLogger(__name__)

class LoadBalancingAbstraction(LoadBalancingProtocol):
    """
    Load balancing abstraction with business logic.
    
    Implements sophisticated load balancing algorithms for Traffic Cop
    including round-robin, least-connections, weighted, and health-based selection.
    """
    
    def __init__(self, redis_adapter, config_adapter, di_container=None):
        """
        Initialize load balancing abstraction.
        
        Args:
            redis_adapter: Redis adapter
            config_adapter: Configuration adapter
            di_container: Dependency injection container
        """
        self.redis_adapter = redis_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "load_balancing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Load balancing configuration
        self.default_strategy = LoadBalancingStrategy.ROUND_ROBIN
        self.health_check_interval = 30  # seconds
        self.service_timeout = 5  # seconds
        
        # Service registry and health tracking
        self.service_instances: Dict[str, List[ServiceInstance]] = {}
        self.service_health: Dict[str, Dict[str, Any]] = {}
        self.round_robin_counters: Dict[str, int] = {}
        
        # Load balancing statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "health_checks": 0,
            "service_failures": 0
        }
        
        self.logger.info("✅ Load Balancing Abstraction initialized")
    
    async def initialize(self):
        """Initialize load balancing abstraction."""
        try:
            # Load service configurations
            await self._load_service_configurations()
            
            # Start health checking
            await self._start_health_checking()
            
            self.logger.info("✅ Load Balancing Abstraction initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Load Balancing Abstraction: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def _load_service_configurations(self):
        """Load service configurations from Redis."""
        try:
            # Load service instances from Redis
            service_keys = await self.redis_adapter.get_keys("load_balancer:services:*")
            
            for key in service_keys:
                service_name = key.split(":")[-1]
                service_data = await self.redis_adapter.get_data(key)
                
                if service_data:
                    instances = []
                    for instance_data in service_data.get("instances", []):
                        instance = ServiceInstance(
                            id=instance_data["id"],
                            host=instance_data["host"],
                            port=instance_data["port"],
                            weight=instance_data.get("weight", 1),
                            health_check_url=instance_data.get("health_check_url"),
                        )
                        instances.append(instance)
                    
                    self.service_instances[service_name] = instances
                    self.round_robin_counters[service_name] = 0
                    
                    # Initialize health tracking
                    self.service_health[service_name] = {
                        "healthy_instances": [],
                        "unhealthy_instances": [],
                        "last_health_check": None
                    }
            
            self.logger.info(f"Loaded {len(self.service_instances)} service configurations")
            
        except Exception as e:
            self.logger.error(f"Failed to load service configurations: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def _start_health_checking(self):
        """Start health checking for all services."""
        try:
            # This would typically run in a background task
            # For now, we'll just initialize the health tracking
            for service_name in self.service_instances:
                await self._check_service_health(service_name)
            
            self.logger.info("Health checking initialized for all services")
            
        except Exception as e:
            self.logger.error(f"Failed to start health checking: {e}")
            raise  # Re-raise for service layer to handle

        """
        Select a service instance using the specified strategy.
        
        Args:
            request: Load balancing request with service name and strategy
            
        Returns:
            LoadBalancingResponse: Selected service instance or error
        """
        try:
            self.stats["total_requests"] += 1
            
            service_name = request.service_name
            strategy = request.strategy or self.default_strategy
            
            # Get available service instances
            instances = self.service_instances.get(service_name, [])
            if not instances:
                self.stats["failed_requests"] += 1
                return LoadBalancingResponse(
                    success=False,
                    error="No service instances available"
                )
            
            # Filter healthy instances
            healthy_instances = self._get_healthy_instances(service_name)
            if not healthy_instances:
                self.stats["failed_requests"] += 1
                return LoadBalancingResponse(
                    success=False,
                    error="No healthy service instances available"
                )
            
            # Select instance based on strategy
            selected_instance = await self._select_instance_by_strategy(
                healthy_instances, strategy, request
            )
            
            if not selected_instance:
                self.stats["failed_requests"] += 1
                return LoadBalancingResponse(
                    success=False,
                    error="Failed to select service instance"
                )
            
            self.stats["successful_requests"] += 1
            
            response = LoadBalancingResponse(
                success=True,
                service_instance=selected_instance,
                service_name=service_name,
                strategy_used=strategy.value,
                selection_time=datetime.utcnow().isoformat()
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Failed to select service: {e}")
            self.stats["failed_requests"] += 1
            raise  # Re-raise for service layer to handle
    
    async def _select_instance_by_strategy(self,
                                         instances: List[ServiceInstance],
                                         strategy: LoadBalancingStrategy,
                                         request: LoadBalancingRequest) -> Optional[ServiceInstance]:
        """Select instance based on load balancing strategy."""
        try:
            if strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return await self._round_robin_selection(instances, request.service_name)
            elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return await self._least_connections_selection(instances)
            elif strategy == LoadBalancingStrategy.WEIGHTED:
                return await self._weighted_selection(instances)
            elif strategy == LoadBalancingStrategy.HEALTH_BASED:
                return await self._health_based_selection(instances)
            elif strategy == LoadBalancingStrategy.RANDOM:
                return await self._random_selection(instances)
            else:
                # Default to round-robin
                return await self._round_robin_selection(instances, request.service_name)
                
        except Exception as e:
            self.logger.error(f"Failed to select instance by strategy: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _round_robin_selection(self, instances: List[ServiceInstance], service_name: str) -> Optional[ServiceInstance]:
        """Round-robin selection algorithm."""
        if not instances:
            return None
        
        counter = self.round_robin_counters.get(service_name, 0)
        selected_instance = instances[counter % len(instances)]
        self.round_robin_counters[service_name] = counter + 1
        
        return selected_instance
    
    async def _least_connections_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection algorithm."""
        if not instances:
            return None
        
        # Get connection counts from Redis
        min_connections = float('inf')
        selected_instance = None
        
        for instance in instances:
            connection_key = f"load_balancer:connections:{instance.id}"
            connections = await self.redis_adapter.get_data(connection_key) or 0
            
            if connections < min_connections:
                min_connections = connections
                selected_instance = instance
        
        return selected_instance
    
    async def _weighted_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted selection algorithm."""
        if not instances:
            return None
        
        # Calculate total weight
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return instances[0]  # Fallback to first instance
        
        # Weighted random selection
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for instance in instances:
            current_weight += instance.weight
            if random_value <= current_weight:
                return instance
        
        # Fallback to last instance
        return instances[-1]
    
    async def _health_based_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Health-based selection algorithm."""
        if not instances:
            return None
        
        # Select instance with best health score
        best_health_score = -1
        selected_instance = None
        
        for instance in instances:
            health_key = f"load_balancer:health:{instance.id}"
            health_data = await self.redis_adapter.get_data(health_key)
            
            if health_data:
                health_score = health_data.get("score", 0)
                if health_score > best_health_score:
                    best_health_score = health_score
                    selected_instance = instance
        
        return selected_instance or instances[0]  # Fallback to first instance
    
    async def _random_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection algorithm."""
        if not instances:
            return None
        
        return random.choice(instances)
    
    def _get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """Get healthy instances for a service."""
        instances = self.service_instances.get(service_name, [])
        health_data = self.service_health.get(service_name, {})
        healthy_instance_ids = health_data.get("healthy_instances", [])
        
        return [instance for instance in instances if instance.id in healthy_instance_ids]
    
    async def _check_service_health(self, service_name: str):
        """Check health of all instances for a service."""
        try:
            self.stats["health_checks"] += 1
            
            instances = self.service_instances.get(service_name, [])
            healthy_instances = []
            unhealthy_instances = []
            
            for instance in instances:
                is_healthy = await self._check_instance_health(instance)
                
                if is_healthy:
                    healthy_instances.append(instance.id)
                else:
                    unhealthy_instances.append(instance.id)
                    self.stats["service_failures"] += 1
            
            # Update health tracking
            self.service_health[service_name] = {
                "healthy_instances": healthy_instances,
                "unhealthy_instances": unhealthy_instances,
                "last_health_check": datetime.utcnow().isoformat()
            }
            
            # Store health data in Redis
            health_key = f"load_balancer:health:{service_name}"
            await self.redis_adapter.store_data(health_key, self.service_health[service_name])
            
        except Exception as e:
            self.logger.error(f"Failed to check service health for {service_name}: {e}")
            raise  # Re-raise for service layer to handle

        """Check health of a specific instance."""
        try:
            if not instance.health_check_url:
                return True  # Assume healthy if no health check URL
            
            # This would typically make an HTTP request to the health check URL
            # For now, we'll simulate a health check
            health_key = f"load_balancer:health:{instance.id}"
            health_data = await self.redis_adapter.get_data(health_key)
            
            if health_data:
                last_check = health_data.get("last_check")
                if last_check:
                    # Check if health check is recent
                    check_time = datetime.fromisoformat(last_check)
                    if (datetime.utcnow() - check_time).seconds < self.health_check_interval:
                        return health_data.get("healthy", False)
            
            # Simulate health check (in real implementation, this would be an HTTP request)
            is_healthy = random.random() > 0.1  # 90% chance of being healthy
            
            # Store health check result
            health_data = {
                "healthy": is_healthy,
                "last_check": datetime.utcnow().isoformat(),
                "score": 100 if is_healthy else 0
            }
            await self.redis_adapter.store_data(health_key, health_data)
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"Failed to check instance health for {instance.id}: {e}")
            raise  # Re-raise for service layer to handle

        """Register a new service instance."""
        try:
            if service_name not in self.service_instances:
                self.service_instances[service_name] = []
                self.round_robin_counters[service_name] = 0
                self.service_health[service_name] = {
                    "healthy_instances": [],
                    "unhealthy_instances": [],
                    "last_health_check": None
                }
            
            self.service_instances[service_name].append(instance)
            
            # Store in Redis
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
                    for inst in self.service_instances[service_name]
                ]
            }
            await self.redis_adapter.store_data(service_key, service_data)
            
            self.logger.info(f"Registered service instance {instance.id} for {service_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register service instance: {e}")
            raise  # Re-raise for service layer to handle

        """Unregister a service instance."""
        try:
            if service_name in self.service_instances:
                self.service_instances[service_name] = [
                    inst for inst in self.service_instances[service_name] 
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
                        for inst in self.service_instances[service_name]
                    ]
                }
                await self.redis_adapter.store_data(service_key, service_data)
                
                self.logger.info(f"Unregistered service instance {instance_id} for {service_name}")
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to unregister service instance: {e}")
            raise  # Re-raise for service layer to handle

        """Get load balancing statistics."""
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "health_checks": self.stats["health_checks"],
            "service_failures": self.stats["service_failures"],
            "registered_services": len(self.service_instances),
            "total_instances": sum(len(instances) for instances in self.service_instances.values()),
            "healthy_instances": sum(
                len(health_data.get("healthy_instances", []))
                for health_data in self.service_health.values()
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for load balancing abstraction."""
        try:
            # Check Redis connectivity
            redis_health = await self.redis_adapter.health_check()
            
            health_status = {
                "healthy": redis_health.get("healthy", False),
                "load_balancing_stats": await self.get_load_balancing_stats(),
                "redis_adapter": redis_health
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Load balancing health check failed: {e}")

            raise  # Re-raise for service layer to handle
