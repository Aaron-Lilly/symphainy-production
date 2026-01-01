#!/usr/bin/env python3
"""
Session Management Adapter - Infrastructure Adapter

Redis-based session management adapter harvested from working infrastructure foundation patterns.
This is Layer 1 of the 5-layer architecture for Traffic Cop session management.

WHAT (Infrastructure Role): I provide Redis-based session management operations
HOW (Infrastructure Implementation): I use real Redis patterns from infrastructure foundation
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

# Try to import Redis, fall back to mock if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    # Note: Using mock implementation when Redis is not available


class MockSessionManagementClient:
    """Mock session management client for testing when Redis is not available."""
    
    def __init__(self):
        self.sessions = {}
        self.session_routes = {}
        self.user_sessions = {}
        self.route_metrics = {
            "total_requests": 0,
            "active_sessions": 0,
            "routes_created": 0,
            "sync_operations": 0
        }
    
    async def create_session_route(self, session_id: str, service_endpoint: str, routing_config: Dict[str, Any]) -> str:
        """Create a session route."""
        route_id = f"route_{session_id}_{uuid.uuid4().hex[:8]}"
        self.session_routes[route_id] = {
            "session_id": session_id,
            "service_endpoint": service_endpoint,
            "routing_config": routing_config,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "is_active": True
        }
        self.route_metrics["routes_created"] += 1
        return route_id
    
    async def validate_session_route(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session route."""
        for route_id, route_data in self.session_routes.items():
            if route_data["session_id"] == session_id and route_data["is_active"]:
                return {
                    "route_id": route_id,
                    "session_id": session_id,
                    "service_endpoint": route_data["service_endpoint"],
                    "routing_config": route_data["routing_config"],
                    "created_at": route_data["created_at"],
                    "last_accessed": route_data["last_accessed"],
                    "expires_at": route_data["expires_at"],
                    "is_active": route_data["is_active"]
                }
        return None
    
    async def update_session_route(self, session_id: str, routing_config: Dict[str, Any]) -> bool:
        """Update session route."""
        for route_id, route_data in self.session_routes.items():
            if route_data["session_id"] == session_id:
                route_data["routing_config"].update(routing_config)
                route_data["last_accessed"] = datetime.utcnow().isoformat()
                return True
        return False
    
    async def destroy_session_route(self, session_id: str) -> bool:
        """Destroy session route."""
        for route_id, route_data in self.session_routes.items():
            if route_data["session_id"] == session_id:
                route_data["is_active"] = False
                return True
        return False
    
    async def get_active_routes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active routes for user."""
        active_routes = []
        for route_id, route_data in self.session_routes.items():
            if route_data["is_active"]:
                active_routes.append(route_data)
        return active_routes
    
    async def cleanup_expired_routes(self) -> int:
        """Cleanup expired routes."""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        for route_id, route_data in self.session_routes.items():
            expires_at = datetime.fromisoformat(route_data["expires_at"])
            if current_time > expires_at:
                route_data["is_active"] = False
                cleaned_count += 1
        
        return cleaned_count
    
    async def get_route_metrics(self) -> Dict[str, Any]:
        """Get route metrics."""
        return self.route_metrics.copy()


class SessionManagementAdapter:
    """
    Session Management Adapter - Infrastructure Adapter
    
    Redis-based session management adapter harvested from working infrastructure foundation patterns.
    This adapter provides session routing and management capabilities for Traffic Cop.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", di_container=None):
        """Initialize Session Management Adapter."""
        if not di_container:
            raise ValueError("DI Container is required for SessionManagementAdapter initialization")
        self.redis_url = redis_url
        self.redis_client = None
        self.is_connected = False
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger("SessionManagementAdapter")
        
        # Session management metrics
        self.metrics = {
            "total_requests": 0,
            "active_sessions": 0,
            "routes_created": 0,
            "sync_operations": 0,
            "successful_routes": 0,
            "failed_routes": 0
        }
        
        self.logger.info("✅ Session Management Adapter initialized")
    
    async def initialize(self) -> bool:
        """Initialize Redis connection."""
        try:
            if REDIS_AVAILABLE:
                # Real Redis connection
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                
                # Test connection
                await self.redis_client.ping()
                self.is_connected = True
                self.logger.info("✅ Connected to Redis successfully for session management")
            else:
                # Mock Redis for development
                self.redis_client = MockSessionManagementClient()
                self.is_connected = True
                self.logger.info("✅ Using mock Redis client for session management")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("initialize", {
                    "service": self.service_name,
                    "redis_available": REDIS_AVAILABLE,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "initialize",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to initialize Redis: {e}")
            # Fall back to mock
            self.redis_client = MockSessionManagementClient()
            self.is_connected = True
            self.logger.warning("⚠️ Falling back to mock Redis client for session management")
            return True
    
    async def create_session_route(self, session_id: str, service_endpoint: str, 
                                 routing_config: Dict[str, Any]) -> str:
        """
        Create a session route.
        
        Args:
            session_id: Session identifier
            service_endpoint: Service endpoint to route to
            routing_config: Routing configuration
            
        Returns:
            str: Route ID
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Generate route ID
            route_id = f"route_{session_id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare route data
            route_data = {
                "route_id": route_id,
                "session_id": session_id,
                "service_endpoint": service_endpoint,
                "routing_config": routing_config,
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "is_active": True
            }
            
            # Store route in Redis
            route_key = f"session_route:{route_id}"
            await self.redis_client.hset(route_key, {
                "data": json.dumps(route_data),
                "created_at": datetime.utcnow().isoformat(),
                "ttl": "3600"
            })
            
            # Set expiration
            await self.redis_client.expire(route_key, 3600)
            
            # Store session route mapping
            session_routes_key = f"session_routes:{session_id}"
            await self.redis_client.sadd(session_routes_key, route_id)
            await self.redis_client.expire(session_routes_key, 3600)
            
            # Update metrics
            self.metrics["routes_created"] += 1
            self.metrics["successful_routes"] += 1
            
            self.logger.info(f"✅ Session route created: {route_id} for session {session_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_session_route", {
                    "route_id": route_id,
                    "session_id": session_id,
                    "success": True
                })
            
            return route_id
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_session_route",
                    "session_id": session_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error creating session route: {e}")
            self.metrics["failed_routes"] += 1
            raise
    
    async def validate_session_route(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Validate session route.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Optional[Dict]: Route data if found and active
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Get session routes
            session_routes_key = f"session_routes:{session_id}"
            route_ids = await self.redis_client.smembers(session_routes_key)
            
            for route_id in route_ids:
                route_key = f"session_route:{route_id}"
                route_data = await self.redis_client.hgetall(route_key)
                
                if route_data:
                    route_info = json.loads(route_data.get("data", "{}"))
                    
                    # Check if route is active and not expired
                    if route_info.get("is_active", False):
                        expires_at = datetime.fromisoformat(route_info.get("expires_at", datetime.utcnow().isoformat()))
                        if datetime.utcnow() < expires_at:
                            # Update last accessed
                            route_info["last_accessed"] = datetime.utcnow().isoformat()
                            await self.redis_client.hset(route_key, "data", json.dumps(route_info))
                            
                            self.logger.debug(f"✅ Session route validated: {route_id}")
                            
                            # Record telemetry on success
                            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                            if telemetry:
                                await telemetry.record_platform_operation_event("validate_session_route", {
                                    "route_id": route_id,
                                    "session_id": session_id,
                                    "found": True,
                                    "success": True
                                })
                            
                            return route_info
            
            self.logger.warning(f"⚠️ No active session route found for session {session_id}")
            
            # Record telemetry for not found
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("validate_session_route", {
                    "session_id": session_id,
                    "found": False,
                    "success": True
                })
            
            return None
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "validate_session_route",
                    "session_id": session_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error validating session route: {e}")
            return None
    
    async def update_session_route(self, session_id: str, routing_config: Dict[str, Any]) -> bool:
        """
        Update session route.
        
        Args:
            session_id: Session identifier
            routing_config: Updated routing configuration
            
        Returns:
            bool: Success status
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Get session routes
            session_routes_key = f"session_routes:{session_id}"
            route_ids = await self.redis_client.smembers(session_routes_key)
            
            for route_id in route_ids:
                route_key = f"session_route:{route_id}"
                route_data = await self.redis_client.hgetall(route_key)
                
                if route_data:
                    route_info = json.loads(route_data.get("data", "{}"))
                    
                    # Update routing configuration
                    route_info["routing_config"].update(routing_config)
                    route_info["last_accessed"] = datetime.utcnow().isoformat()
                    
                    # Store updated route
                    await self.redis_client.hset(route_key, "data", json.dumps(route_info))
                    
                    self.logger.debug(f"✅ Session route updated: {route_id}")
                    
                    # Record telemetry on success
                    telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                    if telemetry:
                        await telemetry.record_platform_operation_event("update_session_route", {
                            "route_id": route_id,
                            "session_id": session_id,
                            "success": True
                        })
                    
                    return True
            
            self.logger.warning(f"⚠️ No session route found to update for session {session_id}")
            return False
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "update_session_route",
                    "session_id": session_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error updating session route: {e}")
            return False
    
    async def destroy_session_route(self, session_id: str) -> bool:
        """
        Destroy session route.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: Success status
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Get session routes
            session_routes_key = f"session_routes:{session_id}"
            route_ids = await self.redis_client.smembers(session_routes_key)
            
            destroyed_count = 0
            for route_id in route_ids:
                route_key = f"session_route:{route_id}"
                
                # Mark route as inactive
                route_data = await self.redis_client.hgetall(route_key)
                if route_data:
                    route_info = json.loads(route_data.get("data", "{}"))
                    route_info["is_active"] = False
                    route_info["last_accessed"] = datetime.utcnow().isoformat()
                    
                    await self.redis_client.hset(route_key, "data", json.dumps(route_info))
                    destroyed_count += 1
            
            # Remove session routes set
            await self.redis_client.delete(session_routes_key)
            
            self.logger.info(f"✅ Destroyed {destroyed_count} session routes for session {session_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("destroy_session_route", {
                    "session_id": session_id,
                    "destroyed_count": destroyed_count,
                    "success": True
                })
            
            return destroyed_count > 0
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "destroy_session_route",
                    "session_id": session_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error destroying session route: {e}")
            return False
    
    async def get_active_routes(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get active routes for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List[Dict]: List of active routes
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Get all session routes for user
            user_routes_key = f"user_routes:{user_id}"
            route_ids = await self.redis_client.smembers(user_routes_key)
            
            active_routes = []
            for route_id in route_ids:
                route_key = f"session_route:{route_id}"
                route_data = await self.redis_client.hgetall(route_key)
                
                if route_data:
                    route_info = json.loads(route_data.get("data", "{}"))
                    if route_info.get("is_active", False):
                        active_routes.append(route_info)
            
            self.logger.debug(f"✅ Retrieved {len(active_routes)} active routes for user {user_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_active_routes", {
                    "user_id": user_id,
                    "route_count": len(active_routes),
                    "success": True
                })
            
            return active_routes
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_active_routes",
                    "user_id": user_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting active routes: {e}")
            return []
    
    async def cleanup_expired_routes(self) -> int:
        """
        Cleanup expired routes.
        
        Returns:
            int: Number of routes cleaned up
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Get all session route keys
            route_keys = await self.redis_client.keys("session_route:*")
            cleaned_count = 0
            current_time = datetime.utcnow()
            
            for route_key in route_keys:
                route_data = await self.redis_client.hgetall(route_key)
                if route_data:
                    route_info = json.loads(route_data.get("data", "{}"))
                    expires_at = datetime.fromisoformat(route_info.get("expires_at", current_time.isoformat()))
                    
                    if current_time > expires_at:
                        # Mark as inactive
                        route_info["is_active"] = False
                        await self.redis_client.hset(route_key, "data", json.dumps(route_info))
                        cleaned_count += 1
            
            self.logger.info(f"✅ Cleaned up {cleaned_count} expired session routes")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("cleanup_expired_routes", {
                    "cleaned_count": cleaned_count,
                    "success": True
                })
            
            return cleaned_count
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "cleanup_expired_routes",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error cleaning up expired routes: {e}")
            return 0
    
    async def get_route_metrics(self) -> Dict[str, Any]:
        """
        Get route metrics.
        
        Returns:
            Dict: Route metrics
        """
        try:
            # Update active sessions count
            if self.is_connected:
                active_routes = await self.redis_client.keys("session_route:*")
                self.metrics["active_sessions"] = len(active_routes)
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_route_metrics", {
                    "active_sessions": self.metrics.get("active_sessions", 0),
                    "success": True
                })
            
            return self.metrics.copy()
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_route_metrics",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting route metrics: {e}")
            return self.metrics.copy()
    
    async def close(self):
        """Close Redis connection."""
        try:
            if self.redis_client and hasattr(self.redis_client, 'close'):
                await self.redis_client.close()
            self.is_connected = False
            self.logger.info("✅ Session Management Adapter connection closed")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("close", {
                    "service": self.service_name,
                    "success": True
                })
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "close",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error closing connection: {e}")



