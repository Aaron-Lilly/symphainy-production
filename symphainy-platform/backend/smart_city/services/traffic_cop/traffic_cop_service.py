#!/usr/bin/env python3
"""
Traffic Cop Service - Micro-Modular Refactored

Clean micro-modular implementation using dynamic module loading via mixin.
Uses Public Works abstractions for infrastructure and direct library injection for business logic.

WHAT (Smart City Role): I orchestrate API Gateway routing, session management, and state synchronization
HOW (Service Implementation): I use SmartCityRoleBase with micro-modules loaded dynamically
"""

import asyncio
from typing import Dict, Any, List, Optional

# Import our new base class and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    TrafficCopServiceProtocol,
    LoadBalancingRequest, LoadBalancingResponse,
    RateLimitRequest, RateLimitResponse,
    SessionRequest, SessionResponse,
    StateSyncRequest, StateSyncResponse,
    APIGatewayRequest, APIGatewayResponse,
    TrafficAnalyticsRequest, TrafficAnalyticsResponse
)


class TrafficCopService(SmartCityRoleBase, TrafficCopServiceProtocol):
    """
    Traffic Cop Service - Micro-Modular Refactored
    
    Clean implementation using micro-modules loaded dynamically via mixin.
    Uses Public Works abstractions for infrastructure and direct library injection for business logic.
    
    WHAT (Smart City Role): I orchestrate API Gateway routing, session management, and state synchronization
    HOW (Service Implementation): I use SmartCityRoleBase with micro-modules loaded dynamically
    """
    
    def __init__(self, di_container: Any):
        """Initialize Traffic Cop Service with micro-module support."""
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
        self.fastapi = None
        self.websocket = None
        self.pandas = None
        self.httpx = None
        self.asyncio = asyncio
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Traffic Cop specific state
        self.service_instances: Dict[str, List[Any]] = {}
        self.load_balancing_counters: Dict[str, int] = {}
        self.rate_limit_counters: Dict[str, Dict[str, Any]] = {}
        self.api_routes: Dict[str, Dict[str, Any]] = {}
        # WebSocket connections now stored in Redis via connection_registry (removed in-memory dict for horizontal scaling)
        self.websocket_connection_registry = None
        
        # Traffic analytics
        self.traffic_metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "active_sessions": 0,
            "state_sync_operations": 0,
            "load_balancing_operations": 0
        }
        
        # Micro-modules (loaded dynamically via mixin)
        self.initialization_module = None
        self.load_balancing_module = None
        self.rate_limiting_module = None
        self.session_management_module = None
        self.state_sync_module = None
        self.api_routing_module = None
        self.analytics_module = None
        self.orchestration_module = None
        self.soa_mcp_module = None
        self.utilities_module = None
        
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
        """Initialize Traffic Cop Service with lazy-loaded modules."""
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "traffic_cop_initialize_start",
            success=True
        )
        
        try:
            # Load initialization module
            self.initialization_module = self.get_module("initialization")
            if not self.initialization_module:
                raise Exception("Failed to load initialization module")
            
            # Initialize infrastructure and libraries
            await self.initialization_module.initialize_infrastructure()
            await self.initialization_module.initialize_direct_libraries()
            await self.initialization_module.initialize_capabilities()
            
            # Load other modules
            self.load_balancing_module = self.get_module("load_balancing")
            self.rate_limiting_module = self.get_module("rate_limiting")
            self.session_management_module = self.get_module("session_management")
            self.websocket_session_management_module = self.get_module("websocket_session_management")
            self.state_sync_module = self.get_module("state_sync")
            self.api_routing_module = self.get_module("api_routing")
            self.analytics_module = self.get_module("analytics")
            self.orchestration_module = self.get_module("orchestration")
            self.soa_mcp_module = self.get_module("soa_mcp")
            self.utilities_module = self.get_module("utilities")
            
            if not all([self.load_balancing_module, self.rate_limiting_module,
                       self.session_management_module, self.state_sync_module,
                       self.api_routing_module, self.analytics_module,
                       self.orchestration_module, self.soa_mcp_module, self.utilities_module]):
                raise Exception("Failed to load required modules")
            
            # WebSocket session management is optional (only needed if WebSocket support is enabled)
            if not self.websocket_session_management_module:
                self.logger.warning("⚠️ WebSocket session management module not available (WebSocket features may be limited)")
            
            # Initialize SOA/MCP
            await self.soa_mcp_module.initialize_soa_api_exposure()
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register capabilities
            # Register capabilities with curator (Phase 2 pattern - simplified for Smart City)
            await self.soa_mcp_module.register_capabilities()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric(
                "traffic_cop_initialized",
                1.0,
                {"service": "TrafficCopService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "traffic_cop_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e,
                "traffic_cop_initialize",
                {
                    "service": "TrafficCopService",
                    "error_type": type(e).__name__
                }
            )
            
            self.service_health = "unhealthy"
            
            # Log failure
            await self.log_operation_with_telemetry(
                "traffic_cop_initialize_complete",
                success=False,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Record health metric
            await self.record_health_metric(
                "traffic_cop_initialized",
                0.0,
                metadata={"error_type": type(e).__name__}
            )
            
            return False
    
    # ============================================================================
    # LOAD BALANCING METHODS - Delegate to load_balancing module
    # ============================================================================
    
    async def select_service(self, request: LoadBalancingRequest, user_context: Optional[Dict[str, Any]] = None) -> LoadBalancingResponse:
        """Select service instance using load balancing strategy."""
        # Service-level method delegates to module (module handles utilities)
        return await self.load_balancing_module.select_service(request, user_context)
    
    async def register_service_instance(self, service_name: str, instance: Any, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new service instance."""
        # Service-level method delegates to module (module handles utilities)
        return await self.load_balancing_module.register_service_instance(service_name, instance, user_context)
    
    async def unregister_service_instance(self, service_name: str, instance_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Unregister a service instance."""
        # Service-level method delegates to module (module handles utilities)
        return await self.load_balancing_module.unregister_service_instance(service_name, instance_id, user_context)
    
    # ============================================================================
    # RATE LIMITING METHODS - Delegate to rate_limiting module
    # ============================================================================
    
    async def check_rate_limit(self, request: RateLimitRequest, user_context: Optional[Dict[str, Any]] = None) -> RateLimitResponse:
        """Check if request is within rate limits."""
        # Service-level method delegates to module (module handles utilities)
        return await self.rate_limiting_module.check_rate_limit(request, user_context)
    
    async def reset_rate_limit(self, user_id: str, api_endpoint: Optional[str] = None, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Reset rate limits for user/API."""
        # Service-level method delegates to module (module handles utilities)
        return await self.rate_limiting_module.reset_rate_limit(user_id, api_endpoint, user_context)
    
    # ============================================================================
    # SESSION MANAGEMENT METHODS - Delegate to session_management module
    # ============================================================================
    
    async def create_session(self, request: SessionRequest, user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Create a new session using Public Works session abstraction."""
        # Service-level method delegates to module (module handles utilities)
        return await self.session_management_module.create_session(request, user_context)
    
    async def get_session(self, session_id: str, user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Get session information using Public Works session abstraction."""
        # Service-level method delegates to module (module handles utilities)
        return await self.session_management_module.get_session(session_id, user_context)
    
    async def update_session(self, session_id: str, updates: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Update session data using Public Works session abstraction."""
        # Service-level method delegates to module (module handles utilities)
        return await self.session_management_module.update_session(session_id, updates, user_context)
    
    async def destroy_session(self, session_id: str, user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Destroy a session using Public Works session abstraction."""
        # Service-level method delegates to module (module handles utilities)
        return await self.session_management_module.destroy_session(session_id, user_context)
    
    # ============================================================================
    # STATE SYNCHRONIZATION METHODS - Delegate to state_sync module
    # ============================================================================
    
    async def sync_state(self, request: StateSyncRequest, user_context: Optional[Dict[str, Any]] = None) -> StateSyncResponse:
        """Synchronize state between pillars using Public Works state management abstraction."""
        # Service-level method delegates to module (module handles utilities)
        return await self.state_sync_module.sync_state(request, user_context)
    
    async def get_state_sync_status(self, sync_id: str, user_context: Optional[Dict[str, Any]] = None) -> StateSyncResponse:
        """Get state synchronization status."""
        # Service-level method delegates to module (module handles utilities)
        return await self.state_sync_module.get_state_sync_status(sync_id)
    
    # ============================================================================
    # API GATEWAY METHODS - Delegate to api_routing module
    # ============================================================================
    
    async def route_api_request(self, request: APIGatewayRequest, user_context: Optional[Dict[str, Any]] = None) -> APIGatewayResponse:
        """Route API request to appropriate service."""
        # Service-level method delegates to module (module handles utilities)
        return await self.api_routing_module.route_api_request(request, user_context)
    
    async def get_api_routes(self) -> List[Dict[str, Any]]:
        """Get available API routes."""
        return await self.api_routing_module.get_api_routes()
    
    # ============================================================================
    # TRAFFIC ANALYTICS METHODS - Delegate to analytics module
    # ============================================================================
    
    async def get_traffic_analytics(self, request: TrafficAnalyticsRequest, user_context: Optional[Dict[str, Any]] = None) -> TrafficAnalyticsResponse:
        """Get traffic analytics data using pandas for analysis."""
        # Service-level method delegates to module (module handles utilities)
        return await self.analytics_module.get_traffic_analytics(request, user_context)
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health information."""
        return await self.analytics_module.get_service_health(service_name)
    
    # ============================================================================
    # ORCHESTRATION METHODS - Delegate to orchestration module
    # ============================================================================
    
    async def orchestrate_api_gateway(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate API Gateway operations."""
        return await self.orchestration_module.orchestrate_api_gateway(request)
    
    async def orchestrate_session_management(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate session management operations."""
        return await self.orchestration_module.orchestrate_session_management(request)
    
    async def orchestrate_state_synchronization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate state synchronization operations."""
        return await self.orchestration_module.orchestrate_state_synchronization(request)
    
    # ============================================================================
    # UTILITY METHODS - Delegate to utilities module
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that Traffic Cop is using correct infrastructure abstractions."""
        return await self.utilities_module.validate_infrastructure_mapping()
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Traffic Cop service capabilities."""
        return await self.utilities_module.get_service_capabilities()
