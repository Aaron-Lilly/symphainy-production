#!/usr/bin/env python3
"""
Policy Configuration Service

WHAT: Manages WAL and Saga policies for Solution Orchestrators
HOW: Centralized policy management via environment variables, configuration files, or API

This service provides centralized policy management for WAL and Saga capabilities,
following the "Capability by Design, Optional by Policy" pattern.
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class PolicyConfigurationService(RealmServiceBase):
    """
    Policy Configuration Service for Solution realm.
    
    Provides centralized policy management for WAL and Saga capabilities.
    Policies can be configured via:
    - Environment variables
    - Configuration files
    - API (future)
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Policy Configuration Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Policy cache (orchestrator_name -> policy)
        self._wal_policy_cache: Dict[str, Dict[str, Any]] = {}
        self._saga_policy_cache: Dict[str, Dict[str, Any]] = {}
        
        # Configuration file path (optional) - get from ConfigAdapter if available
        config_adapter = self._get_config_adapter()
        if config_adapter:
            self._config_file_path = config_adapter.get("POLICY_CONFIG_FILE")
        else:
            self._config_file_path = os.getenv("POLICY_CONFIG_FILE", None)
            if self._config_file_path:
                self.logger.warning("⚠️ [POLICY_CONFIG] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
    
    async def initialize(self) -> bool:
        """
        Initialize Policy Configuration Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "policy_configuration_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # Load configuration from file if provided
            if self._config_file_path and os.path.exists(self._config_file_path):
                await self._load_config_from_file()
            
            # Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "policy_management",
                        "protocol": "PolicyConfigurationProtocol",
                        "description": "Manage WAL and Saga policies",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_wal_policy",
                                "endpoint": "/api/v1/solution/policy/wal",
                                "method": "GET",
                                "handler": self.get_wal_policy,
                                "metadata": {
                                    "description": "Get WAL policy for an orchestrator",
                                    "parameters": ["orchestrator_name", "user_context"]
                                }
                            },
                            "soa_api": {
                                "api_name": "get_saga_policy",
                                "endpoint": "/api/v1/solution/policy/saga",
                                "method": "GET",
                                "handler": self.get_saga_policy,
                                "metadata": {
                                    "description": "Get Saga policy for an orchestrator",
                                    "parameters": ["orchestrator_name", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.manage_policy",
                            "semantic_api": "/api/v1/solution/policy",
                            "user_journey": "manage_policy"
                        }
                    }
                ],
                soa_apis=[
                    "get_wal_policy",
                    "get_saga_policy",
                    "update_wal_policy",
                    "update_saga_policy"
                ]
            )
            
            # Record health metric
            await self.record_health_metric(
                "policy_configuration_initialized",
                1.0,
                {"service": "PolicyConfigurationService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "policy_configuration_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Policy Configuration Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "policy_configuration_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "policy_configuration_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Policy Configuration Service initialization failed: {e}")
            return False
    
    async def _load_config_from_file(self):
        """Load policy configuration from file."""
        try:
            with open(self._config_file_path, 'r') as f:
                config = json.load(f)
                
            # Load WAL policies
            if "wal_policies" in config:
                for orchestrator_name, policy in config["wal_policies"].items():
                    self._wal_policy_cache[orchestrator_name] = policy
            
            # Load Saga policies
            if "saga_policies" in config:
                for orchestrator_name, policy in config["saga_policies"].items():
                    self._saga_policy_cache[orchestrator_name] = policy
            
            self.logger.info(f"✅ Loaded policy configuration from {self._config_file_path}")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load policy configuration from file: {e}")
    
    # ========================================================================
    # WAL POLICY MANAGEMENT (SOA APIs)
    # ========================================================================
    
    async def get_wal_policy(
        self,
        orchestrator_name: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get WAL policy for an orchestrator (SOA API).
        
        Checks in order:
        1. Policy cache (from config file)
        2. Environment variables
        3. Default policy
        
        Args:
            orchestrator_name: Name of the orchestrator (e.g., "DataSolutionOrchestratorService")
            user_context: Optional user context
        
        Returns:
            Dict with WAL policy:
            {
                "enable_wal": bool,
                "log_operations": List[str],
                "namespace": str
            }
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_wal_policy_start",
            success=True,
            details={"orchestrator_name": orchestrator_name}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "get_wal_policy", "read"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "get_wal_policy",
                        details={"user_id": user_context.get("user_id"), "orchestrator_name": orchestrator_name}
                    )
                    await self.record_health_metric("get_wal_policy_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("get_wal_policy_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
            
            # Check cache first
            if orchestrator_name in self._wal_policy_cache:
                policy = self._wal_policy_cache[orchestrator_name]
            else:
                # Build policy from environment variables
                policy = self._build_wal_policy_from_env(orchestrator_name)
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "get_wal_policy_complete",
                success=True,
                details={"orchestrator_name": orchestrator_name}
            )
            
            return {
                "success": True,
                "policy": policy
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_wal_policy", details={"orchestrator_name": orchestrator_name})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_wal_policy_complete",
                success=False,
                details={"error": str(e), "orchestrator_name": orchestrator_name}
            )
            
            self.logger.error(f"❌ Get WAL policy failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_wal_policy_from_env(self, orchestrator_name: str) -> Dict[str, Any]:
        """Build WAL policy from ConfigAdapter (preferred) or environment variables."""
        config_adapter = self._get_config_adapter()
        
        # Helper to get config value
        def get_config_value(key: str, default: str = "") -> str:
            if config_adapter:
                value = config_adapter.get(key, default)
                return str(value) if value else default
            else:
                value = os.getenv(key, default)
                if value != default:
                    self.logger.warning(f"⚠️ [POLICY_CONFIG] Using os.getenv() for {key} - consider accessing ConfigAdapter")
                return value
        
        # Check global WAL enablement
        wal_enabled_str = get_config_value("WAL_ENABLED", "false")
        wal_enabled = wal_enabled_str.lower() == "true"
        
        # Check orchestrator-specific enablement
        orchestrator_env_key = orchestrator_name.upper().replace("SERVICE", "").replace("ORCHESTRATOR", "").replace("SOLUTION", "")
        orchestrator_wal_key = f"{orchestrator_env_key}_WAL_ENABLED"
        orchestrator_wal_enabled = get_config_value(orchestrator_wal_key, "")
        
        if orchestrator_wal_enabled:
            wal_enabled = orchestrator_wal_enabled.lower() == "true"
        
        # Get log operations
        wal_operations_env = get_config_value("WAL_OPERATIONS", "")
        log_operations = [op.strip() for op in wal_operations_env.split(",") if op.strip()] if wal_operations_env else []
        
        # Get namespace
        namespace = get_config_value("WAL_NAMESPACE", f"{orchestrator_name.lower()}_operations")
        
        return {
            "enable_wal": wal_enabled,
            "log_operations": log_operations,
            "namespace": namespace
        }
    
    # ========================================================================
    # SAGA POLICY MANAGEMENT (SOA APIs)
    # ========================================================================
    
    async def get_saga_policy(
        self,
        orchestrator_name: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Saga policy for an orchestrator (SOA API).
        
        Checks in order:
        1. Policy cache (from config file)
        2. Environment variables
        3. Default policy
        
        Args:
            orchestrator_name: Name of the orchestrator (e.g., "DataSolutionOrchestratorService")
            user_context: Optional user context
        
        Returns:
            Dict with Saga policy:
            {
                "enable_saga": bool,
                "saga_operations": List[str],
                "compensation_handlers": Dict[str, Dict[str, str]]
            }
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_saga_policy_start",
            success=True,
            details={"orchestrator_name": orchestrator_name}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "get_saga_policy", "read"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "get_saga_policy",
                        details={"user_id": user_context.get("user_id"), "orchestrator_name": orchestrator_name}
                    )
                    await self.record_health_metric("get_saga_policy_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("get_saga_policy_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
            
            # Check cache first
            if orchestrator_name in self._saga_policy_cache:
                policy = self._saga_policy_cache[orchestrator_name]
            else:
                # Build policy from environment variables
                policy = self._build_saga_policy_from_env(orchestrator_name)
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "get_saga_policy_complete",
                success=True,
                details={"orchestrator_name": orchestrator_name}
            )
            
            return {
                "success": True,
                "policy": policy
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_saga_policy", details={"orchestrator_name": orchestrator_name})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_saga_policy_complete",
                success=False,
                details={"error": str(e), "orchestrator_name": orchestrator_name}
            )
            
            self.logger.error(f"❌ Get Saga policy failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_saga_policy_from_env(self, orchestrator_name: str) -> Dict[str, Any]:
        """Build Saga policy from ConfigAdapter (preferred) or environment variables."""
        config_adapter = self._get_config_adapter()
        
        # Helper to get config value
        def get_config_value(key: str, default: str = "") -> str:
            if config_adapter:
                value = config_adapter.get(key, default)
                return str(value) if value else default
            else:
                value = os.getenv(key, default)
                if value != default:
                    self.logger.warning(f"⚠️ [POLICY_CONFIG] Using os.getenv() for {key} - consider accessing ConfigAdapter")
                return value
        
        # Check global Saga enablement
        saga_enabled_str = get_config_value("SAGA_ENABLED", "false")
        saga_enabled = saga_enabled_str.lower() == "true"
        
        # Check orchestrator-specific enablement
        orchestrator_env_key = orchestrator_name.upper().replace("SERVICE", "").replace("ORCHESTRATOR", "").replace("SOLUTION", "")
        orchestrator_saga_key = f"{orchestrator_env_key}_SAGA_ENABLED"
        orchestrator_saga_enabled = get_config_value(orchestrator_saga_key, "")
        
        if orchestrator_saga_enabled:
            saga_enabled = orchestrator_saga_enabled.lower() == "true"
        
        # Get saga operations
        saga_operations_env = get_config_value("SAGA_OPERATIONS", "")
        saga_operations = [op.strip() for op in saga_operations_env.split(",") if op.strip()] if saga_operations_env else []
        
        # Compensation handlers are defined per orchestrator (not from env)
        # They should be defined in the orchestrator's _get_compensation_handlers() method
        compensation_handlers = {}
        
        return {
            "enable_saga": saga_enabled,
            "saga_operations": saga_operations,
            "compensation_handlers": compensation_handlers
        }
    
    # ========================================================================
    # POLICY UPDATE (SOA APIs - Future)
    # ========================================================================
    
    async def update_wal_policy(
        self,
        orchestrator_name: str,
        policy: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update WAL policy for an orchestrator (SOA API - Future).
        
        Updates policy cache. In future, could persist to config file or database.
        
        Args:
            orchestrator_name: Name of the orchestrator
            policy: New policy configuration
            user_context: Optional user context
        
        Returns:
            Dict with update result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "update_wal_policy_start",
            success=True,
            details={"orchestrator_name": orchestrator_name}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "update_wal_policy", "write"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "update_wal_policy",
                        details={"user_id": user_context.get("user_id"), "orchestrator_name": orchestrator_name}
                    )
                    await self.record_health_metric("update_wal_policy_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("update_wal_policy_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
            
            # Update cache
            self._wal_policy_cache[orchestrator_name] = policy
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "update_wal_policy_complete",
                success=True,
                details={"orchestrator_name": orchestrator_name}
            )
            
            return {
                "success": True,
                "message": f"WAL policy updated for {orchestrator_name}"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "update_wal_policy", details={"orchestrator_name": orchestrator_name})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "update_wal_policy_complete",
                success=False,
                details={"error": str(e), "orchestrator_name": orchestrator_name}
            )
            
            self.logger.error(f"❌ Update WAL policy failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_saga_policy(
        self,
        orchestrator_name: str,
        policy: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update Saga policy for an orchestrator (SOA API - Future).
        
        Updates policy cache. In future, could persist to config file or database.
        
        Args:
            orchestrator_name: Name of the orchestrator
            policy: New policy configuration
            user_context: Optional user context
        
        Returns:
            Dict with update result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "update_saga_policy_start",
            success=True,
            details={"orchestrator_name": orchestrator_name}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "update_saga_policy", "write"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "update_saga_policy",
                        details={"user_id": user_context.get("user_id"), "orchestrator_name": orchestrator_name}
                    )
                    await self.record_health_metric("update_saga_policy_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("update_saga_policy_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
            
            # Update cache
            self._saga_policy_cache[orchestrator_name] = policy
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "update_saga_policy_complete",
                success=True,
                details={"orchestrator_name": orchestrator_name}
            )
            
            return {
                "success": True,
                "message": f"Saga policy updated for {orchestrator_name}"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "update_saga_policy", details={"orchestrator_name": orchestrator_name})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "update_saga_policy_complete",
                success=False,
                details={"error": str(e), "orchestrator_name": orchestrator_name}
            )
            
            self.logger.error(f"❌ Update Saga policy failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }



