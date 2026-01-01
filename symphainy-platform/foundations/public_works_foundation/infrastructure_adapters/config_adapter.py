#!/usr/bin/env python3
"""
Config Adapter - Raw Technology Client

Real configuration access with no business logic.
This is Layer 1 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide raw configuration operations
HOW (Infrastructure Implementation): I use real environment variables with no business logic
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigAdapter:
    """
    Raw configuration access - no business logic.
    
    This adapter provides direct access to configuration operations without
    any business logic or abstraction. It's the raw technology layer.
    
    BREAKING CHANGE: Now requires UnifiedConfigurationManager to read config.
    This ensures all config values loaded from files are accessible.
    """
    
    def __init__(self, unified_config_manager: Any = None, env_file_path: str = None):
        """
        Initialize Config adapter with UnifiedConfigurationManager.
        
        BREAKING: unified_config_manager is now required (no default).
        This breaks all code that creates ConfigAdapter() without UnifiedConfigurationManager.
        
        Args:
            unified_config_manager: UnifiedConfigurationManager instance (REQUIRED)
            env_file_path: Optional env file path (deprecated, kept for backward compatibility)
        """
        if not unified_config_manager:
            raise ValueError(
                "ConfigAdapter requires UnifiedConfigurationManager. "
                "Pass UnifiedConfigurationManager instance to constructor. "
                "Example: ConfigAdapter(unified_config_manager=unified_config)"
            )
        
        self.config_manager = unified_config_manager
        self.env_file_path = env_file_path  # Deprecated, kept for compatibility
        self.config_cache = {}  # Deprecated, kept for compatibility
        
        logger.info(f"✅ Config adapter initialized with UnifiedConfigurationManager")
    
    # ============================================================================
    # RAW ENVIRONMENT VARIABLE OPERATIONS
    # ============================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Raw configuration retrieval - no business logic.
        
        BREAKING: Now reads from UnifiedConfigurationManager (not os.getenv()).
        This ensures all config values loaded from files are accessible.
        """
        try:
            # Read from UnifiedConfigurationManager
            value = self.config_manager.get(key, default)
            return value
        except Exception as e:
            logger.error(f"Config GET error for key {key}: {str(e)}")
            return default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Raw integer configuration retrieval - no business logic."""
        try:
            value = self.config_manager.get(key)
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError) as e:
            logger.error(f"Config GET_INT error for key {key}: {str(e)}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Raw float configuration retrieval - no business logic."""
        try:
            value = self.config_manager.get(key)
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError) as e:
            logger.error(f"Config GET_FLOAT error for key {key}: {str(e)}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Raw boolean configuration retrieval - no business logic."""
        try:
            value = self.config_manager.get(key)
            if value is None:
                return default
            # Handle both string and boolean values
            if isinstance(value, bool):
                return value
            return str(value).lower() in ('true', '1', 'yes', 'on')
        except Exception as e:
            logger.error(f"Config GET_BOOL error for key {key}: {str(e)}")
            return default
    
    def get_list(self, key: str, default: List[str] = None, separator: str = ",") -> List[str]:
        """Raw list configuration retrieval - no business logic."""
        try:
            value = self.config_manager.get(key)
            if value is None:
                return default or []
            # Handle both string and list values
            if isinstance(value, list):
                return value
            return [item.strip() for item in str(value).split(separator) if item.strip()]
        except Exception as e:
            logger.error(f"Config GET_LIST error for key {key}: {str(e)}")
            return default or []
    
    # ============================================================================
    # RAW CONFIGURATION FILE OPERATIONS
    # ============================================================================
    
    def load_env_file(self, file_path: str = None) -> Dict[str, str]:
        """Raw environment file loading - no business logic."""
        try:
            env_file = file_path or self.env_file_path
            if not env_file or not os.path.exists(env_file):
                return {}
            
            config = {}
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
            
            logger.info(f"✅ Loaded {len(config)} variables from {env_file}")
            return config
            
        except Exception as e:
            logger.error(f"Config file loading error: {str(e)}")
            return {}
    
    def set_env_from_file(self, file_path: str = None) -> bool:
        """Raw environment variable setting from file - no business logic."""
        try:
            config = self.load_env_file(file_path)
            for key, value in config.items():
                os.environ[key] = value
            
            logger.info(f"✅ Set {len(config)} environment variables from file")
            return True
            
        except Exception as e:
            logger.error(f"Config file setting error: {str(e)}")
            return False
    
    # ============================================================================
    # RAW SUPABASE CONFIGURATION OPERATIONS
    # ============================================================================
    
    def get_supabase_config(self) -> Dict[str, Any]:
        """
        Raw Supabase configuration retrieval - no business logic.
        
        Supports both new and legacy naming conventions.
        """
        return {
            "url": self.get("SUPABASE_URL"),
            # New naming (preferred)
            "publishable_key": self.get("SUPABASE_PUBLISHABLE_KEY"),
            "secret_key": self.get("SUPABASE_SECRET_KEY"),
            # Legacy naming (for backward compatibility)
            "anon_key": self.get("SUPABASE_ANON_KEY"),
            "service_key": self.get("SUPABASE_SERVICE_KEY"),
            # Generic fallback
            "key": self.get("SUPABASE_KEY")
        }
    
    def get_supabase_url(self) -> Optional[str]:
        """Raw Supabase URL retrieval - no business logic."""
        return self.get("SUPABASE_URL")
    
    def get_supabase_anon_key(self) -> Optional[str]:
        """
        Raw Supabase anon/publishable key retrieval - no business logic.
        
        Supports both new and legacy naming:
        - New: SUPABASE_PUBLISHABLE_KEY (preferred)
        - Legacy: SUPABASE_ANON_KEY, SUPABASE_KEY (fallback)
        """
        return (
            self.get("SUPABASE_PUBLISHABLE_KEY") or  # New naming (preferred)
            self.get("SUPABASE_ANON_KEY") or         # Legacy naming
            self.get("SUPABASE_KEY")                 # Generic fallback
        )
    
    def get_supabase_service_key(self) -> Optional[str]:
        """
        Raw Supabase service/secret key retrieval - no business logic.
        
        Supports both new and legacy naming:
        - New: SUPABASE_SECRET_KEY (preferred)
        - Legacy: SUPABASE_SERVICE_KEY, SUPABASE_KEY (fallback)
        """
        return (
            self.get("SUPABASE_SECRET_KEY") or       # New naming (preferred)
            self.get("SUPABASE_SERVICE_KEY") or      # Legacy naming
            self.get("SUPABASE_KEY")                 # Generic fallback
        )
    
    # ============================================================================
    # RAW REDIS CONFIGURATION OPERATIONS
    # ============================================================================
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Raw Redis configuration retrieval - no business logic."""
        return {
            "host": self.get("REDIS_HOST", "localhost"),
            "port": self.get_int("REDIS_PORT", 6379),
            "db": self.get_int("REDIS_DB", 0),
            "password": self.get("REDIS_PASSWORD"),
            "url": self.get("REDIS_URL")
        }
    
    def get_redis_host(self) -> str:
        """Raw Redis host retrieval - no business logic."""
        return self.get("REDIS_HOST", "localhost")
    
    def get_redis_port(self) -> int:
        """Raw Redis port retrieval - no business logic."""
        return self.get_int("REDIS_PORT", 6379)
    
    def get_redis_db(self) -> int:
        """Raw Redis database retrieval - no business logic."""
        return self.get_int("REDIS_DB", 0)
    
    def get_redis_password(self) -> Optional[str]:
        """Raw Redis password retrieval - no business logic."""
        return self.get("REDIS_PASSWORD")
    
    def get_redis_url(self) -> Optional[str]:
        """Raw Redis URL retrieval - no business logic."""
        return self.get("REDIS_URL")
    
    # ============================================================================
    # RAW JWT CONFIGURATION OPERATIONS
    # ============================================================================
    
    def get_jwt_config(self) -> Dict[str, Any]:
        """Raw JWT configuration retrieval - no business logic."""
        return {
            "secret_key": self.get("JWT_SECRET_KEY") or self.get("JWT_SECRET") or "default-jwt-secret",
            "algorithm": self.get("JWT_ALGORITHM", "HS256"),
            "expiration": self.get_int("JWT_EXPIRATION", 3600),
            "refresh_expiration": self.get_int("JWT_REFRESH_EXPIRATION", 604800)  # 7 days
        }
    
    def get_jwt_secret_key(self) -> Optional[str]:
        """Raw JWT secret key retrieval - no business logic."""
        return self.get("JWT_SECRET_KEY")
    
    def get_jwt_algorithm(self) -> str:
        """Raw JWT algorithm retrieval - no business logic."""
        return self.get("JWT_ALGORITHM", "HS256")
    
    def get_jwt_expiration(self) -> int:
        """Raw JWT expiration retrieval - no business logic."""
        return self.get_int("JWT_EXPIRATION", 3600)
    
    # ============================================================================
    # RAW MULTI-TENANT CONFIGURATION OPERATIONS
    # ============================================================================
    
    def get_multi_tenant_config(self) -> Dict[str, Any]:
        """Raw multi-tenant configuration retrieval - no business logic."""
        return {
            "enabled": self.get_bool("MULTI_TENANT_ENABLED", False),
            "default_tenant_type": self.get("DEFAULT_TENANT_TYPE", "individual"),
            "max_tenants_per_user": self.get_int("MAX_TENANTS_PER_USER", 1),
            "tenant_isolation_strict": self.get_bool("TENANT_ISOLATION_STRICT", True),
            "rls_enabled": self.get_bool("RLS_ENABLED", True)
        }
    
    def is_multi_tenant_enabled(self) -> bool:
        """Raw multi-tenant enabled check - no business logic."""
        return self.get_bool("MULTI_TENANT_ENABLED", False)
    
    def get_default_tenant_type(self) -> str:
        """Raw default tenant type retrieval - no business logic."""
        return self.get("DEFAULT_TENANT_TYPE", "individual")
    
    def is_tenant_isolation_strict(self) -> bool:
        """Raw tenant isolation strict check - no business logic."""
        return self.get_bool("TENANT_ISOLATION_STRICT", True)
    
    def is_rls_enabled(self) -> bool:
        """Raw RLS enabled check - no business logic."""
        return self.get_bool("RLS_ENABLED", True)
    
    # ============================================================================
    # RAW SECURITY CONFIGURATION OPERATIONS
    # ============================================================================
    
    def get_security_config(self) -> Dict[str, Any]:
        """Raw security configuration retrieval - no business logic."""
        return {
            "level": self.get("SECURITY_LEVEL", "standard"),
            "jwt_secret": self.get("JWT_SECRET_KEY"),
            "password_min_length": self.get_int("PASSWORD_MIN_LENGTH", 8),
            "password_require_uppercase": self.get_bool("PASSWORD_REQUIRE_UPPERCASE", True),
            "password_require_lowercase": self.get_bool("PASSWORD_REQUIRE_LOWERCASE", True),
            "password_require_numbers": self.get_bool("PASSWORD_REQUIRE_NUMBERS", True),
            "password_require_symbols": self.get_bool("PASSWORD_REQUIRE_SYMBOLS", True)
        }
    
    def get_security_level(self) -> str:
        """Raw security level retrieval - no business logic."""
        return self.get("SECURITY_LEVEL", "standard")
    
    def get_password_requirements(self) -> Dict[str, Any]:
        """Raw password requirements retrieval - no business logic."""
        return {
            "min_length": self.get_int("PASSWORD_MIN_LENGTH", 8),
            "require_uppercase": self.get_bool("PASSWORD_REQUIRE_UPPERCASE", True),
            "require_lowercase": self.get_bool("PASSWORD_REQUIRE_LOWERCASE", True),
            "require_numbers": self.get_bool("PASSWORD_REQUIRE_NUMBERS", True),
            "require_symbols": self.get_bool("PASSWORD_REQUIRE_SYMBOLS", True)
        }
    
    # ============================================================================
    # RAW CACHING CONFIGURATION OPERATIONS
    # ============================================================================
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Raw cache configuration retrieval - no business logic."""
        return {
            "enabled": self.get_bool("CACHE_ENABLED", True),
            "tenant_cache_ttl": self.get_int("TENANT_CACHE_TTL", 3600),
            "user_context_cache_ttl": self.get_int("USER_CONTEXT_CACHE_TTL", 1800),
            "session_cache_ttl": self.get_int("SESSION_CACHE_TTL", 3600)
        }
    
    def is_cache_enabled(self) -> bool:
        """Raw cache enabled check - no business logic."""
        return self.get_bool("CACHE_ENABLED", True)
    
    def get_tenant_cache_ttl(self) -> int:
        """Raw tenant cache TTL retrieval - no business logic."""
        return self.get_int("TENANT_CACHE_TTL", 3600)
    
    def get_user_context_cache_ttl(self) -> int:
        """Raw user context cache TTL retrieval - no business logic."""
        return self.get_int("USER_CONTEXT_CACHE_TTL", 1800)
    
    def get_arangodb_hosts(self) -> str:
        """Raw ArangoDB hosts retrieval - no business logic."""
        return self.get("ARANGO_HOSTS", "localhost:8529")
    
    def get_arangodb_database(self) -> str:
        """Raw ArangoDB database retrieval - no business logic."""
        return self.get("ARANGO_DB", "symphainy_metadata")
    
    def get_arangodb_url(self) -> str:
        """Raw ArangoDB URL retrieval - no business logic."""
        return self.get("ARANGO_URL", "http://localhost:8529")
    
    def get_arangodb_user(self) -> str:
        """Raw ArangoDB user retrieval - no business logic."""
        return self.get("ARANGO_USER", "root")
    
    def get_arangodb_password(self) -> str:
        """Raw ArangoDB password retrieval - no business logic."""
        return self.get("ARANGO_PASS", "")
    
    def get_arangodb_username(self) -> str:
        """Raw ArangoDB username retrieval - no business logic."""
        return self.get("ARANGO_USER", "root")
    
    # ============================================================================
    # RAW GCS CONFIGURATION OPERATIONS
    # ============================================================================
    
    def get_gcs_project_id(self) -> Optional[str]:
        """
        Raw GCS project ID retrieval - no business logic.
        
        Supports multiple naming conventions:
        - GCS_PROJECT_ID (preferred)
        - GOOGLE_CLOUD_PROJECT (alternative)
        """
        return (
            self.get("GCS_PROJECT_ID") or
            self.get("GOOGLE_CLOUD_PROJECT")
        )
    
    def get_gcs_bucket_name(self) -> Optional[str]:
        """
        Raw GCS bucket name retrieval - no business logic.
        
        Supports multiple naming conventions:
        - GCS_BUCKET_NAME (preferred)
        - GCS_BUCKET (alternative)
        """
        return (
            self.get("GCS_BUCKET_NAME") or
            self.get("GCS_BUCKET")
        )
    
    def get_gcs_credentials_json(self) -> Optional[str]:
        """
        Raw GCS bucket credentials JSON retrieval - no business logic.
        
        CRITICAL ARCHITECTURAL SEPARATION:
        - This returns ONLY bucket credentials (from GCS_CREDENTIALS_JSON)
        - It does NOT use GOOGLE_APPLICATION_CREDENTIALS as fallback
        - GOOGLE_APPLICATION_CREDENTIALS is for SSH/VM access (infrastructure)
        - GCS_CREDENTIALS_JSON is for bucket access (application data)
        - These are SEPARATE concerns and must remain distinct
        
        SUPABASE PATTERN:
        - Store credentials as JSON string in environment variable
        - No file paths needed = no path resolution = simpler and safer
        - Consistent with Supabase adapter pattern
        
        Returns:
            JSON string of service account credentials, or None if not set
        """
        # ✅ ONLY return bucket credentials - never fallback to SSH credentials
        return self.get("GCS_CREDENTIALS_JSON")
    
    def get_gcs_config(self) -> Dict[str, Any]:
        """
        Raw GCS configuration retrieval - no business logic.
        
        Returns a dictionary with GCS configuration values.
        """
        return {
            "project_id": self.get_gcs_project_id(),
            "bucket_name": self.get_gcs_bucket_name() or "symphainy-platform-files",
            "credentials_json": self.get_gcs_credentials_json()
        }
    
    def get_arangodb_config(self) -> Dict[str, Any]:
        """Raw ArangoDB configuration retrieval - no business logic."""
        return {
            "hosts": self.get("ARANGO_URL", "http://localhost:8529"),
            "database": self.get("ARANGO_DB", "symphainy_metadata"),
            "user": self.get("ARANGO_USER", "root"),
            "password": self.get("ARANGO_PASS", "")
        }
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Config adapter - no business logic."""
        try:
            # Test basic operations
            test_key = "TEST_CONFIG_KEY"
            test_value = "test_value"
            
            # Set a test environment variable
            os.environ[test_key] = test_value
            
            # Test retrieval
            retrieved_value = self.get(test_key)
            
            # Clean up
            del os.environ[test_key]
            
            return {
                "success": True,
                "message": "Config adapter working correctly",
                "test_value_set": test_value,
                "test_value_retrieved": retrieved_value,
                "values_match": test_value == retrieved_value
            }
        except Exception as e:
            logger.error(f"Config adapter test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get Config adapter information - no business logic."""
        return {
            "env_file_path": self.env_file_path,
            "cache_size": len(self.config_cache),
            "environment_variables_count": len(os.environ)
        }
