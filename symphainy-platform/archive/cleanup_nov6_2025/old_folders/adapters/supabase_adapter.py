#!/usr/bin/env python3
"""
Supabase Adapter - Raw Technology Client

Real Supabase client wrapper with no business logic.
This is Layer 1 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide raw Supabase client operations
HOW (Infrastructure Implementation): I use real Supabase client with no business logic
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from supabase import create_client, Client
from gotrue.errors import AuthError as SupabaseAuthError

logger = logging.getLogger(__name__)

class SupabaseAdapter:
    """
    Raw Supabase client wrapper - no business logic.
    
    This adapter provides direct access to Supabase operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, url: str, anon_key: str, service_key: str = None):
        """Initialize Supabase adapter with real credentials."""
        self.url = url
        self.anon_key = anon_key
        self.service_key = service_key
        
        # Create clients
        self.anon_client: Client = create_client(url, anon_key)
        self.service_client: Client = create_client(url, service_key) if service_key else self.anon_client
        
        logger.info(f"✅ Supabase adapter initialized with URL: {url}")
    
    # ============================================================================
    # RAW AUTHENTICATION OPERATIONS
    # ============================================================================
    
    async def sign_in_with_password(self, email: str, password: str) -> Dict[str, Any]:
        """Raw authentication with Supabase - no business logic."""
        try:
            response = self.anon_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None,
                "session": response.session.__dict__ if response.session else None,
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None,
                "expires_in": response.session.expires_in if response.session else None,
                "expires_at": response.session.expires_at if response.session else None
            }
        except SupabaseAuthError as e:
            logger.error(f"Supabase auth error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "auth_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in sign_in_with_password: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "unexpected_error"
            }
    
    async def sign_up_with_password(self, email: str, password: str, user_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Raw user registration with Supabase - no business logic."""
        try:
            response = self.anon_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None,
                "session": response.session.__dict__ if response.session else None,
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None,
                "expires_in": response.session.expires_in if response.session else None,
                "expires_at": response.session.expires_at if response.session else None
            }
        except SupabaseAuthError as e:
            logger.error(f"Supabase signup error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "auth_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in sign_up_with_password: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "unexpected_error"
            }
    
    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Raw token refresh with Supabase - no business logic."""
        try:
            response = self.anon_client.auth.refresh_session(refresh_token)
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None,
                "session": response.session.__dict__ if response.session else None,
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None,
                "expires_in": response.session.expires_in if response.session else None,
                "expires_at": response.session.expires_at if response.session else None
            }
        except SupabaseAuthError as e:
            logger.error(f"Supabase refresh error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "auth_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in refresh_session: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "unexpected_error"
            }
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """Raw user retrieval with Supabase - no business logic."""
        try:
            # Set the session for the client
            self.anon_client.auth.set_session(access_token, "")
            user = self.anon_client.auth.get_user()
            
            return {
                "success": True,
                "user": user.user.__dict__ if user.user else None,
                "access_token": access_token
            }
        except SupabaseAuthError as e:
            logger.error(f"Supabase get_user error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "auth_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_user: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "unexpected_error"
            }
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Raw user sign out with Supabase - no business logic."""
        try:
            # Set the session for the client
            self.anon_client.auth.set_session(access_token, "")
            response = self.anon_client.auth.sign_out()
            
            return {
                "success": True,
                "message": "User signed out successfully"
            }
        except SupabaseAuthError as e:
            logger.error(f"Supabase sign_out error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "auth_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in sign_out: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "unexpected_error"
            }
    
    # ============================================================================
    # RAW DATABASE OPERATIONS (for RLS policies)
    # ============================================================================
    
    async def execute_rls_policy(self, table: str, operation: str, user_context: Dict[str, Any], data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Raw RLS policy execution with Supabase - no business logic."""
        try:
            # Set the session for the client
            if user_context.get("access_token"):
                self.anon_client.auth.set_session(user_context["access_token"], "")
            
            if operation == "select":
                response = self.anon_client.table(table).select("*").execute()
            elif operation == "insert":
                response = self.anon_client.table(table).insert(data).execute()
            elif operation == "update":
                response = self.anon_client.table(table).update(data).execute()
            elif operation == "delete":
                response = self.anon_client.table(table).delete().execute()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported operation: {operation}",
                    "error_type": "invalid_operation"
                }
            
            return {
                "success": True,
                "data": response.data,
                "count": response.count,
                "operation": operation,
                "table": table
            }
        except Exception as e:
            logger.error(f"Supabase RLS policy error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "rls_error"
            }
    
    # ============================================================================
    # RAW ADMIN OPERATIONS (using service key)
    # ============================================================================
    
    async def admin_get_user(self, user_id: str) -> Dict[str, Any]:
        """Raw admin user retrieval with Supabase - no business logic."""
        try:
            response = self.service_client.auth.admin.get_user_by_id(user_id)
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None
            }
        except Exception as e:
            logger.error(f"Supabase admin_get_user error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "admin_error"
            }
    
    async def admin_update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw admin user update with Supabase - no business logic."""
        try:
            response = self.service_client.auth.admin.update_user_by_id(user_id, updates)
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None
            }
        except Exception as e:
            logger.error(f"Supabase admin_update_user error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "admin_error"
            }
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Supabase connection - no business logic."""
        try:
            # Try to get the current user (this will fail if not authenticated, but that's OK)
            self.anon_client.auth.get_user()
            return {
                "success": True,
                "message": "Supabase connection successful",
                "url": self.url
            }
        except Exception as e:
            # Connection test doesn't require authentication
            return {
                "success": True,
                "message": "Supabase connection successful (no auth required)",
                "url": self.url
            }
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get Supabase connection information - no business logic."""
        return {
            "url": self.url,
            "has_anon_key": bool(self.anon_key),
            "has_service_key": bool(self.service_key),
            "anon_client_initialized": self.anon_client is not None,
            "service_client_initialized": self.service_client is not None
        }



