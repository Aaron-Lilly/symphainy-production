#!/usr/bin/env python3
"""
Cloud-Ready Configuration - Feature Flag System

Manages feature flags for cloud-ready architecture migration.
Allows parallel implementation of old and new approaches.

WHAT (Configuration Utility): I provide feature flag management for cloud-ready architecture
HOW (Implementation): I read environment variables and provide configuration state
"""

import os
import logging
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class CloudReadyMode(Enum):
    """Cloud-ready mode enumeration."""
    DISABLED = "disabled"  # Use current implementation
    ENABLED = "enabled"     # Use cloud-ready implementation
    HYBRID = "hybrid"       # Use cloud-ready where available, fallback to current


class CloudReadyConfig:
    """
    Cloud-ready configuration manager.
    
    Provides centralized feature flag management for cloud-ready architecture migration.
    Supports environment variable-based configuration with component-level granularity.
    """
    
    def __init__(self, config_adapter=None):
        """
        Initialize cloud-ready configuration.
        
        Args:
            config_adapter: Optional ConfigAdapter for reading configuration (preferred over os.getenv)
        """
        self.config_adapter = config_adapter
        
        # Read mode from ConfigAdapter (preferred) or environment variable
        if config_adapter:
            mode_str = config_adapter.get("CLOUD_READY_MODE", "disabled")
            if isinstance(mode_str, str):
                mode_str = mode_str.lower()
        else:
            mode_str = os.getenv("CLOUD_READY_MODE", "disabled").lower()
            if mode_str != "disabled":
                logger.warning("⚠️ [CLOUD_READY_CONFIG] Using os.getenv() - consider passing config_adapter for centralized configuration")
        
        if mode_str == "enabled":
            self.mode = CloudReadyMode.ENABLED
        elif mode_str == "hybrid":
            self.mode = CloudReadyMode.HYBRID
        else:
            self.mode = CloudReadyMode.DISABLED
        
        # Component-level flags (override mode if explicitly set)
        # Use ConfigAdapter if available, otherwise fallback to os.getenv()
        def get_config_value(key: str, default: str = "false") -> str:
            if config_adapter:
                value = config_adapter.get(key, default)
                return str(value).lower() if value else default
            else:
                value = os.getenv(key, default)
                if value != default:
                    logger.warning(f"⚠️ [CLOUD_READY_CONFIG] Using os.getenv() for {key} - consider passing config_adapter")
                return value.lower()
        
        self.auto_discovery_enabled = get_config_value("CLOUD_READY_AUTO_DISCOVERY", "false") == "true"
        self.unified_registry_enabled = get_config_value("CLOUD_READY_UNIFIED_REGISTRY", "false") == "true"
        self.managed_services_enabled = get_config_value("CLOUD_READY_MANAGED_SERVICES", "false") == "true"
        self.cloud_ready_startup_enabled = get_config_value("CLOUD_READY_STARTUP", "false") == "true"
        
        # If mode is enabled, enable all components by default
        if self.mode == CloudReadyMode.ENABLED:
            # Only enable if not explicitly disabled via component flag
            if get_config_value("CLOUD_READY_AUTO_DISCOVERY", "") != "false":
                self.auto_discovery_enabled = True
            if get_config_value("CLOUD_READY_UNIFIED_REGISTRY", "") != "false":
                self.unified_registry_enabled = True
            if get_config_value("CLOUD_READY_MANAGED_SERVICES", "") != "false":
                self.managed_services_enabled = True
            if get_config_value("CLOUD_READY_STARTUP", "") != "false":
                self.cloud_ready_startup_enabled = True
        
        # Log configuration state
        logger.info(f"🔧 Cloud-Ready Configuration: mode={self.mode.value}")
        logger.info(f"   - Auto-Discovery: {self.auto_discovery_enabled}")
        logger.info(f"   - Unified Registry: {self.unified_registry_enabled}")
        logger.info(f"   - Managed Services: {self.managed_services_enabled}")
        logger.info(f"   - Cloud-Ready Startup: {self.cloud_ready_startup_enabled}")
    
    def is_cloud_ready(self) -> bool:
        """
        Check if cloud-ready mode is enabled.
        
        Returns:
            True if cloud-ready mode is enabled, False otherwise.
        """
        return self.mode == CloudReadyMode.ENABLED
    
    def is_hybrid(self) -> bool:
        """
        Check if hybrid mode is enabled.
        
        Returns:
            True if hybrid mode is enabled, False otherwise.
        """
        return self.mode == CloudReadyMode.HYBRID
    
    def is_disabled(self) -> bool:
        """
        Check if cloud-ready mode is disabled (current implementation).
        
        Returns:
            True if cloud-ready mode is disabled, False otherwise.
        """
        return self.mode == CloudReadyMode.DISABLED
    
    def should_use_auto_discovery(self) -> bool:
        """
        Check if auto-discovery should be used.
        
        Returns:
            True if auto-discovery should be enabled, False otherwise.
        """
        return self.auto_discovery_enabled or self.is_cloud_ready()
    
    def should_use_unified_registry(self) -> bool:
        """
        Check if unified registry should be used.
        
        Returns:
            True if unified registry should be enabled, False otherwise.
        """
        return self.unified_registry_enabled or self.is_cloud_ready()
    
    def should_use_managed_services(self) -> bool:
        """
        Check if managed services should be used.
        
        Returns:
            True if managed services should be enabled, False otherwise.
        """
        return self.managed_services_enabled or self.is_cloud_ready()
    
    def should_use_cloud_ready_startup(self) -> bool:
        """
        Check if cloud-ready startup orchestrator should be used.
        
        Returns:
            True if cloud-ready startup should be enabled, False otherwise.
        """
        return self.cloud_ready_startup_enabled or self.is_cloud_ready()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for logging/debugging.
        
        Returns:
            Dictionary with configuration state.
        """
        return {
            "mode": self.mode.value,
            "auto_discovery": self.auto_discovery_enabled,
            "unified_registry": self.unified_registry_enabled,
            "managed_services": self.managed_services_enabled,
            "cloud_ready_startup": self.cloud_ready_startup_enabled,
            "is_cloud_ready": self.is_cloud_ready(),
            "is_hybrid": self.is_hybrid(),
            "is_disabled": self.is_disabled()
        }


# Global instance (singleton pattern)
_cloud_ready_config_instance: CloudReadyConfig = None


def get_cloud_ready_config(config_adapter=None) -> CloudReadyConfig:
    """
    Get the global cloud-ready configuration instance.
    
    Args:
        config_adapter: Optional ConfigAdapter for reading configuration (preferred over os.getenv)
    
    Returns:
        CloudReadyConfig instance (singleton).
    """
    global _cloud_ready_config_instance
    if _cloud_ready_config_instance is None:
        _cloud_ready_config_instance = CloudReadyConfig(config_adapter=config_adapter)
    return _cloud_ready_config_instance


def reset_cloud_ready_config():
    """
    Reset the cloud-ready configuration singleton (for testing).
    
    This allows tests to force a fresh config instance to be created.
    """
    global _cloud_ready_config_instance
    _cloud_ready_config_instance = None


# Note: We don't create cloud_ready_config at module level to avoid
# singleton issues during testing. Use get_cloud_ready_config() instead.

