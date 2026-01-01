#!/usr/bin/env python3
"""
API Routing Utility - Centralized Request Routing for All Realms

This utility provides centralized API request routing with middleware support
across all realms in the SymphAIny platform.

WHAT (Utility Role): I provide centralized API routing with middleware support for all realms
HOW (Utility Implementation): I use a flexible routing system with pluggable middleware pipeline
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union, Protocol
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import re
import uuid

from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext


class HTTPMethod(Enum):
    """HTTP methods supported by the API router."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class RouteStatus(Enum):
    """Route registration status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


@dataclass
class RouteInfo:
    """Information about a registered route."""
    method: HTTPMethod
    path: str
    handler: Callable
    middleware: List[Callable] = field(default_factory=list)
    pillar: str = ""
    realm: str = ""
    status: RouteStatus = RouteStatus.ACTIVE
    description: str = ""
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)


@dataclass
class RequestContext:
    """Context for API requests."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: HTTPMethod = HTTPMethod.GET
    path: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    user_context: Optional[UserContext] = None
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    pillar: str = ""
    realm: str = ""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ResponseContext:
    """Context for API responses."""
    request_id: str = ""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    end_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# Middleware protocol moved to middleware_protocol.py to avoid circular imports
# Re-export for backward compatibility (after RequestContext/ResponseContext are defined)
from .middleware_protocol import Middleware


