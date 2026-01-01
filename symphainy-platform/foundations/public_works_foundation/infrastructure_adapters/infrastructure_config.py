#!/usr/bin/env python3
"""
Infrastructure Configuration - Unified Configuration Management

Provides unified configuration retrieval for all infrastructure adapters.
This is a convenience layer that doesn't change adapter interfaces.

WHAT (Infrastructure Role): I provide unified configuration for all infrastructure
HOW (Infrastructure Implementation): I wrap ConfigAdapter with convenience methods

CRITICAL SAFEGUARDS:
- NEVER touches GOOGLE_APPLICATION_CREDENTIALS (SSH/VM access)
- Only uses application-specific credentials (GCS_CREDENTIALS_JSON, etc.)
- Preserves infrastructure swapping (adapters still use dependency injection)
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class InfrastructureConfig:
    """
    Unified configuration for all infrastructure adapters.
    
    Provides convenient configuration retrieval while preserving:
    - Infrastructure swapping (adapters still use dependency injection)
    - SSH credential protection (never touches GOOGLE_APPLICATION_CREDENTIALS)
    """
    
    # CRITICAL: SSH/VM Credentials - NEVER modified or used for application access
    CRITICAL_SSH_ENV_VARS = [
        "GOOGLE_APPLICATION_CREDENTIALS",  # SSH/VM access
        "GCLOUD_PROJECT",                  # GCP project (SSH context)
        "GOOGLE_CLOUD_PROJECT",            # GCP project (SSH context)
        "GCLOUD_CONFIG",                   # GCP config (SSH context)
        "CLOUDSDK_CONFIG"                  # GCP SDK config (SSH context)
    ]
    
    def __init__(self, config_adapter):
        """
        Initialize InfrastructureConfig with ConfigAdapter.
        
        Args:
            config_adapter: ConfigAdapter instance
        """
        self.config_adapter = config_adapter
        self.logger = logging.getLogger(__name__)
    
    # ============================================================================
    # STORAGE CONFIGURATION
    # ============================================================================
    
    def get_storage_config(self) -> Dict[str, Any]:
        """
        Get storage configuration (GCS, Supabase).
        
        CRITICAL: This method NEVER touches GOOGLE_APPLICATION_CREDENTIALS.
        Only uses GCS_CREDENTIALS_JSON for bucket access (Supabase pattern).
        
        Returns:
            Dictionary with storage configuration
        """
        return {
            "gcs": self._get_gcs_config(),
            "supabase": self._get_supabase_config(),
        }
    
    def _get_gcs_config(self) -> Dict[str, Any]:
        """
        Get GCS configuration (Supabase pattern - JSON credentials only).
        
        CREDENTIALS PATTERN (Supabase-style):
        - credentials_json: JSON string from GCS_CREDENTIALS_JSON environment variable
        - No file paths = no path resolution = no SSH/GCE concerns!
        - Consistent with Supabase adapter pattern
        
        Returns:
            Dictionary with GCS configuration including credentials_json
        """
        project_id = self.config_adapter.get_gcs_project_id()
        bucket_name = self.config_adapter.get_gcs_bucket_name() or "symphainy-platform-files"
        credentials_json = self.config_adapter.get_gcs_credentials_json()
        
        if credentials_json:
            self.logger.info("✅ Using GCS credentials from GCS_CREDENTIALS_JSON (Supabase pattern)")
        else:
            self.logger.info("ℹ️ No GCS_CREDENTIALS_JSON set - will use Application Default Credentials")
        
        return {
            "project_id": project_id,
            "bucket_name": bucket_name,
            "credentials_json": credentials_json  # JSON string (Supabase pattern)
        }
    
    def _get_supabase_config(self) -> Dict[str, Any]:
        """Get Supabase configuration."""
        return {
            "url": self.config_adapter.get_supabase_url(),
            "anon_key": self.config_adapter.get_supabase_anon_key(),
            "service_key": self.config_adapter.get_supabase_service_key()
        }
    
    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration (ArangoDB, Redis).
        
        Returns:
            Dictionary with database configuration
        """
        return {
            "arangodb": self._get_arangodb_config(),
            "redis": self._get_redis_config(),
        }
    
    def _get_arangodb_config(self) -> Dict[str, Any]:
        """Get ArangoDB configuration."""
        return self.config_adapter.get_arangodb_config()
    
    def _get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return self.config_adapter.get_redis_config()
    
    # ============================================================================
    # AI CONFIGURATION
    # ============================================================================
    
    def get_ai_config(self) -> Dict[str, Any]:
        """
        Get AI configuration (OpenAI, Anthropic).
        
        Returns:
            Dictionary with AI configuration
        """
        return {
            "openai": self._get_openai_config(),
            "anthropic": self._get_anthropic_config(),
        }
    
    def _get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration."""
        return {
            "api_key": self.config_adapter.get("OPENAI_API_KEY"),
            "model": self.config_adapter.get("OPENAI_MODEL", "gpt-4o-mini"),
            "base_url": self.config_adapter.get("OPENAI_BASE_URL")
        }
    
    def _get_anthropic_config(self) -> Dict[str, Any]:
        """Get Anthropic configuration."""
        return {
            "api_key": self.config_adapter.get("ANTHROPIC_API_KEY"),
            "model": self.config_adapter.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        }
    
    # ============================================================================
    # PATH RESOLUTION - REMOVED
    # ============================================================================
    #
    # PATH RESOLUTION NO LONGER NEEDED:
    # - GCS now uses JSON credentials (Supabase pattern)
    # - No file paths = no path resolution needed
    # - No SSH credential verification needed
    # - Simpler, cleaner, safer code
    #

