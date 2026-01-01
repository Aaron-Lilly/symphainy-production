#!/usr/bin/env python3
"""
Authentication Manager Micro-Module

Manages authentication and creates standardized headers.

WHAT (Micro-Module): I manage authentication and create headers
HOW (Implementation): I create standardized authenticated headers for API requests
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from config.environment_loader import EnvironmentLoader
from utilities import UserContext


class AuthenticationManagerModule:
    """
    Authentication Manager Micro-Module
    
    Manages authentication and creates standardized headers for API requests.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, environment: Optional[EnvironmentLoader] = None):
        """Initialize Authentication Manager Module."""
        self.logger = logger or logging.getLogger(__name__)
        self.environment = environment
        self.is_initialized = False
        
        self.logger.info("🔐 Authentication Manager Module initialized")
    
    async def initialize(self):
        """Initialize the Authentication Manager Module."""
        self.logger.info("🚀 Initializing Authentication Manager Module...")
        self.is_initialized = True
        self.logger.info("✅ Authentication Manager Module initialized successfully")
    
    async def create_headers(
        self, 
        user_context: UserContext, 
        session_token: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Create standardized authenticated headers for API requests.
        
        Args:
            user_context: Context of the user making the request
            session_token: Smart City session token
            additional_headers: Additional headers to include
            
        Returns:
            A dictionary containing the headers
        """
        self.logger.info(f"Creating authenticated headers for user: {user_context.user_id}")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Symphainy-Frontend/1.0.0",
                "X-Request-ID": f"req_{int(datetime.utcnow().timestamp())}",
                "X-User-ID": user_context.user_id,
                "X-User-Email": user_context.email,
                "X-User-Name": user_context.full_name
            }
            
            # Add session token if provided
            if session_token:
                headers["X-Session-Token"] = session_token
            
            # Add user permissions if available
            if hasattr(user_context, 'permissions') and user_context.permissions:
                headers["X-User-Permissions"] = ",".join(user_context.permissions)
            
            # Add session ID if available
            if hasattr(user_context, 'session_id') and user_context.session_id:
                headers["X-Session-ID"] = user_context.session_id
            
            # Add additional headers if provided
            if additional_headers:
                headers.update(additional_headers)
            
            return headers
            
        except Exception as e:
            self.logger.error(f"Failed to create headers: {str(e)}")
            # Return basic headers if creation fails
            return {
                "Content-Type": "application/json",
                "User-Agent": "Symphainy-Frontend/1.0.0"
            }
    
    async def validate_session_token(self, session_token: str) -> Dict[str, Any]:
        """
        Validate a session token.
        
        Args:
            session_token: The session token to validate
            
        Returns:
            A dictionary containing validation results
        """
        self.logger.info("Validating session token")
        
        try:
            # For MVP, simulate token validation
            # In a real implementation, this would validate against a session store
            if session_token and len(session_token) > 10:
                return {
                    "valid": True,
                    "session_id": session_token,
                    "expires_at": datetime.utcnow().isoformat(),
                    "user_id": "validated_user"
                }
            else:
                return {
                    "valid": False,
                    "error": "Invalid session token format"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to validate session token: {str(e)}")
            return {
                "valid": False,
                "error": f"Token validation failed: {str(e)}"
            }
    
    async def create_bearer_token(self, user_context: UserContext) -> str:
        """
        Create a bearer token for the user.
        
        Args:
            user_context: Context of the user
            
        Returns:
            A bearer token string
        """
        self.logger.info(f"Creating bearer token for user: {user_context.user_id}")
        
        try:
            # For MVP, create a simple token
            # In a real implementation, this would create a JWT or similar
            token_data = {
                "user_id": user_context.user_id,
                "email": user_context.email,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Simple base64 encoding for MVP
            import base64
            import json
            token_string = json.dumps(token_data)
            encoded_token = base64.b64encode(token_string.encode()).decode()
            
            return f"Bearer {encoded_token}"
            
        except Exception as e:
            self.logger.error(f"Failed to create bearer token: {str(e)}")
            return f"Bearer {user_context.user_id}_{int(datetime.utcnow().timestamp())}"
    
    async def extract_user_from_headers(self, headers: Dict[str, str]) -> Optional[UserContext]:
        """
        Extract user context from headers.
        
        Args:
            headers: Request headers
            
        Returns:
            UserContext if found, None otherwise
        """
        try:
            user_id = headers.get("X-User-ID")
            email = headers.get("X-User-Email")
            full_name = headers.get("X-User-Name")
            
            if not user_id:
                return None
            
            # Create user context
            user_context = UserContext(
                user_id=user_id,
                full_name=full_name or "Unknown User",
                email=email or f"{user_id}@example.com",
                session_id=headers.get("X-Session-ID"),
                permissions=headers.get("X-User-Permissions", "").split(",") if headers.get("X-User-Permissions") else []
            )
            
            return user_context
            
        except Exception as e:
            self.logger.error(f"Failed to extract user from headers: {str(e)}")
            return None
    
    async def get_authentication_status(self, user_context: UserContext) -> Dict[str, Any]:
        """
        Get authentication status for a user.
        
        Args:
            user_context: Context of the user
            
        Returns:
            A dictionary containing authentication status
        """
        return {
            "authenticated": True,
            "user_id": user_context.user_id,
            "email": user_context.email,
            "full_name": user_context.full_name,
            "permissions": getattr(user_context, 'permissions', []),
            "session_id": getattr(user_context, 'session_id', None),
            "timestamp": datetime.utcnow().isoformat()
        }
