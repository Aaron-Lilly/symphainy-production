#!/usr/bin/env python3
"""
Traffic Cop Service - Multi-Tenant

Comprehensive session and state management service for routing and coordination
with multi-tenant awareness and proper tenant isolation.

WHAT (Smart City Role): I manage session routing and state synchronization across the platform with tenant awareness
HOW (Service Implementation): I use micro-modules for focused session and state operations with tenant isolation
"""

import os
import sys
import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation import CuratorFoundationService
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment

# Import micro-modules
from .micro_modules.session_management import SessionManagementModule, SessionStatus, SessionPriority
from .micro_modules.state_management import StateManagementModule, StatePriority

# Import interfaces (for consumers, not implementers)
from backend.smart_city.interfaces.traffic_cop_interface import (
    ITrafficCop, SessionRequest, SessionResponse, StateRequest, StateResponse,
    RoutingRequest, RoutingResponse, SyncRequest, SyncResponse,
    AnalyticsRequest, AnalyticsResponse, HealthCheckRequest, HealthCheckResponse
)
from bases.soa_service_base import SOAServiceBase, SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from foundations.infrastructure_foundation.abstractions.redis_streams_abstraction import RedisStreamsAbstraction


class TrafficCopService(SOAServiceBase):
    """
    Traffic Cop Service - Multi-Tenant

    Comprehensive session and state management service for routing and coordination
    with multi-tenant awareness and proper tenant isolation.
    
    WHAT (Smart City Role): I manage session routing and state synchronization across the platform with tenant awareness
    HOW (Service Implementation): I use micro-modules for focused session and state operations with tenant isolation
    """

    def __init__(self, utility_foundation, curator_foundation=None, public_works_foundation=None):
        """Initialize Traffic Cop Service with multi-tenant capabilities."""
        super().__init__("TrafficCopService", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.env_loader = EnvironmentLoader()

        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # Initialize SOA protocol
        self.soa_protocol = TrafficCopSOAProtocol("TrafficCopService", self, curator_foundation), public_works_foundation

        # Initialize Redis Streams abstraction
        self.redis_streams_abstraction = RedisStreamsAbstraction(
            host="localhost",
            port=6379,
            password=None,
            graph_name="traffic_cop"
        )

        # Initialize micro-modules
        self.session_management_module = SessionManagementModule(
            logger=self.logger,
            env_loader=self.env_loader,
            redis_streams_abstraction=self.redis_streams_abstraction
        )
        self.state_management_module = StateManagementModule(
            logger=self.logger,
            env_loader=self.env_loader,
            redis_streams_abstraction=self.redis_streams_abstraction
        )

        # Service capabilities
        self.capabilities = [
            "session_management",
            "state_management",
            "routing",
            "synchronization",
            "multi_tenant_session_management"
        ]

        self.logger.info("🚦 Traffic Cop Service initialized - Multi-Tenant Session & State Hub")

    async def initialize(self):
        """Initialize the Traffic Cop service with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Traffic Cop Service with multi-tenant capabilities...")

            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")

            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions from public works
            if self.public_works_foundation:
                await self.soa_protocol.load_smart_city_abstractions()
            self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions")
            
            # Initialize micro-modules
            await self.session_management_module.initialize()
            await self.state_management_module.initialize()

            # Initialize infrastructure abstractions
            await self._initialize_infrastructure_abstractions()

            self.logger.info("✅ Traffic Cop Service initialized with multi-tenant capabilities")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="traffic_cop_initialize")
            raise

        except Exception as e:
            await self.error_handler.handle_error(e, context="traffic_cop_service_initialization")
            self.service_health = "unhealthy"
            raise

    async def _initialize_infrastructure_abstractions(self):
        """Initialize infrastructure abstractions."""
        try:
            # Test Redis Streams connection
            connection_result = await self.redis_streams_abstraction.connect()
            if not connection_result:
                raise ValueError("Redis Streams connection failed")
            
            self.logger.info("✅ Redis Streams initialized for Traffic Cop Service")

            self.logger.info("✅ Infrastructure abstractions initialized successfully")
        except Exception as e:
            await self.error_handler.handle_error(e, context="traffic_cop_infrastructure_initialization")
            raise

    # ITrafficCop Interface Implementation
    async def create_session(self, request: SessionRequest, user_context: Optional[UserContext] = None) -> SessionResponse:
        """Create a new session and route it to appropriate pillars with tenant awareness."""
        try:
            # Validate tenant access
            if user_context and self.multi_tenant_coordinator:
                tenant_validation = await self.multi_tenant_coordinator.validate_tenant_feature_access(
                    user_context.tenant_id, "session_creation"
                )
                if not tenant_validation.get("allowed", False):
                    return SessionResponse(
                        success=False, 
                        message="Insufficient tenant permissions for session creation"
                    )
            
            # Add tenant context to session metadata
            session_metadata = request.metadata or {}
            if user_context and user_context.tenant_id:
                session_metadata["tenant_id"] = user_context.tenant_id
                session_metadata["created_by"] = user_context.user_id
            
            result = await self.session_management_module.create_session(
                user_id=request.user_id,
                initial_pillar=request.initial_pillar,
                priority=SessionPriority(request.priority) if request.priority else SessionPriority.NORMAL,
                metadata=session_metadata
            )
            
            if result["success"]:
                # Record telemetry with tenant context
                await self.telemetry_service.record_metric(
                    "session_created", 1,
                    {
                        "user_id": request.user_id,
                        "tenant_id": user_context.tenant_id if user_context else "system",
                        "pillar": request.initial_pillar
                    }
                )
                
                # Audit the action
                if user_context:
                    await self.security_service.audit_user_action(
                        user_context, "create_session", "traffic_cop",
                        {
                            "session_id": result["session_id"],
                            "initial_pillar": request.initial_pillar,
                            "priority": request.priority
                        }
                    )
                
                return SessionResponse(
                    success=True,
                    session_id=result["session_id"],
                    session_data=result["session_data"],
                    message=result["message"]
                )
            return SessionResponse(success=False, message=result["error"])
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="traffic_cop_create_session")
            return SessionResponse(success=False, message=f"Session creation failed: {str(e)}")

    async def route_session(self, request: RoutingRequest) -> RoutingResponse:
        """Route a session to a specific pillar."""
        result = await self.session_management_module.route_session_to_pillar(
            session_id=request.session_id,
            pillar_name=request.pillar_name,
            context=request.context
        )
        
        if result["success"]:
            return RoutingResponse(
                success=True,
                session_id=result["session_id"],
                pillar=result["pillar"],
                message=result["message"]
            )
        return RoutingResponse(success=False, message=result["error"])

    async def get_session_status(self, session_id: str) -> SessionResponse:
        """Get the current status of a session."""
        result = await self.session_management_module.get_session_status(session_id)
        
        if result["success"]:
            return SessionResponse(
                success=True,
                session_id=result["session_id"],
                session_data=result,
                message=result["message"]
            )
        return SessionResponse(success=False, message=result["error"])

    async def terminate_session(self, session_id: str, reason: str = "user_request") -> SessionResponse:
        """Terminate a session."""
        result = await self.session_management_module.terminate_session(session_id, reason)
        
        if result["success"]:
            return SessionResponse(
                success=True,
                session_id=result["session_id"],
                message=result["message"]
            )
        return SessionResponse(success=False, message=result["error"])

    async def set_state(self, request: StateRequest) -> StateResponse:
        """Set state for a key, optionally scoped to a pillar."""
        result = await self.state_management_module.set_state(
            key=request.key,
            value=request.value,
            pillar_name=request.pillar_name,
            priority=StatePriority(request.priority) if request.priority else StatePriority.NORMAL,
            ttl_seconds=request.ttl_seconds
        )
        
        if result["success"]:
            return StateResponse(
                success=True,
                key=result["key"],
                state_id=result["state_id"],
                message=result["message"]
            )
        return StateResponse(success=False, message=result["error"])

    async def get_state(self, key: str, pillar_name: str = None, user_context: Optional[UserContext] = None) -> StateResponse:
        """Get state for a key, optionally scoped to a pillar with tenant awareness."""
        try:
            # Validate tenant access to state
            if user_context and self.multi_tenant_coordinator:
                # Check if the state key belongs to the tenant
                tenant_validation = await self.multi_tenant_coordinator.validate_tenant_feature_access(
                    user_context.tenant_id, "state_access"
                )
                if not tenant_validation.get("allowed", False):
                    return StateResponse(
                        success=False, 
                        message="Insufficient tenant permissions for state access"
                    )
            
            result = await self.state_management_module.get_state(key, pillar_name)
            
            if result["success"]:
                # Record telemetry for state retrieval with tenant context
                await self.telemetry_service.record_metric(
                    "state_retrieval_count", 1,
                    {
                        "key": key, 
                        "pillar": pillar_name or "global",
                        "tenant_id": user_context.tenant_id if user_context else "system"
                    }
                )
                
                # Audit the action
                if user_context:
                    await self.security_service.audit_user_action(
                        user_context, "get_state", "traffic_cop",
                        {
                            "key": key,
                            "pillar": pillar_name or "global",
                            "state_id": result.get("state_id")
                        }
                    )
                
                return StateResponse(
                    success=True,
                    key=result["key"],
                    value=result["value"],
                    pillar=result["pillar"],
                    state_id=result["state_id"],
                    updated_at=result["updated_at"],
                    message="State retrieved successfully"
                )
            return StateResponse(success=False, message=result["error"])
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="traffic_cop_get_state")
            return StateResponse(success=False, message=f"State retrieval failed: {str(e)}")

    async def sync_state(self, request: SyncRequest) -> SyncResponse:
        """Synchronize state between pillars."""
        result = await self.state_management_module.sync_state(
            source_pillar=request.source_pillar,
            target_pillar=request.target_pillar,
            keys=request.keys
        )
        
        if result["success"]:
            return SyncResponse(
                success=True,
                source_pillar=result["source_pillar"],
                target_pillar=result["target_pillar"],
                synced_count=result["synced_count"],
                conflicts=result["conflicts"],
                message=result["message"]
            )
        return SyncResponse(success=False, message=result["error"])

    async def get_analytics(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """Get analytics for sessions or state management."""
        if request.analytics_type == "session":
            result = await self.session_management_module.get_session_analytics(request.session_id)
            if result["success"]:
                return AnalyticsResponse(
                    success=True,
                    analytics_type="session",
                    data=result["analytics"],
                    message=result["message"]
                )
        elif request.analytics_type == "state":
            result = await self.state_management_module.get_state_analytics(request.pillar_name)
            if result["success"]:
                return AnalyticsResponse(
                    success=True,
                    analytics_type="state",
                    data=result["analytics"],
                    message=result["message"]
                )
        
        return AnalyticsResponse(success=False, message="Invalid analytics type or request failed")

    async def health_check(self, request: HealthCheckRequest) -> HealthCheckResponse:
        """Perform health check on the Traffic Cop service."""
        try:
            # Check Redis Streams connection
            redis_healthy = await self.redis_streams_abstraction.connect()
            
            # Check micro-modules
            session_healthy = self.session_management_module is not None
            state_healthy = self.state_management_module is not None
            
            overall_health = redis_healthy and session_healthy and state_healthy
            
            return HealthCheckResponse(
                success=overall_health,
                service_name="traffic_cop",
                status="healthy" if overall_health else "unhealthy",
                details={
                    "redis_streams": "healthy" if redis_healthy else "unhealthy",
                    "session_management": "healthy" if session_healthy else "unhealthy",
                    "state_management": "healthy" if state_healthy else "unhealthy"
                },
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            await self.error_handler.handle_error(e, context="traffic_cop_health_check")
            return HealthCheckResponse(
                success=False,
                service_name="traffic_cop",
                status="unhealthy",
                details={"error": str(e)},
                timestamp=datetime.utcnow().isoformat()
            )

    # Additional Traffic Cop specific methods
    async def get_session_events(self, session_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get events for a specific session."""
        return await self.session_management_module.get_session_events(session_id, limit)

    async def update_session_state(self, session_id: str, pillar_name: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update session state for a specific pillar."""
        return await self.session_management_module.update_session_state(session_id, pillar_name, state_data)

    async def resolve_state_conflict(self, key: str, resolution_strategy: str = "source_wins", custom_value: Any = None) -> Dict[str, Any]:
        """Resolve a state conflict using a specified strategy."""
        return await self.state_management_module.resolve_state_conflict(key, resolution_strategy, custom_value)

    async def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions."""
        return list(self.session_management_module.active_sessions.values())

    async def get_pillar_states(self, pillar_name: str) -> Dict[str, Any]:
        """Get all states for a specific pillar."""
        return dict(self.state_management_module.pillar_states.get(pillar_name, {}))

    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """Clean up expired sessions."""
        try:
            cleaned_count = 0
            current_time = datetime.utcnow()
            
            for session_id, session_data in list(self.session_management_module.active_sessions.items()):
                # Check if session is expired (simple TTL check)
                created_at = datetime.fromisoformat(session_data["created_at"])
                if (current_time - created_at).total_seconds() > 3600:  # 1 hour default TTL
                    await self.terminate_session(session_id, "expired")
                    cleaned_count += 1

            return {
                "success": True,
                "cleaned_count": cleaned_count,
                "message": f"Cleaned up {cleaned_count} expired sessions"
            }
        except Exception as e:
            await self.error_handler.handle_error(e, context="traffic_cop_cleanup_sessions")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC METHODS
    # ============================================================================
    
    async def get_tenant_sessions(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get all sessions for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's sessions"}
            
            # Get all sessions and filter by tenant
            all_sessions = await self.get_all_sessions()
            tenant_sessions = [
                session for session in all_sessions 
                if session.get("metadata", {}).get("tenant_id") == tenant_id
            ]
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_sessions", "traffic_cop",
                    {"tenant_id": tenant_id, "session_count": len(tenant_sessions)}
                )
            
            return {"success": True, "sessions": tenant_sessions, "count": len(tenant_sessions)}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_sessions")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_session_metrics(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get session metrics for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's session metrics"}
            
            # Get tenant sessions
            tenant_sessions = await self.get_tenant_sessions(tenant_id, user_context)
            if not tenant_sessions.get("success"):
                return tenant_sessions
            
            sessions = tenant_sessions.get("sessions", [])
            
            # Calculate session metrics
            session_metrics = {
                "tenant_id": tenant_id,
                "total_sessions": len(sessions),
                "active_sessions": len([s for s in sessions if s.get("status") == "active"]),
                "completed_sessions": len([s for s in sessions if s.get("status") == "completed"]),
                "failed_sessions": len([s for s in sessions if s.get("status") == "failed"]),
                "average_session_duration": self._calculate_average_session_duration(sessions),
                "pillar_distribution": self._calculate_pillar_distribution(sessions)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_session_metrics", "traffic_cop",
                    {"tenant_id": tenant_id, "total_sessions": session_metrics["total_sessions"]}
                )
            
            return {"success": True, "session_metrics": session_metrics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_session_metrics")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_state_summary(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get state summary for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's state summary"}
            
            # Get all pillar states and filter by tenant
            all_pillars = ["experience", "business", "data", "infrastructure"]
            tenant_states = {}
            
            for pillar in all_pillars:
                pillar_states = await self.get_pillar_states(pillar)
                # Filter states that belong to the tenant (assuming tenant_id is in state keys or metadata)
                tenant_pillar_states = {
                    key: value for key, value in pillar_states.items()
                    if self._state_belongs_to_tenant(key, value, tenant_id)
                }
                if tenant_pillar_states:
                    tenant_states[pillar] = tenant_pillar_states
            
            state_summary = {
                "tenant_id": tenant_id,
                "total_states": sum(len(states) for states in tenant_states.values()),
                "pillar_distribution": {pillar: len(states) for pillar, states in tenant_states.items()},
                "state_types": self._categorize_state_types(tenant_states)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_state_summary", "traffic_cop",
                    {"tenant_id": tenant_id, "total_states": state_summary["total_states"]}
                )
            
            return {"success": True, "state_summary": state_summary}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_state_summary")
            return {"success": False, "error": str(e)}
    
    def _calculate_average_session_duration(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate average session duration in minutes."""
        if not sessions:
            return 0.0
        
        durations = []
        for session in sessions:
            if session.get("start_time") and session.get("end_time"):
                start = datetime.fromisoformat(session["start_time"].replace('Z', '+00:00'))
                end = datetime.fromisoformat(session["end_time"].replace('Z', '+00:00'))
                duration = (end - start).total_seconds() / 60  # Convert to minutes
                durations.append(duration)
        
        return round(sum(durations) / len(durations), 2) if durations else 0.0
    
    def _calculate_pillar_distribution(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of sessions across pillars."""
        pillar_counts = {}
        for session in sessions:
            pillar = session.get("current_pillar", "unknown")
            pillar_counts[pillar] = pillar_counts.get(pillar, 0) + 1
        return pillar_counts
    
    def _state_belongs_to_tenant(self, key: str, value: Any, tenant_id: str) -> bool:
        """Check if a state belongs to a specific tenant."""
        # This is a simplified check - in a real implementation, you'd check metadata
        # For now, we'll assume tenant_id is part of the key or value metadata
        if isinstance(value, dict) and value.get("tenant_id") == tenant_id:
            return True
        if tenant_id in key:
            return True
        return False
    
    def _categorize_state_types(self, tenant_states: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """Categorize state types for the tenant."""
        type_counts = {}
        for pillar, states in tenant_states.items():
            for key, value in states.items():
                # Simple categorization based on key patterns
                if "config" in key.lower():
                    type_counts["configuration"] = type_counts.get("configuration", 0) + 1
                elif "user" in key.lower():
                    type_counts["user_data"] = type_counts.get("user_data", 0) + 1
                elif "session" in key.lower():
                    type_counts["session_data"] = type_counts.get("session_data", 0) + 1
                else:
                    type_counts["other"] = type_counts.get("other", 0) + 1
        return type_counts


class TrafficCopSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for Traffic Cop Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize Traffic Cop SOA Protocol."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="TrafficCopService",
            version="1.0.0",
            description="Traffic Cop Service - Multi-tenant session and state management",
            interface_name="ITrafficCop",
            endpoints=self._create_all_endpoints(),
            tags=["session-management", "state-management", "multi-tenant", "routing"],
            contact={"email": "trafficcop@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/traffic-cop", "description": "Traffic Cop Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for Traffic Cop Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # Traffic Cop specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/sessions",
                method="POST",
                summary="Create Session",
                description="Create a new session with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "session_type": {"type": "string"},
                        "metadata": {"type": "object"},
                        "duration_hours": {"type": "integer"}
                    },
                    "required": ["session_type"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Sessions", "Management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/sessions/{session_id}",
                method="GET",
                summary="Get Session",
                description="Get session information",
                parameters=[
                    {
                        "name": "session_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Session ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "status": {"type": "string"},
                        "metadata": {"type": "object"}
                    }
                }),
                tags=["Sessions", "Information"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/state",
                method="POST",
                summary="Set State",
                description="Set state with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "object"},
                        "pillar": {"type": "string"}
                    },
                    "required": ["key", "value", "pillar"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["State", "Management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/state/{key}",
                method="GET",
                summary="Get State",
                description="Get state by key with tenant awareness",
                parameters=[
                    {
                        "name": "key",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "State key"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "object"}
                    }
                }),
                tags=["State", "Information"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/state-summary",
                method="GET",
                summary="Get Tenant State Summary",
                description="Get state summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_states": {"type": "integer"},
                        "pillar_counts": {"type": "object"}
                    }
                }),
                tags=["Tenant", "State"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths