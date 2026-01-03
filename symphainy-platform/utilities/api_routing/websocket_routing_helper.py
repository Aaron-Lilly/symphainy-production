#!/usr/bin/env python3
"""
WebSocket Routing Helper

Provides utilities for websocket routing configuration and validation.
Centralizes websocket-specific routing logic.

WHAT: Helper utilities for websocket routing
HOW: Configuration loading, path detection, origin validation
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import for FastAPI middleware compatibility
try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    STARLETTE_AVAILABLE = True
except ImportError:
    STARLETTE_AVAILABLE = False
    BaseHTTPMiddleware = None
    Request = None


class WebSocketRoutingHelper:
    """Helper for websocket routing configuration and validation."""
    
    # Class-level config adapter (can be set globally)
    _config_adapter = None
    
    @classmethod
    def set_config_adapter(cls, config_adapter):
        """Set ConfigAdapter for centralized configuration (required)."""
        if not config_adapter:
            raise ValueError(
                "ConfigAdapter is required for WebSocketRoutingHelper. "
                "Pass config_adapter from Public Works Foundation."
            )
        cls._config_adapter = config_adapter
    
    @staticmethod
    def is_websocket_path(path: str) -> bool:
        """
        Check if path is a websocket endpoint.
        
        Args:
            path: Request path
            
        Returns:
            bool: True if path is a websocket endpoint
        """
        websocket_paths = WebSocketRoutingHelper.get_websocket_paths()
        return any(path.startswith(ws_path) for ws_path in websocket_paths)
    
    @staticmethod
    def get_websocket_paths() -> List[str]:
        """
        Get websocket paths from configuration.
        
        Returns:
            List[str]: List of websocket path prefixes
        
        Raises:
            ValueError: If ConfigAdapter is not set via set_config_adapter()
        
        Note:
            ConfigAdapter must be set at startup. This is not a runtime service locator.
            If ConfigAdapter is not available, that indicates a configuration problem.
        """
        if not WebSocketRoutingHelper._config_adapter:
            raise ValueError(
                "ConfigAdapter is required. Call WebSocketRoutingHelper.set_config_adapter() "
                "at startup with ConfigAdapter from Public Works Foundation. "
                "ConfigAdapter must be available before City Manager initialization."
            )
        
        ws_paths_str = WebSocketRoutingHelper._config_adapter.get("WEBSOCKET_PATHS", "/ws,/api/ws")
        
        if isinstance(ws_paths_str, str):
            return [path.strip() for path in ws_paths_str.split(",") if path.strip()]
        return ["/ws", "/api/ws"]  # Default includes new /ws endpoint
    
    @staticmethod
    def get_allowed_origins() -> List[str]:
        """
        Get allowed origins from configuration.
        
        Environment-aware: production uses specific origins, development allows all.
        
        Returns:
            List[str]: List of allowed origins
        
        Raises:
            ValueError: If ConfigAdapter is not set via set_config_adapter()
        
        Note:
            ConfigAdapter must be set at startup. This is not a runtime service locator.
            If ConfigAdapter is not available, that indicates a configuration problem.
        """
        if not WebSocketRoutingHelper._config_adapter:
            raise ValueError(
                "ConfigAdapter is required. Call WebSocketRoutingHelper.set_config_adapter() "
                "at startup with ConfigAdapter from Public Works Foundation. "
                "ConfigAdapter must be available before City Manager initialization."
            )
        
        env = WebSocketRoutingHelper._config_adapter.get("ENVIRONMENT", "development")
        cors_origins = WebSocketRoutingHelper._config_adapter.get("CORS_ORIGINS") or WebSocketRoutingHelper._config_adapter.get("API_CORS_ORIGINS")
        
        if isinstance(env, str):
            env = env.lower()
        
        if env == "production":
            # Production: specific origins only (no wildcard)
            if cors_origins:
                origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
                # Remove wildcard in production
                origins = [o for o in origins if o != "*"]
                if origins:
                    return origins
            # Fallback: empty list (reject all if not configured)
            logger.warning("⚠️ No CORS origins configured for production - websocket connections may be rejected")
            return []
        else:
            # Development: allow all origins
            if cors_origins and cors_origins != "*":
                return [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
            return ["*"]
    
    @staticmethod
    def validate_origin(origin: Optional[str]) -> bool:
        """
        Validate websocket origin (security in depth).
        
        Even though CORS is bypassed for websockets, we validate origins
        as an additional security layer.
        
        Args:
            origin: Origin header from websocket request
            
        Returns:
            bool: True if origin is allowed
        
        Raises:
            ValueError: If ConfigAdapter is not set via set_config_adapter()
        
        Note:
            ConfigAdapter must be set at startup. This is not a runtime service locator.
            If ConfigAdapter is not available, that indicates a configuration problem.
        """
        if not WebSocketRoutingHelper._config_adapter:
            raise ValueError(
                "ConfigAdapter is required. Call WebSocketRoutingHelper.set_config_adapter() "
                "at startup with ConfigAdapter from Public Works Foundation. "
                "ConfigAdapter must be available before City Manager initialization."
            )
        
        env = WebSocketRoutingHelper._config_adapter.get("ENVIRONMENT", "development")
        
        if isinstance(env, str):
            env = env.lower()
        allowed_origins = WebSocketRoutingHelper.get_allowed_origins()
        
        # In development, allow all origins (including None/missing)
        # This is safe because authentication is handled via session_token
        if env != "production":
            logger.debug(f"🔌 Development mode: allowing origin '{origin}' (or None)")
            return True
        
        # If no CORS origins configured, allow connection (for testing/development scenarios)
        # This handles the case where ENVIRONMENT=production but CORS_ORIGINS is not set
        if not allowed_origins:
            logger.warning(f"⚠️ Production mode but no CORS origins configured - allowing connection from origin '{origin}' (testing mode)")
            return True
        
        # In production with CORS origins configured, require origin header
        if not origin:
            logger.warning("🚫 Production mode: rejecting connection without origin header")
            return False
        
        # Wildcard allows all (shouldn't happen in production, but handle it)
        if "*" in allowed_origins:
            return True
        
        # Check if origin is in allowed list
        is_allowed = origin in allowed_origins
        if not is_allowed:
            logger.warning(f"🚫 Production mode: rejecting origin '{origin}' (not in allowed list)")
        return is_allowed
    
    @staticmethod
    def get_connection_limits() -> Dict[str, int]:
        """
        Get connection limits from configuration.
        
        Returns:
            Dict with max_connections_per_user and max_global_connections
        
        Raises:
            ValueError: If ConfigAdapter is not set via set_config_adapter()
        
        Note:
            ConfigAdapter must be set at startup. This is not a runtime service locator.
            If ConfigAdapter is not available, that indicates a configuration problem.
        """
        if not WebSocketRoutingHelper._config_adapter:
            raise ValueError(
                "ConfigAdapter is required. Call WebSocketRoutingHelper.set_config_adapter() "
                "at startup with ConfigAdapter from Public Works Foundation. "
                "ConfigAdapter must be available before City Manager initialization."
            )
        
        max_per_user = WebSocketRoutingHelper._config_adapter.get("WEBSOCKET_MAX_CONNECTIONS_PER_USER", "5")
        max_global = WebSocketRoutingHelper._config_adapter.get("WEBSOCKET_MAX_GLOBAL_CONNECTIONS", "1000")
        
        return {
            "max_per_user": int(max_per_user) if isinstance(max_per_user, (str, int)) else 5,
            "max_global": int(max_global) if isinstance(max_global, (str, int)) else 1000
        }
    
    @staticmethod
    def get_rate_limits() -> Dict[str, int]:
        """
        Get rate limits from configuration.
        
        Returns:
            Dict with max_messages_per_second and max_messages_per_minute
        
        Raises:
            ValueError: If ConfigAdapter is not set via set_config_adapter()
        
        Note:
            ConfigAdapter must be set at startup. This is not a runtime service locator.
            If ConfigAdapter is not available, that indicates a configuration problem.
        """
        if not WebSocketRoutingHelper._config_adapter:
            raise ValueError(
                "ConfigAdapter is required. Call WebSocketRoutingHelper.set_config_adapter() "
                "at startup with ConfigAdapter from Public Works Foundation. "
                "ConfigAdapter must be available before City Manager initialization."
            )
        
        max_per_second = WebSocketRoutingHelper._config_adapter.get("WEBSOCKET_MAX_MESSAGES_PER_SECOND", "10")
        max_per_minute = WebSocketRoutingHelper._config_adapter.get("WEBSOCKET_MAX_MESSAGES_PER_MINUTE", "100")
        
        return {
            "max_per_second": int(max_per_second) if isinstance(max_per_second, (str, int)) else 10,
            "max_per_minute": int(max_per_minute) if isinstance(max_per_minute, (str, int)) else 100
        }
    
    @staticmethod
    def get_websocket_cors_config() -> Dict[str, Any]:
        """
        Get CORS configuration for websockets.
        
        Returns:
            Dict with CORS configuration
        """
        return {
            "bypass_cors": True,  # Websockets handle auth via session_token
            "allowed_origins": WebSocketRoutingHelper.get_allowed_origins(),
            "allowed_methods": ["GET", "POST", "OPTIONS"],
            "allowed_headers": ["*"]
        }


# FastAPI-compatible CORS Middleware with WebSocket support
if STARLETTE_AVAILABLE:
    class FastAPICORSMiddleware(BaseHTTPMiddleware):
        """
        FastAPI CORS middleware with websocket support.
        
        Integrates with WebSocketRoutingHelper for configuration.
        Bypasses CORS for websocket paths (auth handled via session_token).
        """
        
        async def dispatch(self, request: Request, call_next):
            # Check if this is a websocket upgrade request or websocket path
            is_websocket_path = WebSocketRoutingHelper.is_websocket_path(request.url.path)
            
            # Also check headers for websocket upgrade
            upgrade_header = request.headers.get("upgrade", "").lower()
            connection_header = request.headers.get("connection", "").lower()
            is_websocket_upgrade = (
                upgrade_header == "websocket" and
                "upgrade" in connection_header
            )
            
            is_websocket = is_websocket_path or is_websocket_upgrade
            
            if is_websocket:
                # For websocket upgrades, completely bypass CORS validation
                # Authentication is handled via session_token query parameter
                # Just proceed with the request - no CORS checks
                logger.info(f"🔌 WebSocket request detected: path={request.url.path}, upgrade={upgrade_header}, connection={connection_header}")
                return await call_next(request)
            
            # For non-websocket requests, use standard CORS middleware logic
            # Handle preflight OPTIONS requests
            if request.method == "OPTIONS":
                origin = request.headers.get("origin")
                allowed_origins = WebSocketRoutingHelper.get_allowed_origins()
                
                if origin and (origin in allowed_origins or "*" in allowed_origins):
                    from starlette.responses import Response
                    headers = {
                        "Access-Control-Allow-Origin": origin if "*" not in allowed_origins else origin,
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Max-Age": "3600",
                    }
                    return Response(status_code=200, headers=headers)
            
            # Process the request
            response = await call_next(request)
            
            # Add CORS headers to response
            origin = request.headers.get("origin")
            allowed_origins = WebSocketRoutingHelper.get_allowed_origins()
            
            if origin and (origin in allowed_origins or "*" in allowed_origins):
                response.headers["Access-Control-Allow-Origin"] = origin if "*" not in allowed_origins else origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "*"
            
            return response

