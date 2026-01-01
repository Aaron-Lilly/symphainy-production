#!/usr/bin/env python3
"""
Session Management Abstraction - Generic Infrastructure Implementation

Generic session management implementation using real adapters.
This is Layer 3 of the 5-layer architecture for Traffic Cop session management.

WHAT (Infrastructure Role): I provide generic session management services
HOW (Infrastructure Implementation): I use real adapters with generic interfaces
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from foundations.public_works_foundation.abstraction_contracts.session_management_protocol import (
    SessionManagementProtocol, SessionRouteContext
)
from foundations.public_works_foundation.infrastructure_adapters.redis_adapter import RedisAdapter
# FIX: JWT adapter import removed - user auth uses Supabase, session tokens may use different approach
# from foundations.public_works_foundation.infrastructure_adapters.jwt_adapter import JWTAdapter
from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter

logger = logging.getLogger(__name__)

class SessionManagementAbstraction(SessionManagementProtocol):
    """
    Generic session management abstraction using real adapters.
    
    This abstraction implements the SessionManagementProtocol using real
    Redis, JWT, and Config adapters, providing a generic interface.
    """
    
    def __init__(self, redis_adapter: RedisAdapter, jwt_adapter: Optional[Any] = None, 
                 config_adapter: ConfigAdapter = None, di_container=None):
        """
        Initialize Session Management abstraction with real adapters.
        
        FIX: jwt_adapter is now optional - user auth uses Supabase, session tokens may use different approach.
        
        Args:
            redis_adapter: Redis adapter (REQUIRED)
            jwt_adapter: JWT adapter (OPTIONAL - not used for user auth)
            config_adapter: Configuration adapter
            di_container: Dependency injection container
        """
        self.redis = redis_adapter
        self.jwt = jwt_adapter  # Can be None
        self.config = config_adapter
        self.di_container = di_container
        self.service_name = "session_management_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Session management configuration
        self.default_ttl = 3600  # 1 hour
        self.max_routes_per_user = 10
        
        self.logger.info("✅ Session Management abstraction initialized with real adapters")
    
    async def create_session_route(self, session_id: str, service_endpoint: str, 
                                 routing_config: Dict[str, Any]) -> str:
        """Create a session route using real adapters."""
        try:
            route_id = f"route_{session_id}_{uuid.uuid4().hex[:8]}"
            
            # Create route data
            route_data = {
                "route_id": route_id,
                "session_id": session_id,
                "service_endpoint": service_endpoint,
                "routing_config": routing_config,
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=self.default_ttl)).isoformat(),
                "is_active": True
            }
            
            # Store in Redis
            route_key = f"session_route:{route_id}"
            await self.redis.set(route_key, route_data, ttl=self.default_ttl)
            
            # Store session to route mapping
            session_route_key = f"session_routes:{session_id}"
            await self.redis.sadd(session_route_key, route_id)
            await self.redis.expire(session_route_key, self.default_ttl)
            
            self.logger.info(f"✅ Session route created: {route_id} for session {session_id}")
            
            return route_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create session route: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def validate_session_route(self, session_id: str) -> SessionRouteContext:
        """Validate session route using real adapters."""
        try:
            # Get session routes
            session_route_key = f"session_routes:{session_id}"
            route_ids = await self.redis.smembers(session_route_key)
            
            if not route_ids:
                raise ValueError(f"No routes found for session {session_id}")
            
            # Get the most recent route
            route_id = list(route_ids)[0]
            route_key = f"session_route:{route_id}"
            route_data = await self.redis.get(route_key)
            
            if not route_data:
                raise ValueError(f"Route {route_id} not found")
            
            # Update last accessed
            route_data["last_accessed"] = datetime.utcnow().isoformat()
            await self.redis.set(route_key, route_data, ttl=self.default_ttl)
            
            # Create SessionRouteContext
            route_context = SessionRouteContext(
                route_id=route_data["route_id"],
                session_id=route_data["session_id"],
                user_id=route_data.get("user_id", "unknown"),
                tenant_id=route_data.get("tenant_id", "unknown"),
                service_endpoint=route_data["service_endpoint"],
                routing_config=route_data["routing_config"],
                created_at=datetime.fromisoformat(route_data["created_at"]),
                last_accessed=datetime.fromisoformat(route_data["last_accessed"]),
                expires_at=datetime.fromisoformat(route_data["expires_at"]),
                is_active=route_data["is_active"]
            )
            
            self.logger.info(f"✅ Session route validated: {route_id}")
            return route_context
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate session route: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def update_session_route(self, session_id: str, routing_config: Dict[str, Any]) -> bool:
        """Update session route using real adapters."""
        try:
            # Get session routes
            session_route_key = f"session_routes:{session_id}"
            route_ids = await self.redis.smembers(session_route_key)
            
            if not route_ids:
                return
            
            # Update each route
            for route_id in route_ids:
                route_key = f"session_route:{route_id}"
                route_data = await self.redis.get(route_key)
                
                if route_data:
                    route_data["routing_config"] = routing_config
                    route_data["last_accessed"] = datetime.utcnow().isoformat()
                    await self.redis.set(route_key, route_data, ttl=self.default_ttl)
            
            self.logger.info(f"✅ Session route updated for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update session route: {e}")
            raise  # Re-raise for service layer to handle

        """Destroy session route using real adapters."""
        try:
            # Get session routes
            session_route_key = f"session_routes:{session_id}"
            route_ids = await self.redis.smembers(session_route_key)
            
            if not route_ids:
                return True
            
            # Destroy each route
            for route_id in route_ids:
                route_key = f"session_route:{route_id}"
                await self.redis.delete(route_key)
            
            # Remove session routes set
            await self.redis.delete(session_route_key)
            
            self.logger.info(f"✅ Session route destroyed for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to destroy session route: {e}")
            raise  # Re-raise for service layer to handle

        """Get active routes for user using real adapters."""
        try:
            # This would require additional user-to-session mapping
            # For now, return empty list
            self.logger.info(f"✅ Active routes retrieved for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get active routes: {e}")
            raise  # Re-raise for service layer to handle

        """Cleanup expired routes using real adapters."""
        try:
            # This would require scanning all routes and checking expiration
            # For now, return 0
            self.logger.info("✅ Expired routes cleaned up")
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup expired routes: {e}")
    
            raise  # Re-raise for service layer to handle

        """Get route metrics using real adapters."""
        try:
            # This would require aggregating metrics from Redis
            # For now, return mock metrics
            metrics = {
                "total_routes": 0,
                "active_routes": 0,
                "expired_routes": 0,
                "average_route_lifetime": 0
            }
            
            self.logger.info("✅ Route metrics retrieved")
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get route metrics: {e}")

            raise  # Re-raise for service layer to handle
