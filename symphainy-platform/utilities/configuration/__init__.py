"""
Configuration Utility Package

Platform-specific configuration utilities for Smart City services.
"""

from .configuration_utility import ConfigurationUtility
from .cloud_ready_config import CloudReadyConfig, CloudReadyMode, get_cloud_ready_config, reset_cloud_ready_config

# Create lazy accessor for backward compatibility
def cloud_ready_config():
    """Lazy accessor for cloud-ready config (backward compatibility)."""
    return get_cloud_ready_config()

__all__ = [
    "ConfigurationUtility",
    "CloudReadyConfig",
    "CloudReadyMode",
    "get_cloud_ready_config",
    "reset_cloud_ready_config",
    "cloud_ready_config"
]