class APIRoutingUtility:
    """
    API Routing Utility - Centralized Request Routing for All Realms
    
    Provides centralized API request routing with middleware support
    across all realms in the SymphAIny platform.
    """
    
    def __init__(self, di_container: DIContainerService):
        """Initialize API Routing Utility."""
        self.di_container = di_container
        self.logger = logging.getLogger("APIRoutingUtility")
        
        # Route registry
        self.routes: Dict[str, RouteInfo] = {}
        self.route_patterns: Dict[str, re.Pattern] = {}
        
        # Middleware registry
        self.global_middleware: List[Callable] = []
        self.realm_middleware: Dict[str, List[Callable]] = {}
        self.pillar_middleware: Dict[str, List[Callable]] = {}
        
        # Initialize enhanced middleware (lazy loading to avoid circular imports)
        self.enhanced_error_handling = None
        self.enhanced_logging = None
        
        # Statistics and monitoring
        self.request_stats: Dict[str, Dict[str, Any]] = {}
        self.error_stats: Dict[str, int] = {}
        
        # Get Curator for route registration (lazy loading)
        self.curator = None
        
        self.logger.info("✅ API Routing Utility initialized")
    
    async def initialize(self):
        """Initialize the API Routing Utility."""
        self.logger.info("🚀 Initializing API Routing Utility...")
        
        # Initialize enhanced middleware (lazy loading to avoid circular imports)
        try:
            from utilities.api_routing.middleware.enhanced_error_handling_middleware import EnhancedErrorHandlingMiddleware
            from utilities.api_routing.middleware.enhanced_logging_middleware import EnhancedLoggingMiddleware
            
            self.enhanced_error_handling = EnhancedErrorHandlingMiddleware(self.di_container)
            self.enhanced_logging = EnhancedLoggingMiddleware(self.di_container)
            
            # Add to global middleware
            self.global_middleware.extend([
                self.enhanced_logging,
                self.enhanced_error_handling
            ])
            
            self.logger.info("✅ Enhanced middleware initialized")
            
        except ImportError as e:
            self.logger.warning(f"Enhanced middleware not available: {e}")
        
        # Get Curator from DI container (for route registration)
        try:
            self.curator = self.di_container.get_curator()
            if self.curator:
                self.logger.info("✅ Curator connected for route registration")
            else:
                self.logger.warning("⚠️ Curator not available - routes will not be registered in Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get Curator: {e}")
        
        self.logger.info("✅ API Routing Utility initialized successfully")
    
    def get_router(self):
        """Get the FastAPI router for this utility."""
        # This is a placeholder - in a real implementation, this would return a FastAPI router
        # For now, we'll return None to avoid breaking the API Gateway
        self.logger.warning("get_router() called but not implemented - returning None")
        return None
    
    async def register_route(
        self,
        method: HTTPMethod,
        path: str,
        handler: Callable,
        pillar: str = "",
        realm: str = "",
        middleware: List[Callable] = None,
        description: str = "",
        version: str = "1.0",
        tags: List[str] = None
    ) -> str:
        """
        Register an API route with middleware support and track in Curator.
        
        Routes are DEFINED by domains (when registering capabilities/SOA APIs),
        but TRACKED centrally by Curator (endpoint registry for discovery).
        
        Args:
            method: HTTP method
            path: Route path (supports path parameters like /api/{id})
            handler: Route handler function
            pillar: Pillar name (e.g., "content-pillar")
            realm: Realm name (e.g., "business_enablement")
            middleware: List of middleware functions
            description: Route description
            version: API version
            tags: Route tags for documentation
            
        Returns:
            str: Route ID for management
        """
        try:
            route_id = f"{method.value}:{path}:{pillar}:{realm}"
            
            # Create route info
            route_info = RouteInfo(
                method=method,
                path=path,
                handler=handler,
                middleware=middleware or [],
                pillar=pillar,
                realm=realm,
                description=description,
                version=version,
                tags=tags or []
            )
            
            # Register route
            self.routes[route_id] = route_info
            
            # Compile path pattern for matching
            pattern = self._compile_path_pattern(path)
            self.route_patterns[route_id] = pattern
            
            # Register route in Curator's endpoint registry (domains define, Curator tracks)
            if self.curator:
                try:
                    route_metadata = {
                        "route_id": route_id,
                        "path": path,
                        "method": method.value,
                        "pillar": pillar,
                        "realm": realm,
                        "handler": handler.__name__ if callable(handler) else str(handler),
                        "description": description,
                        "version": version,
                        "defined_by": realm or "unknown_domain"  # Domain that defined this route
                    }
                    
                    # Register in Curator's endpoint registry (Curator tracks centrally)
                    if hasattr(self.curator, 'register_route'):
                        await self.curator.register_route(route_metadata)
                        self.logger.debug(f"✅ Route registered in Curator: {path}")
                    else:
                        self.logger.warning("⚠️ Curator.register_route() not available")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to register route in Curator: {e}")
            
            self.logger.info(f"✅ Route registered: {method.value} {path} ({pillar})")
            return route_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register route {method.value} {path}: {e}")
            raise
    
    async def register_middleware(
        self,
        middleware: Callable,
        scope: str = "global",
        target: str = ""
    ) -> None:
        """
        Register middleware for different scopes.
        
        Args:
            middleware: Middleware function
            scope: Middleware scope ("global", "realm", "pillar")
            target: Target realm or pillar name (for realm/pillar scope)
        """
        try:
            if scope == "global":
                self.global_middleware.append(middleware)
                self.logger.info(f"✅ Global middleware registered: {middleware.__name__}")
            elif scope == "realm":
                if target not in self.realm_middleware:
                    self.realm_middleware[target] = []
                self.realm_middleware[target].append(middleware)
                self.logger.info(f"✅ Realm middleware registered: {middleware.__name__} for {target}")
            elif scope == "pillar":
                if target not in self.pillar_middleware:
                    self.pillar_middleware[target] = []
                self.pillar_middleware[target].append(middleware)
                self.logger.info(f"✅ Pillar middleware registered: {middleware.__name__} for {target}")
            else:
                raise ValueError(f"Invalid middleware scope: {scope}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to register middleware: {e}")
            raise
    
    async def route_request(
        self,
        method: HTTPMethod,
        path: str,
        request_data: Dict[str, Any],
        user_context: UserContext,
        headers: Dict[str, str] = None,
        query_params: Dict[str, Any] = None
    ) -> ResponseContext:
        """
        Route an API request through middleware to appropriate handler.
        
        Args:
            method: HTTP method
            path: Request path
            request_data: Request body data
            user_context: User context
            headers: Request headers
            query_params: Query parameters
            
        Returns:
            ResponseContext: Response context with result
        """
        start_time = datetime.utcnow()
        request_id = str(uuid.uuid4())
        
        try:
            # Find matching route first to get pillar and realm
            route_info = await self._find_matching_route(method, path)
            
            # Create request context
            request_context = RequestContext(
                request_id=request_id,
                method=method,
                path=path,
                headers=headers or {},
                query_params=query_params or {},
                body=request_data,
                user_context=user_context,
                start_time=start_time.isoformat(),
                pillar=route_info.pillar if route_info else "",
                realm=route_info.realm if route_info else "",
                correlation_id=request_id  # Use request_id as correlation_id
            )
            if not route_info:
                return await self._create_error_response(
                    request_context,
                    404,
                    f"Route not found: {method.value} {path}"
                )
            
            # APPROACH 1: DEBUG LOGGING AT APIRoutingUtility LEVEL
            if "process-file" in path:
                import sys
                sys.stderr.write(f"\n🔍🔍🔍 [APPROACH 1] APIRoutingUtility.route_request CALLED\n")
                sys.stderr.write(f"🔍🔍🔍 [APPROACH 1] path={path}, method={method.value}\n")
                sys.stderr.write(f"🔍🔍🔍 [APPROACH 1] request_data KEYS: {list(request_data.keys()) if isinstance(request_data, dict) else 'NOT_A_DICT'}\n")
                sys.stderr.write(f"🔍🔍🔍 [APPROACH 1] request_data.get('options'): {request_data.get('options') if isinstance(request_data, dict) else 'N/A'}\n")
                sys.stderr.write(f"🔍🔍🔍 [APPROACH 1] route_info.handler: {route_info.handler if route_info else 'NO_ROUTE_INFO'}\n")
                sys.stderr.flush()
                self.logger.error(f"🔍🔍🔍 [APPROACH 1] APIRoutingUtility.route_request CALLED for path={path}")
                self.logger.error(f"🔍🔍🔍 [APPROACH 1] request_data KEYS: {list(request_data.keys()) if isinstance(request_data, dict) else 'NOT_A_DICT'}")
            
            # Build middleware chain with enhanced middleware
            middleware_chain = await self._build_enhanced_middleware_chain(route_info)
            
            # Execute request through middleware chain
            response_context = await self._execute_middleware_chain(
                request_context,
                middleware_chain,
                route_info.handler
            )
            
            # Update statistics
            await self._update_request_stats(route_info, response_context)
            
            return response_context
            
        except Exception as e:
            self.logger.error(f"❌ Request routing failed: {e}")
            return await self._create_error_response(
                request_context,
                500,
                f"Internal server error: {str(e)}"
            )
    
    async def get_route_info(self, route_id: str) -> Optional[RouteInfo]:
        """Get information about a registered route."""
        return self.routes.get(route_id)
    
    async def list_routes(
        self,
        pillar: str = None,
        realm: str = None,
        status: RouteStatus = None
    ) -> List[RouteInfo]:
        """List registered routes with optional filtering."""
        filtered_routes = []
        
        for route_info in self.routes.values():
            if pillar and route_info.pillar != pillar:
                continue
            if realm and route_info.realm != realm:
                continue
            if status and route_info.status != status:
                continue
            filtered_routes.append(route_info)
        
        return filtered_routes
    
    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics and metrics."""
        return {
            "total_routes": len(self.routes),
            "active_routes": len([r for r in self.routes.values() if r.status == RouteStatus.ACTIVE]),
            "global_middleware_count": len(self.global_middleware),
            "realm_middleware_count": sum(len(mw) for mw in self.realm_middleware.values()),
            "pillar_middleware_count": sum(len(mw) for mw in self.pillar_middleware.values()),
            "request_stats": self.request_stats,
            "error_stats": self.error_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the API routing utility."""
        return {
            "status": "healthy",
            "routes_registered": len(self.routes),
            "middleware_loaded": len(self.global_middleware),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # PRIVATE METHODS
    
    def _compile_path_pattern(self, path: str) -> re.Pattern:
        """Compile path pattern for route matching."""
        # Convert path parameters {param} to regex groups
        pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', path)
        pattern = f"^{pattern}$"
        return re.compile(pattern)
    
    async def _find_matching_route(self, method: HTTPMethod, path: str) -> Optional[RouteInfo]:
        """Find route that matches the method and path."""
        # APPROACH 1: DEBUG LOGGING AT ROUTE MATCHING
        if "process-file" in path:
            import sys
            sys.stderr.write(f"\n🔍🔍🔍 [APPROACH 1] _find_matching_route CALLED: method={method.value}, path={path}\n")
            sys.stderr.write(f"🔍🔍🔍 [APPROACH 1] Total routes: {len(self.routes)}\n")
            sys.stderr.flush()
            self.logger.error(f"🔍🔍🔍 [APPROACH 1] _find_matching_route CALLED: method={method.value}, path={path}, total_routes={len(self.routes)}")
        
        for route_id, route_info in self.routes.items():
            if route_info.method != method:
                continue
            
            pattern = self.route_patterns.get(route_id)
            if pattern and pattern.match(path):
                if "process-file" in path:
                    import sys
                    sys.stderr.write(f"🔍🔍🔍 [APPROACH 1] ROUTE MATCHED: route_id={route_id}, handler={route_info.handler}\n")
                    sys.stderr.flush()
                    self.logger.error(f"🔍🔍🔍 [APPROACH 1] ROUTE MATCHED: route_id={route_id}, handler={route_info.handler}")
                return route_info
        
        if "process-file" in path:
            import sys
            sys.stderr.write(f"🔍🔍🔍 [APPROACH 1] NO ROUTE MATCHED for path={path}\n")
            sys.stderr.flush()
            self.logger.error(f"🔍🔍🔍 [APPROACH 1] NO ROUTE MATCHED for path={path}")
        
        return None
    
    async def _build_middleware_chain(self, route_info: RouteInfo) -> List[Callable]:
        """Build middleware chain for a route."""
        middleware_chain = []
        
        # Add global middleware
        middleware_chain.extend(self.global_middleware)
        
        # Add realm-specific middleware
        if route_info.realm in self.realm_middleware:
            middleware_chain.extend(self.realm_middleware[route_info.realm])
        
        # Add pillar-specific middleware
        if route_info.pillar in self.pillar_middleware:
            middleware_chain.extend(self.pillar_middleware[route_info.pillar])
        
        # Add route-specific middleware
        middleware_chain.extend(route_info.middleware)
        
        return middleware_chain
    
    async def _build_enhanced_middleware_chain(self, route_info: RouteInfo) -> List[Callable]:
        """Build enhanced middleware chain with error handling and logging integration."""
        middleware_chain = []
        
        # Lazy load enhanced middleware
        if self.enhanced_logging is None:
            from .middleware.enhanced_logging_middleware import EnhancedLoggingMiddleware
            self.enhanced_logging = EnhancedLoggingMiddleware(self.di_container)
        
        if self.enhanced_error_handling is None:
            from .middleware.enhanced_error_handling_middleware import EnhancedErrorHandlingMiddleware
            self.enhanced_error_handling = EnhancedErrorHandlingMiddleware(self.di_container)
        
        # Add enhanced logging middleware first (for request start logging)
        middleware_chain.append(self.enhanced_logging)
        
        # Add global middleware
        middleware_chain.extend(self.global_middleware)
        
        # Add realm-specific middleware
        if route_info.realm in self.realm_middleware:
            middleware_chain.extend(self.realm_middleware[route_info.realm])
        
        # Add pillar-specific middleware
        if route_info.pillar in self.pillar_middleware:
            middleware_chain.extend(self.pillar_middleware[route_info.pillar])
        
        # Add route-specific middleware
        middleware_chain.extend(route_info.middleware)
        
        # Add enhanced error handling middleware last (for error handling)
        middleware_chain.append(self.enhanced_error_handling)
        
        return middleware_chain
    
    async def _execute_middleware_chain(
        self,
        request_context: RequestContext,
        middleware_chain: List[Callable],
        handler: Callable
    ) -> ResponseContext:
        """Execute request through middleware chain."""
        async def execute_handler():
            """Execute the final handler."""
            try:
                result = await handler(request_context.body, request_context.user_context)
                return ResponseContext(
                    request_id=request_context.request_id,
                    status_code=200,
                    body=result,
                    end_time=datetime.utcnow().isoformat()
                )
            except Exception as e:
                self.logger.error(f"❌ Handler execution failed: {e}")
                return await self._create_error_response(
                    request_context,
                    500,
                    f"Handler execution failed: {str(e)}"
                )
        
        # Execute middleware chain
        current_handler = execute_handler
        for middleware in reversed(middleware_chain):
            current_handler = lambda mw=middleware, next_h=current_handler: mw(
                request_context, request_context.user_context, next_h
            )
        
        return await current_handler()
    
    async def _create_error_response(
        self,
        request_context: RequestContext,
        status_code: int,
        error_message: str
    ) -> ResponseContext:
        """Create standardized error response."""
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=status_code,
            body={
                "success": False,
                "error": {
                    "code": f"HTTP_{status_code}",
                    "message": error_message,
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            end_time=datetime.utcnow().isoformat()
        )
    
    async def _update_request_stats(self, route_info: RouteInfo, response_context: ResponseContext) -> None:
        """Update request statistics."""
        route_key = f"{route_info.method.value}:{route_info.path}"
        
        if route_key not in self.request_stats:
            self.request_stats[route_key] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0
            }
        
        stats = self.request_stats[route_key]
        stats["total_requests"] += 1
        
        if 200 <= response_context.status_code < 300:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
            error_key = f"{response_context.status_code}"
            self.error_stats[error_key] = self.error_stats.get(error_key, 0) + 1
        
        # Update average response time
        if response_context.processing_time_ms > 0:
            current_avg = stats["average_response_time"]
            total_requests = stats["total_requests"]
            stats["average_response_time"] = (
                (current_avg * (total_requests - 1) + response_context.processing_time_ms) / total_requests
            )
