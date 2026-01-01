#!/usr/bin/env python3
"""
JWT Adapter - Raw Technology Client

Real JWT token handling with no business logic.
This is Layer 1 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide raw JWT token operations
HOW (Infrastructure Implementation): I use real JWT library with no business logic
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError

logger = logging.getLogger(__name__)

class JWTAdapter:
    """
    Raw JWT token handling - no business logic.
    
    This adapter provides direct access to JWT operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """Initialize JWT adapter with real secret key."""
        self.secret_key = secret_key
        self.algorithm = algorithm
        
        logger.info(f"✅ JWT adapter initialized with algorithm: {algorithm}")
    
    # ============================================================================
    # RAW TOKEN ENCODING OPERATIONS
    # ============================================================================
    
    def encode_token(self, payload: Dict[str, Any], expires_delta: timedelta = None) -> str:
        """Raw JWT token encoding - no business logic."""
        try:
            # Create a copy of the payload to avoid modifying the original
            token_payload = payload.copy()
            
            # Add expiration if specified
            if expires_delta:
                token_payload["exp"] = datetime.utcnow() + expires_delta
            elif "exp" not in token_payload:
                # Default expiration of 1 hour if not specified
                token_payload["exp"] = datetime.utcnow() + timedelta(hours=1)
            
            # Add issued at time
            token_payload["iat"] = datetime.utcnow()
            
            # Encode the token
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"✅ JWT token encoded successfully")
            return token
            
        except Exception as e:
            logger.error(f"JWT encoding error: {str(e)}")
            raise
    
    def encode_token_with_custom_exp(self, payload: Dict[str, Any], exp_timestamp: int) -> str:
        """Raw JWT token encoding with custom expiration timestamp - no business logic."""
        try:
            # Create a copy of the payload to avoid modifying the original
            token_payload = payload.copy()
            
            # Set custom expiration
            token_payload["exp"] = exp_timestamp
            token_payload["iat"] = datetime.utcnow()
            
            # Encode the token
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"✅ JWT token encoded with custom expiration")
            return token
            
        except Exception as e:
            logger.error(f"JWT encoding error: {str(e)}")
            raise
    
    # ============================================================================
    # RAW TOKEN DECODING OPERATIONS
    # ============================================================================
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Raw JWT token decoding - no business logic."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.info(f"✅ JWT token decoded successfully")
            return payload
            
        except ExpiredSignatureError as e:
            logger.error(f"JWT token expired: {str(e)}")
            raise
        except InvalidTokenError as e:
            logger.error(f"JWT token invalid: {str(e)}")
            raise
        except DecodeError as e:
            logger.error(f"JWT token decode error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"JWT decoding error: {str(e)}")
            raise
    
    def decode_token_without_verification(self, token: str) -> Dict[str, Any]:
        """Raw JWT token decoding without verification - no business logic."""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            logger.info(f"✅ JWT token decoded without verification")
            return payload
            
        except Exception as e:
            logger.error(f"JWT decoding without verification error: {str(e)}")
            raise
    
    # ============================================================================
    # RAW TOKEN VALIDATION OPERATIONS
    # ============================================================================
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Raw JWT token validation - no business logic."""
        try:
            payload = self.decode_token(token)
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                return {
                    "valid": False,
                    "error": "Token expired",
                    "expired": True
                }
            
            # Check if token is not yet valid
            nbf = payload.get("nbf")
            if nbf and datetime.utcnow().timestamp() < nbf:
                return {
                    "valid": False,
                    "error": "Token not yet valid",
                    "not_yet_valid": True
                }
            
            return {
                "valid": True,
                "payload": payload,
                "expired": False,
                "not_yet_valid": False
            }
            
        except ExpiredSignatureError:
            return {
                "valid": False,
                "error": "Token expired",
                "expired": True
            }
        except InvalidTokenError as e:
            return {
                "valid": False,
                "error": f"Invalid token: {str(e)}",
                "invalid": True
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Token validation error: {str(e)}",
                "error_type": "validation_error"
            }
    
    def is_token_expired(self, token: str) -> bool:
        """Raw JWT token expiration check - no business logic."""
        try:
            payload = self.decode_token(token)
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow().timestamp() > exp
            return False
            
        except Exception:
            return True  # Consider expired if we can't decode
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """Raw JWT token expiration time retrieval - no business logic."""
        try:
            payload = self.decode_token(token)
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp)
            return None
            
        except Exception:
            return None
    
    # ============================================================================
    # RAW TOKEN REFRESH OPERATIONS
    # ============================================================================
    
    def refresh_token(self, token: str, new_expires_delta: timedelta = None) -> str:
        """Raw JWT token refresh - no business logic."""
        try:
            # Decode the existing token
            payload = self.decode_token(token)
            
            # Remove expiration and issued at times
            payload.pop("exp", None)
            payload.pop("iat", None)
            
            # Set new expiration
            if new_expires_delta:
                payload["exp"] = datetime.utcnow() + new_expires_delta
            else:
                # Default to 1 hour from now
                payload["exp"] = datetime.utcnow() + timedelta(hours=1)
            
            # Encode new token
            new_token = self.encode_token(payload)
            
            logger.info(f"✅ JWT token refreshed successfully")
            return new_token
            
        except Exception as e:
            logger.error(f"JWT token refresh error: {str(e)}")
            raise
    
    # ============================================================================
    # RAW TOKEN UTILITY OPERATIONS
    # ============================================================================
    
    def extract_user_id(self, token: str) -> Optional[str]:
        """Raw JWT token user ID extraction - no business logic."""
        try:
            payload = self.decode_token(token)
            return payload.get("user_id") or payload.get("sub")
            
        except Exception as e:
            logger.error(f"JWT user ID extraction error: {str(e)}")
            return None
    
    def extract_tenant_id(self, token: str) -> Optional[str]:
        """Raw JWT token tenant ID extraction - no business logic."""
        try:
            payload = self.decode_token(token)
            return payload.get("tenant_id")
            
        except Exception as e:
            logger.error(f"JWT tenant ID extraction error: {str(e)}")
            return None
    
    def extract_roles(self, token: str) -> List[str]:
        """Raw JWT token roles extraction - no business logic."""
        try:
            payload = self.decode_token(token)
            roles = payload.get("roles", [])
            if isinstance(roles, str):
                # Handle comma-separated roles
                roles = [role.strip() for role in roles.split(",")]
            return roles
            
        except Exception as e:
            logger.error(f"JWT roles extraction error: {str(e)}")
            return []
    
    def extract_permissions(self, token: str) -> List[str]:
        """Raw JWT token permissions extraction - no business logic."""
        try:
            payload = self.decode_token(token)
            permissions = payload.get("permissions", [])
            if isinstance(permissions, str):
                # Handle comma-separated permissions
                permissions = [perm.strip() for perm in permissions.split(",")]
            return permissions
            
        except Exception as e:
            logger.error(f"JWT permissions extraction error: {str(e)}")
            return []
    
    # ============================================================================
    # RAW TOKEN CREATION OPERATIONS
    # ============================================================================
    
    def create_access_token(self, user_id: str, tenant_id: str = None, roles: List[str] = None, permissions: List[str] = None, expires_delta: timedelta = None) -> str:
        """Raw JWT access token creation - no business logic."""
        try:
            payload = {
                "user_id": user_id,
                "token_type": "access"
            }
            
            if tenant_id:
                payload["tenant_id"] = tenant_id
            
            if roles:
                payload["roles"] = roles
            
            if permissions:
                payload["permissions"] = permissions
            
            # Set expiration
            if expires_delta:
                payload["exp"] = datetime.utcnow() + expires_delta
            else:
                # Default to 1 hour for access tokens
                payload["exp"] = datetime.utcnow() + timedelta(hours=1)
            
            token = self.encode_token(payload)
            
            logger.info(f"✅ JWT access token created for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"JWT access token creation error: {str(e)}")
            raise
    
    def create_refresh_token(self, user_id: str, tenant_id: str = None, expires_delta: timedelta = None) -> str:
        """Raw JWT refresh token creation - no business logic."""
        try:
            payload = {
                "user_id": user_id,
                "token_type": "refresh"
            }
            
            if tenant_id:
                payload["tenant_id"] = tenant_id
            
            # Set expiration (refresh tokens last longer)
            if expires_delta:
                payload["exp"] = datetime.utcnow() + expires_delta
            else:
                # Default to 7 days for refresh tokens
                payload["exp"] = datetime.utcnow() + timedelta(days=7)
            
            token = self.encode_token(payload)
            
            logger.info(f"✅ JWT refresh token created for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"JWT refresh token creation error: {str(e)}")
            raise
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    def test_connection(self) -> Dict[str, Any]:
        """Test JWT adapter - no business logic."""
        try:
            # Test with a simple token creation and decoding
            test_payload = {"test": "value", "user_id": "test_user"}
            token = self.encode_token(test_payload)
            decoded = self.decode_token(token)
            
            return {
                "success": True,
                "message": "JWT adapter working correctly",
                "algorithm": self.algorithm,
                "test_token_created": bool(token),
                "test_token_decoded": decoded.get("test") == "value"
            }
        except Exception as e:
            logger.error(f"JWT adapter test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "algorithm": self.algorithm
            }
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get JWT adapter information - no business logic."""
        return {
            "algorithm": self.algorithm,
            "has_secret_key": bool(self.secret_key),
            "secret_key_length": len(self.secret_key) if self.secret_key else 0
        }
