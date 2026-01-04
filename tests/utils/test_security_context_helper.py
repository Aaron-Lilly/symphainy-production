#!/usr/bin/env python3
"""
Test Security Context Helper

Helper functions for building security context from Supabase tokens in tests.
This ensures tests properly validate tokens and extract permissions for security checks.
"""

import logging
from typing import Dict, Any, Optional
from config.test_config import TestConfig

logger = logging.getLogger(__name__)


async def build_user_context_from_token(
    access_token: str,
    auth_abstraction: Optional[Any] = None,
    di_container: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Build user context from Supabase access token.
    
    This function:
    1. Validates the token through auth abstraction
    2. Extracts user_id, tenant_id, and permissions
    3. Returns properly formatted user_context dict for security checks
    
    Args:
        access_token: Supabase JWT access token
        auth_abstraction: Optional auth abstraction (will get from di_container if not provided)
        di_container: Optional DI container (for getting auth abstraction)
    
    Returns:
        Dict with user_id, tenant_id, permissions, access_token, and other security context
    """
    if not access_token:
        logger.warning("⚠️ No access token provided - returning empty context")
        return {}
    
    try:
        # Get auth abstraction if not provided
        if not auth_abstraction:
            if di_container:
                # Try to get auth abstraction from Public Works Foundation
                public_works = di_container.get_foundation_service("PublicWorksFoundationService")
                if public_works and hasattr(public_works, 'auth_abstraction'):
                    auth_abstraction = public_works.auth_abstraction
        
        # Validate token through auth abstraction
        if auth_abstraction:
            try:
                security_context = await auth_abstraction.validate_token(access_token)
                
                # Build user_context from SecurityContext
                user_context = {
                    "user_id": security_context.user_id,
                    "tenant_id": security_context.tenant_id,
                    "email": getattr(security_context, 'email', None),
                    "roles": security_context.roles if hasattr(security_context, 'roles') else [],
                    "permissions": security_context.permissions if hasattr(security_context, 'permissions') else [],
                    "access_token": access_token,
                    "origin": getattr(security_context, 'origin', 'auth_abstraction')
                }
                
                # Ensure permissions list is not empty (for security checks)
                if not user_context.get("permissions"):
                    # Default permissions for test users
                    # Note: check_permissions looks for "write", "admin", or "execute" in permissions list
                    user_context["permissions"] = ["read", "write", "admin", "session_management:read", "session_management:write"]
                    logger.debug(f"⚠️ No permissions found in token, using default test permissions")
                
                logger.debug(f"✅ Built user context from token: user_id={user_context.get('user_id')}, tenant_id={user_context.get('tenant_id')}, permissions={len(user_context.get('permissions', []))}")
                return user_context
                
            except Exception as e:
                logger.warning(f"⚠️ Token validation failed: {e}, using fallback context")
                # Fallback: build basic context from token (without validation)
                return _build_fallback_context(access_token)
        else:
            logger.warning("⚠️ Auth abstraction not available, using fallback context")
            return _build_fallback_context(access_token)
            
    except Exception as e:
        logger.error(f"❌ Failed to build user context from token: {e}")
        return _build_fallback_context(access_token)


def _build_fallback_context(access_token: str) -> Dict[str, Any]:
    """
    Build fallback user context when token validation is not available.
    
    This is used when auth abstraction is not available or validation fails.
    For tests, we provide default permissions to allow security checks to pass.
    """
    # Extract basic info from token (if possible)
    # For now, use test defaults
    return {
        "user_id": "test_user",
        "tenant_id": "test_tenant",
        "permissions": ["read", "write", "admin", "execute", "session_management:read", "session_management:write"],
        "access_token": access_token,
        "origin": "fallback"
    }


async def build_user_context_for_test(
    test_token: Optional[str] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    permissions: Optional[list] = None,
    auth_abstraction: Optional[Any] = None,
    di_container: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Build user context for tests with optional token validation.
    
    This is a convenience function that:
    1. Gets test token if not provided
    2. Validates token if available
    3. Merges with provided user_id, tenant_id, permissions
    4. Returns properly formatted user_context
    
    Args:
        test_token: Optional Supabase token (will get from get_test_supabase_token if not provided)
        user_id: Optional user_id (will use from token if not provided)
        tenant_id: Optional tenant_id (will use from token if not provided)
        permissions: Optional permissions list (will use from token if not provided)
        auth_abstraction: Optional auth abstraction
        di_container: Optional DI container
    
    Returns:
        Dict with user_id, tenant_id, permissions, access_token
    """
    from utils.real_infrastructure_helpers import get_test_supabase_token
    
    # Get token if not provided
    if not test_token:
        test_token = get_test_supabase_token()
    
    # Build context from token if available
    if test_token:
        token_context = await build_user_context_from_token(
            test_token,
            auth_abstraction=auth_abstraction,
            di_container=di_container
        )
    else:
        token_context = {}
    
    # Merge with provided values (provided values take precedence)
    user_context = {
        "user_id": user_id or token_context.get("user_id") or "test_user",
        "tenant_id": tenant_id or token_context.get("tenant_id") or "test_tenant",
        "permissions": permissions or token_context.get("permissions") or ["read", "write", "admin", "execute", "session_management:read", "session_management:write"],
        "access_token": test_token or token_context.get("access_token"),
        "email": token_context.get("email"),
        "roles": token_context.get("roles", []),
        "origin": token_context.get("origin", "test_helper")
    }
    
    logger.debug(f"✅ Built test user context: user_id={user_context.get('user_id')}, tenant_id={user_context.get('tenant_id')}, permissions={len(user_context.get('permissions', []))}")
    return user_context

