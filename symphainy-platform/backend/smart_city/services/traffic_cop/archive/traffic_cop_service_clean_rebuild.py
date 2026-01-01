#!/usr/bin/env python3
"""
Traffic Cop Service - Clean Rebuild with Proper Infrastructure

Clean implementation using Public Works abstractions for infrastructure
and direct library injection for business logic.

WHAT (Smart City Role): I orchestrate API Gateway routing, session management, and state synchronization
HOW (Service Implementation): I use SmartCityRoleBase with Public Works abstractions + direct library injection
"""

import asyncio
import random
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json

# Import our new base class and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    TrafficCopServiceProtocol,
    LoadBalancingRequest, LoadBalancingResponse, LoadBalancingStrategy,
    RateLimitRequest, RateLimitResponse, RateLimitType,
    SessionRequest, SessionResponse, SessionStatus,
    StateSyncRequest, StateSyncResponse, StateSyncStatus,
    APIGatewayRequest, APIGatewayResponse,
    TrafficAnalyticsRequest, TrafficAnalyticsResponse,
    ServiceInstance
)


class TrafficCopService(SmartCityRoleBase, TrafficCopServiceProtocol):
    """
    Traffic Cop Service - Clean Rebuild with Proper Infrastructure
    
    Clean implementation using Public Works abstractions for infrastructure
    and direct library injection for business logic.
    
    WHAT (Smart City Role): I orchestrate API Gateway routing, session management, and state synchronization
    HOW (Service Implementation): I use SmartCityRoleBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any):
        """Initialize Traffic Cop Service with proper infrastructure mapping."""
        super().__init__(
            service_name="TrafficCopService",
            role_name="traffic_cop",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure)
        self.session_abstraction = None
        self.state_management_abstraction = None
        self.messaging_abstraction = None
        self.file_management_abstraction = None
        self.analytics_abstraction = None
        
        # Direct Library Injection (business logic)
        self.fastapi = None  # FastAPI for API routing
        self.websocket = None  # WebSocket for real-time communication
        self.pandas = None  # pandas for traffic analytics
        self.httpx = None  # httpx for health checks
        self.asyncio = asyncio  # asyncio for concurrency
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Traffic Cop specific state
        self.service_instances: Dict[str, List[ServiceInstance]] = {}
        self.load_balancing_counters: Dict[str, int] = {}
        self.rate_limit_counters: Dict[str, Dict[str, Any]] = {}
        self.api_routes: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, Dict[str, Any]] = {}
        
        # Traffic analytics
        self.traffic_metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "active_sessions": 0,
            "state_sync_operations": 0,
            "load_balancing_operations": 0
        }
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Traffic Cop Service initialized")
    
    def _log(self, level: str, message: str):
        """Safe logging method."""
        if hasattr(self, 'logger') and self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
            elif level == "debug":
                self.logger.debug(message)
    
    async def initialize(self) -> bool:
        """Initialize Traffic Cop Service with infrastructure and libraries."""
        try:
            self._log("info", "🚀 Initializing Traffic Cop Service...")
            
            # Initialize infrastructure connections (Public Works)
            self._log("info", "Step 1: Initializing infrastructure connections...")
            await self._initialize_infrastructure_connections()
            self._log("info", "✅ Infrastructure connections initialized")
            
            # Initialize direct library injection
            self._log("info", "Step 2: Initializing direct libraries...")
            await self._initialize_direct_libraries()
            self._log("info", "✅ Direct libraries initialized")
            
            # Initialize Traffic Cop capabilities
            self._log("info", "Step 3: Initializing Traffic Cop capabilities...")
            await self._initialize_traffic_cop_capabilities()
            self._log("info", "✅ Traffic Cop capabilities initialized")
            
            # Initialize SOA API exposure
            self._log("info", "Step 4: Initializing SOA API exposure...")
            await self._initialize_soa_api_exposure()
            self._log("info", "✅ SOA API exposure initialized")
            
            # Initialize MCP tool integration
            self._log("info", "Step 5: Initializing MCP tool integration...")
            await self._initialize_mcp_tool_integration()
            self._log("info", "✅ MCP tool integration initialized")
            
            # Register Traffic Cop capabilities
            self._log("info", "Step 6: Registering Traffic Cop capabilities...")
            await self._register_traffic_cop_capabilities()
            self._log("info", "✅ Traffic Cop capabilities registered")
            
            self._log("info", "✅ Traffic Cop Service initialized successfully")
            return True
            
        except Exception as e:
            self._log("error", f"❌ Failed to initialize Traffic Cop Service: {e}")
            import traceback
            self._log("error", f"Traceback: {traceback.format_exc()}")
            return False
    
    async def _initialize_infrastructure_connections(self):
        """Initialize connections to Public Works abstractions."""
        try:
            self._log("info", "🔌 Connecting to Public Works infrastructure abstractions...")
            
            # Get Public Works Foundation from DI Container
            public_works_foundation = self.di_container.get_foundation_service("PublicWorksFoundationService")
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Initialize infrastructure abstractions
            self.session_abstraction = public_works_foundation.get_session_abstraction()
            self.state_management_abstraction = public_works_foundation.get_state_management_abstraction()
            self.messaging_abstraction = public_works_foundation.get_messaging_abstraction()
            self.file_management_abstraction = public_works_foundation.get_file_management_abstraction()
            self.analytics_abstraction = public_works_foundation.get_analytics_abstraction()
            
            self.is_infrastructure_connected = True
            self._log("info", "✅ Infrastructure connections established")
            
        except Exception as e:
            self._log("error", f"❌ Failed to connect to infrastructure: {e}")
            raise
    
    async def _initialize_direct_libraries(self):
        """Initialize direct library injection for business logic."""
        try:
            self._log("info", "📚 Initializing direct library injection...")
            
            # Get libraries from DI Container
            self.fastapi = self.di_container.get_service("FastAPI")
            self.websocket = self.di_container.get_service("WebSocket")
            self.pandas = self.di_container.get_service("pandas")
            self.httpx = self.di_container.get_service("httpx")
            
            self._log("debug", f"Libraries loaded - FastAPI: {self.fastapi is not None}, WebSocket: {self.websocket is not None}, pandas: {self.pandas is not None}, httpx: {self.httpx is not None}")
            
            # Initialize FastAPI app for API Gateway
            if self.fastapi:
                self.fastapi_app = self.fastapi.FastAPI(
                    title="Traffic Cop API Gateway",
                    description="API Gateway for Smart City Platform",
                    version="1.0.0"
                )
                
                # Add CORS middleware
                self.fastapi_app.add_middleware(
                    self.fastapi.middleware.cors.CORSMiddleware,
                    allow_origins=["*"],
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"]
                )
            
            self.logger.info("✅ Direct libraries initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize direct libraries: {e}")
            raise
    
    async def _initialize_traffic_cop_capabilities(self):
        """Initialize Traffic Cop specific capabilities."""
        try:
            self.logger.info("🚦 Initializing Traffic Cop capabilities...")
            
            # Initialize service registry
            self.service_instances = {}
            self.load_balancing_counters = {}
            
            # Initialize rate limiting
            self.rate_limit_counters = {}
            
            # Initialize API routes
            self.api_routes = {
                "/api/v1/health": {"method": "GET", "service": "health"},
                "/api/v1/sessions": {"method": "POST", "service": "session"},
                "/api/v1/state": {"method": "POST", "service": "state"},
                "/api/v1/analytics": {"method": "GET", "service": "analytics"}
            }
            
            # Initialize WebSocket connections
            self.websocket_connections = {}
            
            self.logger.info("✅ Traffic Cop capabilities initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Traffic Cop capabilities: {e}")
            raise
    
    async def _initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities."""
        try:
            self.logger.info("🌐 Initializing SOA API exposure...")
            
            # Define SOA APIs for Traffic Cop capabilities
            self.soa_apis = {
                "load_balancing": {
                    "endpoint": "/soa/load-balancing",
                    "methods": ["POST"],
                    "description": "Load balancing service selection"
                },
                "rate_limiting": {
                    "endpoint": "/soa/rate-limiting",
                    "methods": ["POST"],
                    "description": "Rate limiting validation"
                },
                "session_management": {
                    "endpoint": "/soa/session-management",
                    "methods": ["POST", "GET", "PUT", "DELETE"],
                    "description": "Session management operations"
                },
                "state_synchronization": {
                    "endpoint": "/soa/state-sync",
                    "methods": ["POST", "GET"],
                    "description": "State synchronization operations"
                },
                "api_gateway": {
                    "endpoint": "/soa/api-gateway",
                    "methods": ["POST"],
                    "description": "API Gateway routing"
                },
                "traffic_analytics": {
                    "endpoint": "/soa/traffic-analytics",
                    "methods": ["GET"],
                    "description": "Traffic analytics and monitoring"
                }
            }
            
            self.logger.info(f"✅ SOA APIs defined: {len(self.soa_apis)} APIs")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize SOA API exposure: {e}")
            raise
    
    async def _initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration."""
        try:
            self.logger.info("🔧 Initializing MCP tool integration...")
            
            # Define MCP tools for Traffic Cop capabilities
            self.mcp_tools = {
                "select_service": {
                    "name": "select_service",
                    "description": "Select service instance using load balancing",
                    "parameters": {
                        "service_name": {"type": "string", "required": True},
                        "strategy": {"type": "string", "required": False}
                    }
                },
                "check_rate_limit": {
                    "name": "check_rate_limit",
                    "description": "Check if request is within rate limits",
                    "parameters": {
                        "user_id": {"type": "string", "required": False},
                        "api_endpoint": {"type": "string", "required": False}
                    }
                },
                "create_session": {
                    "name": "create_session",
                    "description": "Create a new session",
                    "parameters": {
                        "session_id": {"type": "string", "required": True},
                        "user_id": {"type": "string", "required": False}
                    }
                },
                "sync_state": {
                    "name": "sync_state",
                    "description": "Synchronize state between pillars",
                    "parameters": {
                        "key": {"type": "string", "required": True},
                        "source_pillar": {"type": "string", "required": True},
                        "target_pillar": {"type": "string", "required": True}
                    }
                },
                "route_api_request": {
                    "name": "route_api_request",
                    "description": "Route API request to appropriate service",
                    "parameters": {
                        "method": {"type": "string", "required": True},
                        "path": {"type": "string", "required": True}
                    }
                },
                "get_traffic_analytics": {
                    "name": "get_traffic_analytics",
                    "description": "Get traffic analytics data",
                    "parameters": {
                        "time_range": {"type": "string", "required": False}
                    }
                }
            }
            
            self.logger.info(f"✅ MCP tools defined: {len(self.mcp_tools)} tools")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MCP tool integration: {e}")
            raise
    
    async def _register_traffic_cop_capabilities(self):
        """Register Traffic Cop capabilities with Curator."""
        try:
            self.logger.info("📋 Registering Traffic Cop capabilities...")
            
            # Get Curator Foundation
            curator_foundation = self.get_curator_foundation()
            if curator_foundation:
                # Register SOA APIs
                for api_name, api_config in self.soa_apis.items():
                    await curator_foundation.register_soa_api(
                        service_name=self.service_name,
                        api_name=api_name,
                        api_config=api_config
                    )
                
                # Register MCP tools
                for tool_name, tool_config in self.mcp_tools.items():
                    await curator_foundation.register_mcp_tool(
                        service_name=self.service_name,
                        tool_name=tool_name,
                        tool_config=tool_config
                    )
                
                self.logger.info("✅ Traffic Cop capabilities registered with Curator")
            else:
                self.logger.warning("⚠️ Curator Foundation not available, skipping registration")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register Traffic Cop capabilities: {e}")
            raise
    
    # ============================================================================
    # LOAD BALANCING METHODS (Business Logic)
    # ============================================================================
    
    async def select_service(self, request: LoadBalancingRequest) -> LoadBalancingResponse:
        """Select service instance using load balancing strategy."""
        try:
            self.traffic_metrics["load_balancing_operations"] += 1
            
            service_name = request.service_name
            strategy = request.strategy or LoadBalancingStrategy.ROUND_ROBIN
            
            # Get available service instances
            instances = self.service_instances.get(service_name, [])
            if not instances:
                return LoadBalancingResponse(
                    success=False,
                    error="No service instances available",
                    service_name=service_name
                )
            
            # Select instance based on strategy
            selected_instance = await self._select_instance_by_strategy(instances, strategy)
            
            if not selected_instance:
                return LoadBalancingResponse(
                    success=False,
                    error="Failed to select service instance",
                    service_name=service_name
                )
            
            return LoadBalancingResponse(
                success=True,
                service_instance=selected_instance,
                service_name=service_name,
                strategy_used=strategy.value,
                selection_time=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to select service: {e}")
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
        counter = self.load_balancing_counters.get(service_name, 0)
        selected_instance = instances[counter % len(instances)]
        self.load_balancing_counters[service_name] = counter + 1
        
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
            connections = await self.messaging_abstraction.get_data(connection_key) or 0
            
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
            if self.httpx:
                async with self.httpx.AsyncClient() as client:
                    response = await client.get(instance.health_check_url, timeout=5.0)
                    if response.status_code == 200:
                        return 100
                    else:
                        return 0
            
            return 50  # Default health score
            
        except Exception as e:
            self.logger.error(f"Health check failed for {instance.id}: {e}")
            return 0
    
    async def register_service_instance(self, service_name: str, instance: ServiceInstance) -> bool:
        """Register a new service instance."""
        try:
            if service_name not in self.service_instances:
                self.service_instances[service_name] = []
                self.load_balancing_counters[service_name] = 0
            
            self.service_instances[service_name].append(instance)
            
            # Store in Redis via messaging abstraction
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
            await self.messaging_abstraction.store_data(service_key, service_data)
            
            self.logger.info(f"Registered service instance {instance.id} for {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service instance: {e}")
            return False
    
    async def unregister_service_instance(self, service_name: str, instance_id: str) -> bool:
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
                await self.messaging_abstraction.store_data(service_key, service_data)
                
                self.logger.info(f"Unregistered service instance {instance_id} for {service_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to unregister service instance: {e}")
            return False
    
    # ============================================================================
    # RATE LIMITING METHODS (Business Logic)
    # ============================================================================
    
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResponse:
        """Check if request is within rate limits."""
        try:
            # Generate rate limit key
            if request.limit_type == RateLimitType.PER_USER:
                key = f"rate_limit:user:{request.user_id}"
            elif request.limit_type == RateLimitType.PER_API:
                key = f"rate_limit:api:{request.api_endpoint}"
            elif request.limit_type == RateLimitType.PER_IP:
                key = f"rate_limit:ip:{request.ip_address}"
            else:  # GLOBAL
                key = "rate_limit:global"
            
            # Get current count from Redis
            current_count = await self.messaging_abstraction.get_data(key) or 0
            
            # Check limits
            if current_count >= request.requests_per_minute:
                return RateLimitResponse(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=(datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                    limit_type=request.limit_type.value
                )
            
            # Increment counter
            await self.messaging_abstraction.increment_counter(key, 60)  # 60 second TTL
            
            return RateLimitResponse(
                allowed=True,
                remaining_requests=request.requests_per_minute - current_count - 1,
                reset_time=(datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                limit_type=request.limit_type.value
            )
            
        except Exception as e:
            self.logger.error(f"Failed to check rate limit: {e}")
            return RateLimitResponse(
                allowed=True,  # Fail open
                remaining_requests=0,
                error=str(e)
            )
    
    async def reset_rate_limit(self, user_id: str, api_endpoint: Optional[str] = None) -> bool:
        """Reset rate limits for user/API."""
        try:
            if api_endpoint:
                key = f"rate_limit:api:{api_endpoint}"
            else:
                key = f"rate_limit:user:{user_id}"
            
            await self.messaging_abstraction.delete_data(key)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset rate limit: {e}")
            return False
    
    # ============================================================================
    # SESSION MANAGEMENT METHODS (Using Public Works)
    # ============================================================================
    
    async def create_session(self, request: SessionRequest) -> SessionResponse:
        """Create a new session using Public Works session abstraction."""
        try:
            self.traffic_metrics["active_sessions"] += 1
            
            # Use Public Works session abstraction
            session_result = await self.session_abstraction.create_session(
                session_id=request.session_id,
                user_id=request.user_id,
                session_data={
                    "session_type": request.session_type,
                    "context": request.context,
                    "created_at": datetime.utcnow().isoformat(),
                    "ttl_seconds": request.ttl_seconds
                }
            )
            
            if session_result:
                return SessionResponse(
                    success=True,
                    session_id=request.session_id,
                    status=SessionStatus.ACTIVE,
                    expires_at=(datetime.utcnow() + timedelta(seconds=request.ttl_seconds)).isoformat()
                )
            else:
                return SessionResponse(
                    success=False,
                    session_id=request.session_id,
                    status=SessionStatus.INACTIVE,
                    error="Failed to create session"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return SessionResponse(
                success=False,
                session_id=request.session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )
    
    async def get_session(self, session_id: str) -> SessionResponse:
        """Get session information using Public Works session abstraction."""
        try:
            session_data = await self.session_abstraction.get_session(session_id)
            
            if session_data:
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    status=SessionStatus.ACTIVE
                )
            else:
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Session not found"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}")
            return SessionResponse(
                success=False,
                session_id=session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> SessionResponse:
        """Update session data using Public Works session abstraction."""
        try:
            success = await self.session_abstraction.update_session(session_id, updates)
            
            if success:
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    status=SessionStatus.ACTIVE
                )
            else:
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Failed to update session"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to update session: {e}")
            return SessionResponse(
                success=False,
                session_id=session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )
    
    async def destroy_session(self, session_id: str) -> SessionResponse:
        """Destroy a session using Public Works session abstraction."""
        try:
            success = await self.session_abstraction.destroy_session(session_id)
            
            if success:
                self.traffic_metrics["active_sessions"] = max(0, self.traffic_metrics["active_sessions"] - 1)
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE
                )
            else:
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Failed to destroy session"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to destroy session: {e}")
            return SessionResponse(
                success=False,
                session_id=session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )
    
    # ============================================================================
    # STATE SYNCHRONIZATION METHODS (Using Public Works)
    # ============================================================================
    
    async def sync_state(self, request: StateSyncRequest) -> StateSyncResponse:
        """Synchronize state between pillars using Public Works state management abstraction."""
        try:
            self.traffic_metrics["state_sync_operations"] += 1
            
            # Use Public Works state management abstraction
            sync_result = await self.state_management_abstraction.sync_state(
                key=request.key,
                source_pillar=request.source_pillar,
                target_pillar=request.target_pillar,
                state_data=request.state_data,
                sync_type=request.sync_type,
                priority=request.priority
            )
            
            if sync_result:
                sync_id = str(uuid.uuid4())
                return StateSyncResponse(
                    success=True,
                    key=request.key,
                    sync_status=StateSyncStatus.COMPLETED,
                    sync_id=sync_id
                )
            else:
                return StateSyncResponse(
                    success=False,
                    key=request.key,
                    sync_status=StateSyncStatus.FAILED,
                    error="Failed to synchronize state"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to sync state: {e}")
            return StateSyncResponse(
                success=False,
                key=request.key,
                sync_status=StateSyncStatus.FAILED,
                error=str(e)
            )
    
    async def get_state_sync_status(self, sync_id: str) -> StateSyncResponse:
        """Get state synchronization status."""
        try:
            # This would typically check the status from Redis
            # For now, return a mock status
            return StateSyncResponse(
                success=True,
                key="unknown",
                sync_status=StateSyncStatus.COMPLETED,
                sync_id=sync_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get state sync status: {e}")
            return StateSyncResponse(
                success=False,
                key="unknown",
                sync_status=StateSyncStatus.FAILED,
                error=str(e)
            )
    
    # ============================================================================
    # API GATEWAY METHODS (Business Logic)
    # ============================================================================
    
    async def route_api_request(self, request: APIGatewayRequest) -> APIGatewayResponse:
        """Route API request to appropriate service."""
        try:
            self.traffic_metrics["total_requests"] += 1
            start_time = time.time()
            
            # Check rate limits
            rate_limit_request = RateLimitRequest(
                user_id=request.user_id,
                api_endpoint=request.path,
                ip_address=request.headers.get("X-Forwarded-For"),
                limit_type=RateLimitType.PER_USER
            )
            
            rate_limit_response = await self.check_rate_limit(rate_limit_request)
            if not rate_limit_response.allowed:
                return APIGatewayResponse(
                    success=False,
                    status_code=429,
                    error="Rate limit exceeded"
                )
            
            # Find matching route
            route_config = self.api_routes.get(request.path)
            if not route_config:
                return APIGatewayResponse(
                    success=False,
                    status_code=404,
                    error="Route not found"
                )
            
            # Select service instance
            load_balancing_request = LoadBalancingRequest(
                service_name=route_config["service"],
                strategy=LoadBalancingStrategy.ROUND_ROBIN
            )
            
            load_balancing_response = await self.select_service(load_balancing_request)
            if not load_balancing_response.success:
                return APIGatewayResponse(
                    success=False,
                    status_code=503,
                    error="No service instances available"
                )
            
            # Route request to selected service
            processing_time = time.time() - start_time
            
            # Mock response (in real implementation, this would forward the request)
            response_data = {
                "message": "Request processed successfully",
                "service_instance": load_balancing_response.service_instance.id,
                "processing_time": processing_time
            }
            
            self.traffic_metrics["successful_requests"] += 1
            
            return APIGatewayResponse(
                success=True,
                status_code=200,
                body=response_data,
                service_instance=load_balancing_response.service_instance,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to route API request: {e}")
            self.traffic_metrics["failed_requests"] += 1
            
            return APIGatewayResponse(
                success=False,
                status_code=500,
                error=str(e)
            )
    
    async def get_api_routes(self) -> List[Dict[str, Any]]:
        """Get available API routes."""
        return [
            {
                "path": path,
                "method": config["method"],
                "service": config["service"]
            }
            for path, config in self.api_routes.items()
        ]
    
    # ============================================================================
    # TRAFFIC ANALYTICS METHODS (Using pandas for business logic)
    # ============================================================================
    
    async def get_traffic_analytics(self, request: TrafficAnalyticsRequest) -> TrafficAnalyticsResponse:
        """Get traffic analytics data using pandas for analysis."""
        try:
            # Get traffic data from Redis
            analytics_key = f"traffic_analytics:{request.time_range}"
            traffic_data = await self.messaging_abstraction.get_data(analytics_key) or []
            
            # Use pandas for analysis if available
            if self.pandas and traffic_data:
                df = self.pandas.DataFrame(traffic_data)
                
                # Calculate analytics
                analytics_data = {
                    "total_requests": len(df),
                    "unique_users": df["user_id"].nunique() if "user_id" in df.columns else 0,
                    "average_response_time": df["response_time"].mean() if "response_time" in df.columns else 0,
                    "error_rate": (df["status_code"] >= 400).mean() if "status_code" in df.columns else 0,
                    "top_endpoints": df["endpoint"].value_counts().head(10).to_dict() if "endpoint" in df.columns else {},
                    "requests_by_hour": df.groupby(df["timestamp"].dt.hour).size().to_dict() if "timestamp" in df.columns else {}
                }
            else:
                # Fallback to basic metrics
                analytics_data = {
                    "total_requests": self.traffic_metrics["total_requests"],
                    "successful_requests": self.traffic_metrics["successful_requests"],
                    "failed_requests": self.traffic_metrics["failed_requests"],
                    "active_sessions": self.traffic_metrics["active_sessions"],
                    "state_sync_operations": self.traffic_metrics["state_sync_operations"],
                    "load_balancing_operations": self.traffic_metrics["load_balancing_operations"]
                }
            
            return TrafficAnalyticsResponse(
                success=True,
                analytics_data=analytics_data,
                time_range=request.time_range,
                generated_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get traffic analytics: {e}")
            return TrafficAnalyticsResponse(
                success=False,
                error=str(e)
            )
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health information."""
        try:
            instances = self.service_instances.get(service_name, [])
            healthy_instances = []
            
            for instance in instances:
                health_score = await self._check_instance_health(instance)
                if health_score > 50:
                    healthy_instances.append(instance.id)
            
            return {
                "service_name": service_name,
                "total_instances": len(instances),
                "healthy_instances": len(healthy_instances),
                "health_percentage": (len(healthy_instances) / len(instances) * 100) if instances else 0,
                "instances": [
                    {
                        "id": inst.id,
                        "host": inst.host,
                        "port": inst.port,
                        "weight": inst.weight
                    }
                    for inst in instances
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get service health: {e}")
            return {
                "service_name": service_name,
                "error": str(e)
            }
    
    # ============================================================================
    # ORCHESTRATION METHODS
    # ============================================================================
    
    async def orchestrate_api_gateway(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate API Gateway operations."""
        try:
            operation = request.get("operation")
            
            if operation == "route_request":
                api_request = APIGatewayRequest(**request.get("api_request", {}))
                response = await self.route_api_request(api_request)
                return {
                    "success": response.success,
                    "status_code": response.status_code,
                    "body": response.body,
                    "error": response.error
                }
            elif operation == "get_routes":
                routes = await self.get_api_routes()
                return {
                    "success": True,
                    "routes": routes
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate API Gateway: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def orchestrate_session_management(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate session management operations."""
        try:
            operation = request.get("operation")
            
            if operation == "create_session":
                session_request = SessionRequest(**request.get("session_request", {}))
                response = await self.create_session(session_request)
                return {
                    "success": response.success,
                    "session_id": response.session_id,
                    "status": response.status.value,
                    "error": response.error
                }
            elif operation == "get_session":
                session_id = request.get("session_id")
                response = await self.get_session(session_id)
                return {
                    "success": response.success,
                    "session_id": response.session_id,
                    "status": response.status.value,
                    "error": response.error
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate session management: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def orchestrate_state_synchronization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate state synchronization operations."""
        try:
            operation = request.get("operation")
            
            if operation == "sync_state":
                sync_request = StateSyncRequest(**request.get("sync_request", {}))
                response = await self.sync_state(sync_request)
                return {
                    "success": response.success,
                    "key": response.key,
                    "sync_status": response.sync_status.value,
                    "sync_id": response.sync_id,
                    "error": response.error
                }
            elif operation == "get_sync_status":
                sync_id = request.get("sync_id")
                response = await self.get_state_sync_status(sync_id)
                return {
                    "success": response.success,
                    "sync_status": response.sync_status.value,
                    "error": response.error
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate state synchronization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # INFRASTRUCTURE VALIDATION
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that Traffic Cop is using correct infrastructure abstractions."""
        try:
            validation_results = {
                "service_name": self.service_name,
                "infrastructure_connected": self.is_infrastructure_connected,
                "abstractions": {},
                "libraries": {},
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
            # Check Public Works abstractions
            validation_results["abstractions"] = {
                "session_abstraction": self.session_abstraction is not None,
                "state_management_abstraction": self.state_management_abstraction is not None,
                "messaging_abstraction": self.messaging_abstraction is not None,
                "file_management_abstraction": self.file_management_abstraction is not None,
                "analytics_abstraction": self.analytics_abstraction is not None
            }
            
            # Check direct library injection
            validation_results["libraries"] = {
                "fastapi": self.fastapi is not None,
                "websocket": self.websocket is not None,
                "pandas": self.pandas is not None,
                "httpx": self.httpx is not None,
                "asyncio": self.asyncio is not None
            }
            
            # Overall validation
            all_abstractions_connected = all(validation_results["abstractions"].values())
            all_libraries_available = all(validation_results["libraries"].values())
            
            validation_results["overall_success"] = all_abstractions_connected and all_libraries_available
            
            if validation_results["overall_success"]:
                self._log("info", "✅ Traffic Cop infrastructure mapping validation successful")
            else:
                self._log("warning", "⚠️ Traffic Cop infrastructure mapping validation failed")
            
            return validation_results
            
        except Exception as e:
            self._log("error", f"Infrastructure validation failed: {e}")
            return {
                "service_name": self.service_name,
                "overall_success": False,
                "error": str(e),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Traffic Cop service capabilities."""
        return {
            "service_name": self.service_name,
            "role": "traffic_cop",
            "capabilities": {
                "load_balancing": True,
                "rate_limiting": True,
                "session_management": True,
                "state_synchronization": True,
                "api_gateway": True,
                "traffic_analytics": True,
                "websocket_support": True
            },
            "infrastructure_abstractions": [
                "session_abstraction",
                "state_management_abstraction", 
                "messaging_abstraction",
                "file_management_abstraction",
                "analytics_abstraction"
            ],
            "direct_libraries": [
                "fastapi",
                "websocket", 
                "pandas",
                "httpx",
                "asyncio"
            ],
            "soa_apis": list(self.soa_apis.keys()),
            "mcp_tools": list(self.mcp_tools.keys()),
            "traffic_metrics": self.traffic_metrics
        }
