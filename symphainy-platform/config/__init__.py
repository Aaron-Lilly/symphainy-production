#!/usr/bin/env python3
"""
Configuration Management

Centralized configuration management for different environments.
Handles loading and validation of environment-specific configurations.

WHAT (Module Role): I manage environment-specific configurations
HOW (Module Implementation): I provide centralized config loading and validation
"""

import os
from typing import Dict, Any, Optional
from enum import Enum


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    STAGING = "staging"


class ConfigManager:
    """
    Configuration Manager
    
    Manages environment-specific configurations with validation and defaults.
    """
    
    def __init__(self, environment: Environment = None):
        """Initialize configuration manager."""
        self.environment = environment or self._detect_environment()
        self.config = self._load_config()
    
    def _detect_environment(self) -> Environment:
        """Detect current environment from environment variables."""
        env_name = os.getenv("SYMPHAINY_ENV", "development").lower()
        
        try:
            return Environment(env_name)
        except ValueError:
            print(f"⚠️ Unknown environment '{env_name}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration for current environment."""
        config_files = {
            Environment.DEVELOPMENT: "config/development.env",
            Environment.TESTING: "config/testing.env", 
            Environment.STAGING: "config/staging.env",
            Environment.PRODUCTION: "config/production.env"
        }
        
        config_file = config_files.get(self.environment, config_files[Environment.DEVELOPMENT])
        
        if not os.path.exists(config_file):
            print(f"⚠️ Config file {config_file} not found, using defaults")
            return self._get_default_config()
        
        return self._load_env_file(config_file)
    
    def _load_env_file(self, file_path: str) -> Dict[str, Any]:
        """Load environment variables from file."""
        config = {}
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
        except Exception as e:
            print(f"❌ Error loading config file {file_path}: {e}")
            return self._get_default_config()
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            # Database
            "DATABASE_URL": "postgresql://localhost:5432/symphainy_dev",
            "DATABASE_POOL_SIZE": "10",
            "DATABASE_MAX_OVERFLOW": "20",
            
            # Redis
            "REDIS_URL": "redis://localhost:6379/0",
            "REDIS_PASSWORD": "",
            
            # API
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000",
            "API_DEBUG": "true",
            
            # Logging
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "json",
            
            # Security
            "SECRET_KEY": "dev-secret-key-change-in-production",
            "JWT_SECRET": "dev-jwt-secret-change-in-production",
            
            # External Services
            "SUPABASE_URL": "",
            "SUPABASE_KEY": "",
            "OPENAI_API_KEY": "",
            
            # Monitoring
            "ENABLE_METRICS": "true",
            "METRICS_PORT": "9090",
            
            # Environment
            "SYMPHAINY_ENV": self.environment.value
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get configuration value as integer."""
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get configuration value as boolean."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes', 'on')
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get configuration value as float."""
        try:
            return float(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, default: list = None) -> list:
        """Get configuration value as list."""
        value = self.get(key, default or [])
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return default or []
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == Environment.STAGING
    
    def get_environment(self) -> Environment:
        """Get current environment."""
        return self.environment
    
    def to_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self.config.copy()


# Global configuration instance
config = ConfigManager()

