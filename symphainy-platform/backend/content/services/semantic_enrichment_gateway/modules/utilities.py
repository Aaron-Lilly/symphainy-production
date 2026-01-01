#!/usr/bin/env python3
"""Utilities module for Semantic Enrichment Gateway."""

from typing import Dict, Any, Optional, List


class Utilities:
    """Utilities module for Semantic Enrichment Gateway."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    def _convert_user_context(self, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert UserContext object to dict if needed.
        
        Args:
            user_context: UserContext object or dict
            
        Returns:
            Dict with user context information
        """
        if user_context is None:
            return {}
        
        # If it's already a dict, return as-is
        if isinstance(user_context, dict):
            return user_context
        
        # If it's a UserContext object, convert to dict
        if hasattr(user_context, 'user_id'):
            return {
                "user_id": getattr(user_context, 'user_id', None),
                "tenant_id": getattr(user_context, 'tenant_id', None),
                "email": getattr(user_context, 'email', None),
                "full_name": getattr(user_context, 'full_name', None),
                "session_id": getattr(user_context, 'session_id', None),
                "permissions": getattr(user_context, 'permissions', []),
                "roles": getattr(user_context, 'roles', [])
            }
        
        return {}
    
    def _extract_tenant_id(self, user_context: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Extract tenant ID from user context.
        
        Args:
            user_context: User context dict or object
            
        Returns:
            Tenant ID or None
        """
        user_context_dict = self._convert_user_context(user_context)
        return user_context_dict.get("tenant_id")
    
    def _validate_content_id(self, content_id: str) -> bool:
        """
        Validate content ID format.
        
        Args:
            content_id: Content metadata ID
            
        Returns:
            True if valid, False otherwise
        """
        if not content_id or not isinstance(content_id, str):
            return False
        
        # Basic validation - content ID should not be empty
        if len(content_id.strip()) == 0:
            return False
        
        return True

