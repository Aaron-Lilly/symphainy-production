"""
Request-Scoped User Context

Provides a clean way to access user context throughout the request lifecycle
without threading it through every function call.

Usage:
    # At request entry point (e.g., FrontendGatewayService.route_frontend_request):
    from utilities.security_authorization.request_context import set_request_user_context
    
    user_context = {...}  # Build from headers/token
    set_request_user_context(user_context)
    
    # Anywhere in the request lifecycle:
    from utilities.security_authorization.request_context import get_request_user_context
    
    user_context = get_request_user_context()
    if user_context:
        user_id = user_context.get("user_id")
        permissions = user_context.get("permissions", [])
"""

import contextvars
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Context variable for request-scoped user context
_request_user_context: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    'request_user_context',
    default=None
)


def set_request_user_context(user_context: Dict[str, Any]) -> None:
    """
    Set the user context for the current request.
    
    This should be called once at the request entry point (e.g., middleware or gateway).
    The context is automatically scoped to the current async task/request.
    
    Args:
        user_context: Dictionary containing user context (user_id, tenant_id, permissions, etc.)
    """
    _request_user_context.set(user_context)
    logger.debug(f"✅ Request user context set: user_id={user_context.get('user_id')}, tenant_id={user_context.get('tenant_id')}")


def get_request_user_context() -> Optional[Dict[str, Any]]:
    """
    Get the user context for the current request.
    
    Returns None if no context has been set (e.g., unauthenticated request).
    
    Returns:
        User context dictionary or None if not set
    """
    return _request_user_context.get()


def get_user_id() -> Optional[str]:
    """Convenience method to get user_id from request context."""
    context = get_request_user_context()
    return context.get("user_id") if context else None


def get_tenant_id() -> Optional[str]:
    """Convenience method to get tenant_id from request context."""
    context = get_request_user_context()
    return context.get("tenant_id") if context else None


def get_permissions() -> list:
    """Convenience method to get permissions from request context."""
    context = get_request_user_context()
    return context.get("permissions", []) if context else []


def clear_request_user_context() -> None:
    """
    Clear the user context for the current request.
    
    This is typically called automatically by middleware, but can be called
    explicitly if needed (e.g., for testing or error recovery).
    """
    _request_user_context.set(None)
    logger.debug("✅ Request user context cleared")


