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
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from supabase import create_client, Client
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
# Note: Supabase client handles auth errors internally
# We catch generic exceptions and identify auth errors by message/type
class SupabaseAuthError(Exception):
    """Custom exception for Supabase authentication errors."""
    pass

logger = logging.getLogger(__name__)

def _is_auth_error(error: Exception) -> bool:
    """Check if an exception is an auth-related error."""
    error_str = str(error).lower()
    return (
        "auth" in error_str or
        "invalid credentials" in error_str or
        ("email" in error_str and "password" in error_str) or
        ("token" in error_str and ("invalid" in error_str or "expired" in error_str)) or
        "unauthorized" in error_str or
        "forbidden" in error_str
    )

class SupabaseAdapter:
    """
    Raw Supabase client wrapper - no business logic.
    
    This adapter provides direct access to Supabase operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, url: str, anon_key: str, service_key: str = None, config_adapter = None):
        """
        Initialize Supabase adapter with real credentials.
        
        Args:
            url: Supabase project URL
            anon_key: Supabase anonymous/public key
            service_key: Supabase service role key (optional)
            config_adapter: Optional ConfigAdapter for reading configuration (preferred over os.getenv)
        """
        # Normalize URL - remove trailing slashes
        self.url = url.rstrip('/') if url else url
        self.anon_key = anon_key
        self.service_key = service_key
        self.config_adapter = config_adapter
        
        # Log service_key status for debugging
        if service_key:
            logger.info(f"✅ [SUPABASE_ADAPTER] Service key provided - service_client will be available for database queries")
        else:
            logger.warning("⚠️ [SUPABASE_ADAPTER] Service key NOT provided - service_client will fallback to anon_client")
            logger.warning("⚠️ [SUPABASE_ADAPTER] This may cause get_user_tenant_info() to fail. Set SUPABASE_SERVICE_KEY or SUPABASE_SECRET_KEY in environment.")
        
        # Create clients
        self.anon_client: Client = create_client(self.url, anon_key)
        self.service_client: Client = create_client(self.url, service_key) if service_key else self.anon_client
        
        # Log client initialization status
        if self.service_client and service_key:
            logger.debug(f"✅ [SUPABASE_ADAPTER] service_client initialized with service_key (can query user_tenants table)")
        else:
            logger.debug(f"⚠️ [SUPABASE_ADAPTER] service_client initialized as anon_client (may not be able to query user_tenants table)")
        
        # Initialize JWKS adapter for local JWT verification
        # Use ConfigAdapter (required, no fallback to os.getenv)
        try:
            from .supabase_jwks_adapter import SupabaseJWKSAdapter
            
            # Get JWKS URL from ConfigAdapter (required)
            if config_adapter:
                jwks_url = config_adapter.get("SUPABASE_JWKS_URL")
            else:
                raise ValueError(
                    "ConfigAdapter is required for Supabase adapter. "
                    "Pass config_adapter from Public Works Foundation."
                )
            
            if jwks_url:
                self.jwks_adapter = SupabaseJWKSAdapter(jwks_url=jwks_url, config_adapter=config_adapter)
                logger.info(f"✅ Supabase adapter initialized with URL: {self.url} (JWKS enabled via SUPABASE_JWKS_URL)")
            else:
                self.jwks_adapter = SupabaseJWKSAdapter(supabase_url=self.url, config_adapter=config_adapter)
                logger.info(f"✅ Supabase adapter initialized with URL: {self.url} (JWKS enabled, constructed URL)")
            
            # Store JWT issuer for validation (from ConfigAdapter)
            if config_adapter:
                self.jwt_issuer = config_adapter.get("SUPABASE_JWT_ISSUER")
            else:
                raise ValueError(
                    "ConfigAdapter is required for Supabase adapter. "
                    "Pass config_adapter from Public Works Foundation."
                )
            
            if self.jwt_issuer:
                logger.info(f"✅ JWT issuer configured: {self.jwt_issuer}")
            else:
                logger.warning("⚠️ SUPABASE_JWT_ISSUER not set - issuer validation will be skipped")
        except ImportError:
            self.jwks_adapter = None
            self.jwt_issuer = None
            logger.warning("⚠️ JWKS adapter not available - local JWT verification disabled")
            logger.info(f"✅ Supabase adapter initialized with URL: {self.url} (JWKS disabled)")
    
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
        except Exception as e:
            if _is_auth_error(e):
                logger.error(f"Supabase auth error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
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
        except Exception as e:
            if _is_auth_error(e):
                logger.error(f"Supabase signup error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
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
        except Exception as e:
            if _is_auth_error(e):
                logger.error(f"Supabase refresh error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
                logger.error(f"Unexpected error in refresh_session: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "unexpected_error"
                }
    
    async def validate_token_local(self, access_token: str) -> Dict[str, Any]:
        """
        Validate JWT token locally using JWKS (no network calls to Supabase API).
        
        This is Supabase's recommended approach for token validation.
        Uses JWKS endpoint to get public keys and verifies JWT signature locally.
        
        Benefits:
        - Fast (no network calls)
        - Reliable (no dependency on Supabase API)
        - Best practice (Supabase's recommended approach)
        - Secure (RS256 asymmetric keys)
        
        Returns:
            Dict with success, user data, or error
        """
        import time
        validation_start = time.time()
        
        if not self.jwks_adapter:
            # Fallback to network call if JWKS not available
            logger.warning("⚠️ [JWKS] JWKS adapter not available, falling back to network validation")
            network_start = time.time()
            result = await self.get_user(access_token)
            network_time = time.time() - network_start
            logger.warning(f"⚠️ [JWKS] Network validation completed in {network_time:.3f}s (fallback mode)")
            return result
        
        try:
            token_preview = access_token[:50] + "..." if len(access_token) > 50 else access_token
            logger.info(f"🔐 [JWKS] Starting local token validation... (token_preview: {token_preview})")
            
            # Decode JWT header to get kid (key ID)
            header_start = time.time()
            try:
                unverified_header = jwt.get_unverified_header(access_token)
                kid = unverified_header.get("kid")
                header_time = time.time() - header_start
                logger.info(f"🔐 [JWKS] JWT header decoded in {header_time:.3f}s, kid (key ID): {kid}")
            except Exception as header_error:
                logger.error(f"❌ [JWKS] Failed to decode JWT header: {header_error}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Invalid token: failed to decode header - {str(header_error)}",
                    "error_type": "auth_error"
                }
            
            if not kid:
                logger.error("❌ [JWKS] JWT missing 'kid' in header")
                logger.error(f"❌ [JWKS] JWT header contents: {unverified_header}")
                return {
                    "success": False,
                    "error": "Invalid token: missing key ID",
                    "error_type": "auth_error"
                }
            
            # Get JWKS (cached)
            jwks_start = time.time()
            logger.info("🔐 [JWKS] Fetching JWKS (may be cached)...")
            try:
                jwks = await self.jwks_adapter.get_jwks()
                jwks_time = time.time() - jwks_start
                logger.info(f"🔐 [JWKS] JWKS fetched in {jwks_time:.3f}s: {len(jwks.get('keys', []))} keys available")
            except Exception as jwks_error:
                logger.error(f"❌ [JWKS] Failed to fetch JWKS: {jwks_error}", exc_info=True)
                return {
                    "success": False,
                    "error": f"JWKS fetch failed: {str(jwks_error)}",
                    "error_type": "jwks_error"
                }
            
            # Get public key by kid
            key_lookup_start = time.time()
            key_data = self.jwks_adapter.get_key_by_kid(kid, jwks)
            key_lookup_time = time.time() - key_lookup_start
            logger.info(f"🔐 [JWKS] Key lookup for kid '{kid}' completed in {key_lookup_time:.3f}s: {'FOUND' if key_data else 'NOT_FOUND'}")
            
            if not key_data:
                logger.error(f"❌ [JWKS] Key with kid '{kid}' not found in JWKS")
                logger.error(f"❌ [JWKS] Available kids in JWKS: {[k.get('kid') for k in jwks.get('keys', [])]}")
                # Try refreshing JWKS (key rotation)
                logger.info("🔄 [JWKS] Attempting to refresh JWKS (key rotation)...")
                refresh_start = time.time()
                try:
                    jwks = await self.jwks_adapter.refresh_jwks()
                    refresh_time = time.time() - refresh_start
                    logger.info(f"🔄 [JWKS] JWKS refresh completed in {refresh_time:.3f}s")
                    key_data = self.jwks_adapter.get_key_by_kid(kid, jwks)
                    if key_data:
                        logger.info(f"✅ [JWKS] Key found after refresh!")
                    else:
                        logger.error(f"❌ [JWKS] Key still not found after refresh. Available kids: {[k.get('kid') for k in jwks.get('keys', [])]}")
                except Exception as refresh_error:
                    logger.error(f"❌ [JWKS] Failed to refresh JWKS: {refresh_error}", exc_info=True)
                
                if not key_data:
                    total_time = time.time() - validation_start
                    logger.error(f"❌ [JWKS] Token validation failed after {total_time:.3f}s: key not found")
                    return {
                        "success": False,
                        "error": "Invalid token: key not found in JWKS",
                        "error_type": "auth_error"
                    }
            
            # Convert JWK to public key (supports both RS256/RSA and ES256/EC)
            import base64
            from cryptography.hazmat.primitives.asymmetric import rsa, ec
            from cryptography.hazmat.backends import default_backend
            
            key_type = key_data.get("kty")  # "RSA" or "EC"
            algorithm = key_data.get("alg")  # "RS256" or "ES256"
            
            if key_type == "EC" or algorithm == "ES256":
                # Elliptic Curve (ES256) - Supabase uses this
                x_bytes = base64.urlsafe_b64decode(key_data["x"] + "==")
                y_bytes = base64.urlsafe_b64decode(key_data["y"] + "==")
                
                # Convert to integers
                x_int = int.from_bytes(x_bytes, "big")
                y_int = int.from_bytes(y_bytes, "big")
                
                # Get curve type (default to P-256 for ES256)
                crv = key_data.get("crv", "P-256")
                if crv == "P-256":
                    curve = ec.SECP256R1()
                elif crv == "P-384":
                    curve = ec.SECP384R1()
                elif crv == "P-521":
                    curve = ec.SECP521R1()
                else:
                    raise ValueError(f"Unsupported curve: {crv}")
                
                # Create EC public key
                public_key = ec.EllipticCurvePublicNumbers(x_int, y_int, curve).public_key(default_backend())
                logger.debug(f"✅ Created EC public key (ES256) for curve {crv}")
                
            elif key_type == "RSA" or algorithm == "RS256":
                # RSA (RS256) - legacy support
                n_bytes = base64.urlsafe_b64decode(key_data["n"] + "==")
                e_bytes = base64.urlsafe_b64decode(key_data["e"] + "==")
                
                # Convert to integers
                n_int = int.from_bytes(n_bytes, "big")
                e_int = int.from_bytes(e_bytes, "big")
                
                # Create RSA public key
                public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key(default_backend())
                logger.debug("✅ Created RSA public key (RS256)")
            else:
                raise ValueError(f"Unsupported key type: {key_type} or algorithm: {algorithm}")
            
            # Verify and decode JWT (PyJWT works with cryptography RSA keys directly)
            # Validate issuer if configured (from ConfigAdapter via jwt_issuer attribute)
            verify_options = {"verify_exp": True, "verify_aud": True}
            issuer = getattr(self, 'jwt_issuer', None)
            
            # Determine algorithm from key type
            if key_type == "EC" or algorithm == "ES256":
                jwt_algorithm = "ES256"
            else:
                jwt_algorithm = "RS256"
            
            logger.info(f"🔐 [JWKS] Verifying JWT with algorithm={jwt_algorithm}, issuer={issuer or 'NOT_SET'}")
            
            verify_start = time.time()
            try:
                payload = jwt.decode(
                    access_token,
                    public_key,
                    algorithms=[jwt_algorithm],  # ES256 for Supabase, RS256 for legacy
                    audience="authenticated",  # Supabase JWT audience
                    issuer=issuer if issuer else None,  # Validate issuer if configured
                    options=verify_options
                )
                verify_time = time.time() - verify_start
                logger.info(f"✅ [JWKS] JWT signature verified successfully in {verify_time:.3f}s! User ID: {payload.get('sub', 'N/A')}")
                
                # Log issuer validation
                if issuer:
                    token_issuer = payload.get("iss")
                    if token_issuer != issuer:
                        logger.error(f"❌ JWT issuer mismatch: expected '{issuer}', got '{token_issuer}'")
                        return {
                            "success": False,
                            "error": f"Invalid token: issuer mismatch (expected '{issuer}')",
                            "error_type": "auth_error"
                        }
                    logger.debug(f"✅ JWT issuer validated: {token_issuer}")
            except ExpiredSignatureError:
                verify_time = time.time() - verify_start
                logger.error(f"❌ [JWKS] JWT validation failed after {verify_time:.3f}s: Token expired")
                return {
                    "success": False,
                    "error": "Token expired",
                    "error_type": "auth_error"
                }
            except InvalidTokenError as e:
                verify_time = time.time() - verify_start
                logger.error(f"❌ [JWKS] JWT validation failed after {verify_time:.3f}s: {e}", exc_info=True)
                logger.error(f"❌ [JWKS] InvalidTokenError details: {type(e).__name__}, message: {str(e)}")
                return {
                    "success": False,
                    "error": f"Invalid token: {str(e)}",
                    "error_type": "auth_error"
                }
            
            # Extract user information from JWT payload
            user_id = payload.get("sub")  # Supabase uses 'sub' for user_id
            email = payload.get("email")
            user_metadata = payload.get("user_metadata", {})
            
            logger.info(f"🔍 [JWKS_DEBUG] Extracted user_id from JWT: {user_id}, email: {email}")
            
            if not user_id:
                logger.error("❌ [JWKS_DEBUG] JWT payload missing 'sub' (user_id)")
                return {
                    "success": False,
                    "error": "Invalid token: missing user ID",
                    "error_type": "auth_error"
                }
            
            # Get tenant information from database (still needed)
            logger.info(f"🔍 [JWKS_DEBUG] Fetching tenant info for user_id: {user_id}")
            tenant_info = await self.get_user_tenant_info(user_id)
            logger.info(f"🔍 [JWKS_DEBUG] Tenant info result: tenant_id={tenant_info.get('tenant_id')}, roles={tenant_info.get('roles')}, permissions={tenant_info.get('permissions')}")
            
            # Build user dict
            user_dict = {
                "id": user_id,
                "email": email,
                "user_metadata": user_metadata,
                "tenant_id": tenant_info.get("tenant_id") or user_metadata.get("tenant_id"),
                "primary_tenant_id": tenant_info.get("primary_tenant_id") or user_metadata.get("primary_tenant_id"),
                "tenant_type": tenant_info.get("tenant_type", "individual"),
                "roles": tenant_info.get("roles", []),
                "permissions": tenant_info.get("permissions", [])  # ✅ This should have permissions from get_user_tenant_info
            }
            
            total_time = time.time() - validation_start
            logger.info(f"✅ [JWKS] Token validated locally for user: {user_id}, tenant_id: {user_dict.get('tenant_id')}, {len(user_dict.get('permissions', []))} permissions (total_time: {total_time:.3f}s)")
            
            return {
                "success": True,
                "user": user_dict,
                "access_token": access_token
            }
            
        except Exception as e:
            total_time = time.time() - validation_start
            logger.error(f"❌ [JWKS] Local token validation error after {total_time:.3f}s: {e}", exc_info=True)
            logger.error(f"❌ [JWKS] Exception type: {type(e).__name__}")
            # Fallback to network call on error
            logger.warning("⚠️ Falling back to network validation due to local validation error")
            return await self.get_user(access_token)
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Raw user retrieval with Supabase - enhanced with tenant context.
        
        FIX: Now fetches tenant information from database, not just metadata.
        
        SECURITY: Uses Supabase's official auth.get_user() API call.
        Adds timeout protection to prevent ForwardAuth from hanging.
        
        NOTE: This method makes a network call. For better performance,
        use validate_token_local() which uses JWKS for local verification.
        """
        try:
            import asyncio
            
            # Use Supabase's official get_user method (validates token via network call)
            # This is the correct Supabase way - we're just adding timeout protection
            # Wrap in timeout to prevent ForwardAuth from hanging (2 second timeout)
            try:
                # Check if get_user is async (it's likely synchronous in supabase-py)
                # Run in thread pool to avoid blocking, with timeout
                user_response = await asyncio.wait_for(
                    asyncio.to_thread(self.anon_client.auth.get_user, access_token),
                    timeout=2.0  # 2 second timeout for ForwardAuth
                )
            except asyncio.TimeoutError:
                logger.error("⚠️ Supabase get_user timeout after 2 seconds - Supabase API may be slow or unavailable")
                return {
                    "success": False,
                    "error": "Token validation timeout - Supabase API slow or unavailable",
                    "error_type": "timeout"
                }
            
            if not user_response.user:
                return {
                    "success": False,
                    "error": "Invalid token",
                    "error_type": "auth_error"
                }
            
            user = user_response.user
            user_id = user.id
            
            # Get tenant information from database (not just metadata)
            tenant_info = await self.get_user_tenant_info(user_id)
            
            # Merge tenant info with user data
            user_dict = user.__dict__ if hasattr(user, '__dict__') else {
                "id": user.id,
                "email": user.email,
                "user_metadata": user.user_metadata or {}
            }
            
            # Add tenant context
            user_dict["tenant_id"] = tenant_info.get("tenant_id")
            user_dict["primary_tenant_id"] = tenant_info.get("primary_tenant_id")
            user_dict["tenant_type"] = tenant_info.get("tenant_type", "individual")
            user_dict["roles"] = tenant_info.get("roles", [])
            user_dict["permissions"] = tenant_info.get("permissions", [])
            
            return {
                "success": True,
                "user": user_dict,
                "access_token": access_token
            }
        except Exception as e:
            if _is_auth_error(e):
                logger.error(f"Supabase get_user error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
                logger.error(f"Unexpected error in get_user: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "unexpected_error"
                }
    
    async def get_user_tenant_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's tenant information from database.
        
        Public method to allow auth abstractions to check tenant status.
        Returns empty dict if no tenant found.
        """
        try:
            # Use service_client to query user_tenants table (requires service key)
            if not self.service_client:
                logger.warning("⚠️ [TENANT_INFO] Service client not available - service_key may not be configured. Cannot query user_tenants table.")
                logger.warning("⚠️ [TENANT_INFO] Check that SUPABASE_SERVICE_KEY or SUPABASE_SECRET_KEY is set in environment.")
                return {}
            
            logger.debug(f"🔍 [TENANT_INFO] Querying user_tenants table for user_id: {user_id}")
            try:
                response = self.service_client.table("user_tenants").select(
                    "tenant_id, role, is_primary, tenants(type, name, status)"
                ).eq("user_id", user_id).eq("is_primary", True).execute()
                
                logger.debug(f"🔍 [TENANT_INFO] Database query returned {len(response.data) if response.data else 0} records")
            except Exception as db_error:
                logger.error(f"❌ [TENANT_INFO] Database query failed for user_id {user_id}: {db_error}", exc_info=True)
                # Try fallback to user_metadata
                response = type('obj', (object,), {'data': []})()  # Empty response object
            
            if not response.data:
                # Fallback: check user_metadata
                logger.warning(f"⚠️ [TENANT_INFO] No tenant data found in user_tenants table for user_id: {user_id}, trying metadata fallback")
                try:
                    user_response = self.service_client.auth.admin.get_user_by_id(user_id)
                    user_metadata = user_response.user.user_metadata or {}
                    logger.info(f"✅ [TENANT_INFO] Using metadata fallback for user_id: {user_id}")
                    logger.debug(f"🔍 [TENANT_INFO] Metadata fallback - tenant_id: {user_metadata.get('tenant_id')}, roles: {user_metadata.get('roles')}, permissions: {user_metadata.get('permissions')}")
                    return {
                        "tenant_id": user_metadata.get("tenant_id"),
                        "primary_tenant_id": user_metadata.get("primary_tenant_id"),
                        "tenant_type": user_metadata.get("tenant_type", "individual"),
                        "roles": user_metadata.get("roles", []),
                        "permissions": user_metadata.get("permissions", [])
                    }
                except Exception as e:
                    logger.warning(f"⚠️ [TENANT_INFO] Could not get user metadata for user_id {user_id}: {e}")
                    logger.warning(f"⚠️ [TENANT_INFO] Returning empty dict - permissions will be empty")
                    return {}
            
            tenant_data = response.data[0]
            tenant_info = tenant_data.get("tenants", {})
            
            # Map role to permissions
            role = tenant_data.get("role", "member")
            permissions = self._get_permissions_for_role(role)
            
            logger.info(f"✅ [TENANT_INFO] Found tenant info for user_id: {user_id}, tenant_id: {tenant_data.get('tenant_id')}, role: {role}, permissions: {permissions}")
            
            return {
                "tenant_id": tenant_data["tenant_id"],
                "primary_tenant_id": tenant_data["tenant_id"],
                "tenant_type": tenant_info.get("type", "individual"),
                "roles": [role],
                "permissions": permissions
            }
            
        except Exception as e:
            logger.error(f"❌ [TENANT_INFO] Error getting tenant info for user_id {user_id}: {e}", exc_info=True)
            return {}
    
    def _get_permissions_for_role(self, role: str) -> List[str]:
        """Get permissions for a given role."""
        role_permissions = {
            "owner": ["read", "write", "admin", "delete"],
            "admin": ["read", "write", "admin"],
            "member": ["read", "write"],
            "viewer": ["read"]
        }
        return role_permissions.get(role, ["read"])
    
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
        except Exception as e:
            if _is_auth_error(e):
                logger.error(f"Supabase sign_out error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
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
    # TENANT MANAGEMENT OPERATIONS (using service key)
    # ============================================================================
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tenant using service key (server-side only)."""
        try:
            if not self.service_client:
                return {
                    "success": False,
                    "error": "Service client not available",
                    "error_type": "config_error"
                }
            
            response = self.service_client.table("tenants").insert(tenant_data).execute()
            
            if not response.data:
                return {
                    "success": False,
                    "error": "Failed to create tenant",
                    "error_type": "database_error"
                }
            
            return {
                "success": True,
                "tenant": response.data[0],
                "tenant_id": response.data[0]["id"]
            }
        except Exception as e:
            logger.error(f"Supabase create_tenant error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "database_error"
            }
    
    async def link_user_to_tenant(self, user_id: str, tenant_id: str, role: str = "member", is_primary: bool = False) -> Dict[str, Any]:
        """Link a user to a tenant using service key (server-side only)."""
        try:
            if not self.service_client:
                return {
                    "success": False,
                    "error": "Service client not available",
                    "error_type": "config_error"
                }
            
            # If setting as primary, unset other primary tenants for this user
            if is_primary:
                self.service_client.table("user_tenants").update({
                    "is_primary": False
                }).eq("user_id", user_id).execute()
            
            response = self.service_client.table("user_tenants").insert({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role": role,
                "is_primary": is_primary
            }).execute()
            
            if not response.data:
                return {
                    "success": False,
                    "error": "Failed to link user to tenant",
                    "error_type": "database_error"
                }
            
            return {
                "success": True,
                "user_tenant": response.data[0]
            }
        except Exception as e:
            logger.error(f"Supabase link_user_to_tenant error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "database_error"
            }
    
    async def get_tenant_by_id(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information by ID."""
        try:
            if not self.service_client:
                return {
                    "success": False,
                    "error": "Service client not available",
                    "error_type": "config_error"
                }
            
            response = self.service_client.table("tenants").select("*").eq("id", tenant_id).execute()
            
            if not response.data:
                return {
                    "success": False,
                    "error": "Tenant not found",
                    "error_type": "not_found"
                }
            
            return {
                "success": True,
                "tenant": response.data[0]
            }
        except Exception as e:
            logger.error(f"Supabase get_tenant_by_id error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "database_error"
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
