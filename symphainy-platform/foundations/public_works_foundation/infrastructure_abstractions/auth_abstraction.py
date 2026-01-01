#!/usr/bin/env python3
"""
Auth Abstraction - Generic Infrastructure Implementation

Generic authentication implementation using real adapters.
This is Layer 3 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide generic authentication services
HOW (Infrastructure Implementation): I use real adapters with generic interfaces
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import AuthenticationProtocol, SecurityContext
from ..infrastructure_adapters.supabase_adapter import SupabaseAdapter
# BREAKING: JWT adapter import removed - user auth uses Supabase only
# from ..infrastructure_adapters.jwt_adapter import JWTAdapter

logger = logging.getLogger(__name__)

class AuthAbstraction(AuthenticationProtocol):
    """
    Generic authentication abstraction using real adapters.
    
    This abstraction implements the AuthenticationProtocol using real
    Supabase and JWT adapters, providing a generic interface.
    """
    
    def __init__(self, supabase_adapter: SupabaseAdapter, jwt_adapter: Optional[Any] = None, di_container=None):
        """
        Initialize Auth abstraction with real adapters.
        
        FIX: jwt_adapter is now optional - user authentication uses Supabase only.
        
        Args:
            supabase_adapter: Supabase adapter for authentication (REQUIRED)
            jwt_adapter: JWT adapter (OPTIONAL - not used for user auth, kept for backward compatibility)
            di_container: Dependency injection container
        """
        self.supabase = supabase_adapter
        self.jwt = jwt_adapter  # Can be None - user auth doesn't use it
        self.di_container = di_container
        self.service_name = "auth_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Auth Abstraction initialized")
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Authenticate user using real Supabase adapter."""
        try:
            email = credentials.get("email")
            password = credentials.get("password")
            
            if not email or not password:
                raise ValueError("Email and password are required")
            
            # Use real Supabase adapter
            result = await self.supabase.sign_in_with_password(email, password)
            
            if not result.get("success"):
                raise AuthenticationError(f"Authentication failed: {result.get('error')}")
            
            user_data = result.get("user", {})
            session_data = result.get("session", {})
            
            # Extract user information
            user_id = user_data.get("id")
            email = user_data.get("email", "")
            
            # ✅ NEW: Check tenant status - query user_tenants table first
            tenant_info = await self.supabase.get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
            
            # ✅ NEW: If no tenant_id from database, check user_metadata as fallback
            if not tenant_id:
                tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
            
            # ✅ NEW: If still no tenant, create one automatically
            if not tenant_id:
                self.logger.warning(f"⚠️ [AUTH_ABSTRACTION] User {user_id} has no tenant - creating default tenant")
                try:
                    tenant_result = await self._create_tenant_for_user(
                        user_id=user_id,
                        tenant_type="individual",
                        tenant_name=f"Tenant for {email or user_id}",
                        email=email
                    )
                    
                    if tenant_result.get("success"):
                        tenant_id = tenant_result.get("tenant_id")
                        # Link user to tenant with owner role
                        link_result = await self.supabase.link_user_to_tenant(
                            user_id=user_id,
                            tenant_id=tenant_id,
                            role="owner",
                            is_primary=True
                        )
                        if link_result.get("success"):
                            self.logger.info(f"✅ [AUTH_ABSTRACTION] Created and linked tenant {tenant_id} for user {user_id}")
                            # Re-fetch tenant info to get permissions
                            tenant_info = await self.supabase.get_user_tenant_info(user_id)
                        else:
                            self.logger.warning(f"⚠️ [AUTH_ABSTRACTION] Tenant created but linking failed: {link_result.get('error')}")
                    else:
                        self.logger.error(f"❌ [AUTH_ABSTRACTION] Failed to create tenant for user {user_id}: {tenant_result.get('error')}")
                except Exception as tenant_error:
                    self.logger.error(f"❌ [AUTH_ABSTRACTION] Error creating tenant for user {user_id}: {tenant_error}", exc_info=True)
                    # Continue without tenant - graceful degradation
            
            # Get roles and permissions from tenant info (if available)
            if tenant_info and tenant_info.get("tenant_id"):
                roles = tenant_info.get("roles", [])
                permissions = tenant_info.get("permissions", [])
            else:
                # Fallback to user_metadata if tenant_info not available
                roles = user_data.get("user_metadata", {}).get("roles", [])
                permissions = user_data.get("user_metadata", {}).get("permissions", [])
            
            # Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_auth"
            )
            
            self.logger.info(f"✅ [AUTH_ABSTRACTION] User authenticated: {user_id}, tenant: {tenant_id}, permissions: {context.permissions}")
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {str(e)}")
            raise  # Re-raise for service layer to handle
    
    async def get_user_context(self, token: str) -> SecurityContext:
        """
        Get user/tenant context via Supabase API.
        
        ALL infrastructure logic here:
        - Calls Supabase API (get_user)
        - Handles errors
        - Extracts user/tenant/roles
        - Returns SecurityContext
        
        Handler just calls: context = await auth.get_user_context(token)
        
        Use case: ForwardAuth endpoint (needs user context in headers)
        """
        try:
            self.logger.info("🔐 [AUTH_ABSTRACTION] Getting user context (Supabase API)...")
            
            # Infrastructure logic: Supabase API call
            result = await self.supabase.get_user(token)
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"❌ [AUTH_ABSTRACTION] User context failed: {error_msg}")
                raise AuthenticationError(f"User context failed: {error_msg}")
            
            self.logger.info("🔐 [AUTH_ABSTRACTION] User context retrieved (Supabase API)")
            
            # Infrastructure logic: Extract user info
            user_data = result.get("user", {})
            user_id = user_data.get("id")
            email = user_data.get("email") or ""
            user_metadata = user_data.get("user_metadata", {})
            
            # Infrastructure logic: Extract tenant info
            # SupabaseAdapter.get_user() already includes tenant info from database
            tenant_id = (
                user_data.get("tenant_id") or
                user_metadata.get("tenant_id") or
                None
            )
            
            # Infrastructure logic: Extract roles/permissions
            # SupabaseAdapter.get_user() already includes roles/permissions from database
            roles = user_data.get("roles", [])
            permissions = user_data.get("permissions", [])
            
            # Fallback to user_metadata if database query didn't return tenant info
            if not tenant_id:
                tenant_id = user_metadata.get("tenant_id")
            if not roles:
                roles = user_metadata.get("roles", [])
            if not permissions:
                permissions = user_metadata.get("permissions", [])
            
            # Return clean SecurityContext - handler doesn't need to know how we got it
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_user_context"
            )
            
            self.logger.info(f"✅ User context retrieved: user={user_id}, tenant={tenant_id}")
            return context
            
        except AuthenticationError:
            raise  # Re-raise authentication errors
        except Exception as e:
            self.logger.error(f"❌ [AUTH_ABSTRACTION] User context error: {e}", exc_info=True)
            raise AuthenticationError(f"Failed to get user context: {str(e)}")
    
    async def validate_token(self, token: str) -> SecurityContext:
        """
        Validate token using Supabase JWKS local verification (fast, no network calls).
        
        FIX: Now uses local JWT verification via JWKS (Supabase's recommended approach).
        This is much faster than network calls and aligns with best practices.
        
        Falls back to network validation if JWKS is unavailable.
        """
        import time
        validation_start = time.time()
        
        try:
            # Log token info (first 50 chars for debugging, not full token for security)
            token_preview = token[:50] + "..." if len(token) > 50 else token
            self.logger.info(f"🔐 [AUTH_ABSTRACTION] Starting token validation (JWKS)... (token_preview: {token_preview})")
            
            # Use local JWT verification via JWKS (fast, no network calls)
            # This is Supabase's recommended approach for token validation
            verification_start = time.time()
            if hasattr(self.supabase, 'validate_token_local'):
                self.logger.info("🔐 [AUTH_ABSTRACTION] Using local JWKS validation...")
                result = await self.supabase.validate_token_local(token)
                verification_time = time.time() - verification_start
                self.logger.info(f"🔐 [AUTH_ABSTRACTION] JWKS validation completed in {verification_time:.3f}s")
            else:
                # Fallback to network call if local verification not available
                self.logger.warning("⚠️ [AUTH_ABSTRACTION] Local token validation not available, using network call")
                result = await self.supabase.get_user(token)
                verification_time = time.time() - verification_start
                self.logger.warning(f"⚠️ [AUTH_ABSTRACTION] Network validation completed in {verification_time:.3f}s (slower than JWKS)")
            
            if not result.get("success"):
                error_type = result.get("error_type", "unknown")
                error_message = result.get("error", "Unknown error")
                self.logger.error(f"❌ [AUTH_ABSTRACTION] Token validation failed: {error_message} (error_type: {error_type})")
                self.logger.error(f"❌ [AUTH_ABSTRACTION] Full validation result: {result}")
                raise AuthenticationError(f"Token validation failed: {error_message}")
            
            self.logger.info("🔐 [AUTH_ABSTRACTION] Token validation succeeded (JWKS)")
            
            user_data = result.get("user", {})
            
            # Extract user information
            user_id = user_data.get("id")
            email = user_data.get("email", "")
            
            # ✅ NEW: Check tenant status - query user_tenants table first
            tenant_info = await self.supabase.get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
            
            # ✅ NEW: If no tenant_id from database, check user_data/user_metadata as fallback
            if not tenant_id:
                tenant_id = user_data.get("tenant_id") or user_data.get("user_metadata", {}).get("tenant_id")
            
            # ✅ NEW: If still no tenant, create one automatically
            if not tenant_id:
                self.logger.warning(f"⚠️ [AUTH_ABSTRACTION] User {user_id} has no tenant - creating default tenant")
                try:
                    tenant_result = await self._create_tenant_for_user(
                        user_id=user_id,
                        tenant_type="individual",
                        tenant_name=f"Tenant for {email or user_id}",
                        email=email
                    )
                    
                    if tenant_result.get("success"):
                        tenant_id = tenant_result.get("tenant_id")
                        # Link user to tenant with owner role
                        link_result = await self.supabase.link_user_to_tenant(
                            user_id=user_id,
                            tenant_id=tenant_id,
                            role="owner",
                            is_primary=True
                        )
                        if link_result.get("success"):
                            self.logger.info(f"✅ [AUTH_ABSTRACTION] Created and linked tenant {tenant_id} for user {user_id}")
                            # Re-fetch tenant info to get permissions
                            tenant_info = await self.supabase.get_user_tenant_info(user_id)
                        else:
                            self.logger.warning(f"⚠️ [AUTH_ABSTRACTION] Tenant created but linking failed: {link_result.get('error')}")
                    else:
                        self.logger.error(f"❌ [AUTH_ABSTRACTION] Failed to create tenant for user {user_id}: {tenant_result.get('error')}")
                except Exception as tenant_error:
                    self.logger.error(f"❌ [AUTH_ABSTRACTION] Error creating tenant for user {user_id}: {tenant_error}", exc_info=True)
                    # Continue without tenant - graceful degradation
            
            # Get roles and permissions from tenant info (if available)
            if tenant_info and tenant_info.get("tenant_id"):
                roles = tenant_info.get("roles", [])
                permissions = tenant_info.get("permissions", [])
            else:
                # Fallback to user_data if tenant_info not available
                roles = user_data.get("roles", [])
                permissions = user_data.get("permissions", [])
            
            # Diagnostic logging
            self.logger.debug(f"🔍 [AUTH_ABSTRACTION] Extracted from user_data: user_id={user_id}, tenant_id={tenant_id}, roles={roles}, permissions={permissions}")
            
            if not permissions:
                self.logger.warning(f"⚠️ [AUTH_ABSTRACTION] No permissions found for user_id: {user_id}")
                self.logger.warning(f"⚠️ [AUTH_ABSTRACTION] This indicates get_user_tenant_info() may have failed. Check [TENANT_INFO] logs.")
            
            # Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_validation"
            )
            
            total_time = time.time() - validation_start
            self.logger.info(f"✅ [AUTH_ABSTRACTION] Token validated for user: {user_id}, tenant: {tenant_id}, permissions: {len(context.permissions)} permissions (total_time: {total_time:.3f}s)")
            
            return context
            
        except AuthenticationError:
            # Re-raise authentication errors as-is (already logged above)
            raise
        except Exception as e:
            total_time = time.time() - validation_start
            self.logger.error(f"❌ [AUTH_ABSTRACTION] Token validation error (after {total_time:.3f}s): {str(e)}", exc_info=True)
            self.logger.error(f"❌ [AUTH_ABSTRACTION] Exception type: {type(e).__name__}")
            raise AuthenticationError(f"Token validation failed: {str(e)}")
    async def refresh_token(self, refresh_token: str) -> SecurityContext:
        """Refresh token using real Supabase adapter."""
        try:
            # Use real Supabase adapter to refresh token
            result = await self.supabase.refresh_session(refresh_token)
            
            if not result.get("success"):
                raise AuthenticationError(f"Token refresh failed: {result.get('error')}")
            
            user_data = result.get("user", {})
            session_data = result.get("session", {})
            
            # Extract user information
            user_id = user_data.get("id")
            tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
            roles = user_data.get("user_metadata", {}).get("roles", [])
            permissions = user_data.get("user_metadata", {}).get("permissions", [])
            
            # Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=user_data.get("email"),  # Include email if available
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_refresh"
            )
            
            self.logger.info(f"✅ Token refreshed for user: {user_id}")
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Token refresh error: {str(e)}")
            raise  # Re-raise for service layer to handle

    
    async def logout_user(self, token: str) -> bool:
        """Logout user using real Supabase adapter."""
        try:
            # Use real Supabase adapter to logout user
            result = await self.supabase.sign_out(token)
            
            if not result.get("success"):
                self.logger.warning(f"Logout failed: {result.get('error')}")
            
            self.logger.info("✅ User logged out successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Logout error: {str(e)}")
            raise  # Re-raise for service layer to handle
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information using real Supabase adapter."""
        try:
            # Use real Supabase adapter to get user info
            result = await self.supabase.admin_get_user(user_id)
            
            if not result.get("success"):
                raise AuthenticationError(f"Failed to get user info: {result.get('error')}")
            
            user_data = result.get("user", {})
            
            return {
                "user_id": user_data.get("id"),
                "email": user_data.get("email"),
                "tenant_id": user_data.get("user_metadata", {}).get("tenant_id"),
                "roles": user_data.get("user_metadata", {}).get("roles", []),
                "permissions": user_data.get("user_metadata", {}).get("permissions", []),
                "created_at": user_data.get("created_at"),
                "last_sign_in": user_data.get("last_sign_in_at")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get user info error: {str(e)}")
            raise AuthenticationError(f"Failed to get user info: {str(e)}")
    
    async def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """Update user metadata using real Supabase adapter."""
        try:
            # Use real Supabase adapter to update user metadata
            result = await self.supabase.admin_update_user(user_id, {"user_metadata": metadata})
            
            if not result.get("success"):
                self.logger.warning(f"Failed to update user metadata: {result.get('error')}")
            
            self.logger.info(f"✅ User metadata updated for user: {user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Update user metadata error: {str(e)}")
            raise  # Re-raise for service layer to handle
    
    async def register_user(self, credentials: Dict[str, Any]) -> SecurityContext:
        """
        Register new user and create/assign tenant (server-side).
        
        FIX: Now creates tenant server-side during registration instead of
        relying on client-side tenant ID generation.
        """
        try:
            email = credentials.get("email")
            password = credentials.get("password")
            tenant_type = credentials.get("tenant_type", "individual")
            tenant_name = credentials.get("tenant_name", f"Tenant for {email}")
            user_metadata = credentials.get("user_metadata", {})
            
            if not email or not password:
                raise ValueError("Email and password are required")
            
            # Step 1: Create user in Supabase Auth
            result = await self.supabase.sign_up_with_password(
                email=email,
                password=password,
                user_metadata={
                    **user_metadata,
                    "full_name": credentials.get("name", ""),
                    "tenant_type": tenant_type
                }
            )
            
            if not result.get("success"):
                raise AuthenticationError(f"Registration failed: {result.get('error')}")
            
            user_data = result.get("user", {})
            user_id = user_data.get("id")
            
            if not user_id:
                raise AuthenticationError("User created but no user ID returned")
            
            # Step 2: Create tenant (server-side, using service key)
            tenant_result = await self._create_tenant_for_user(
                user_id=user_id,
                tenant_type=tenant_type,
                tenant_name=tenant_name,
                email=email
            )
            
            if not tenant_result.get("success"):
                self.logger.error(f"Failed to create tenant for user {user_id}")
                # User is created but tenant creation failed - this is a problem
                # In production, you might want to rollback user creation
                raise AuthenticationError("Registration succeeded but tenant creation failed")
            
            tenant_id = tenant_result.get("tenant_id")
            
            # Step 3: Link user to tenant
            link_result = await self.supabase.link_user_to_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
                role="owner",
                is_primary=True
            )
            
            if not link_result.get("success"):
                self.logger.warning(f"Failed to link user {user_id} to tenant {tenant_id}")
                # Continue anyway - tenant exists, link can be fixed later
            
            # Step 4: Update user metadata with tenant_id
            update_result = await self.supabase.admin_update_user(user_id, {
                "user_metadata": {
                    **user_metadata,
                    "tenant_id": tenant_id,
                    "primary_tenant_id": tenant_id,
                    "tenant_type": tenant_type,
                    "full_name": credentials.get("name", "")
                }
            })
            
            if not update_result.get("success"):
                self.logger.warning(f"Failed to update user metadata for {user_id}")
                # Continue - metadata update is not critical
            
            # Step 5: Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,  # Email from registration credentials
                roles=["owner"],
                permissions=["read", "write", "admin", "delete"],
                origin="supabase_registration"
            )
            
            self.logger.info(f"✅ User registered with tenant: {user_id} -> {tenant_id}")
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Registration error: {str(e)}")
            raise AuthenticationError(f"Registration failed: {str(e)}")
    
    async def _create_tenant_for_user(self, user_id: str, tenant_type: str, tenant_name: str, email: str) -> Dict[str, Any]:
        """Create tenant for a new user (server-side only)."""
        try:
            # Generate unique slug
            import uuid
            slug = f"tenant-{user_id[:8]}-{uuid.uuid4().hex[:8]}"
            
            tenant_data = {
                "name": tenant_name,
                "slug": slug,
                "type": tenant_type,
                "owner_id": user_id,
                "status": "active",
                "metadata": {
                    "created_by": user_id,
                    "created_for": email
                }
            }
            
            result = await self.supabase.create_tenant(tenant_data)
            
            if not result.get("success"):
                self.logger.error(f"Tenant creation failed: {result.get('error')}")
                return result
            
            self.logger.info(f"✅ Tenant created: {result.get('tenant_id')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating tenant: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "tenant_creation_error"
            }


class AuthenticationError(Exception):
    """Authentication error exception."""
    pass
