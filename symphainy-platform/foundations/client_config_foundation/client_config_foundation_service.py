#!/usr/bin/env python3
"""
Client Config Foundation Service - Customer Configuration Management

Provides SDK for managing customer-specific configurations that don't fork the platform.
Similar to Experience Foundation pattern (SDK builders).

WHAT (Client Config Foundation Role): I provide customer configuration SDK to all realms
HOW (Client Config Foundation Implementation): I provide SDK builders for config loading, storage, validation, and versioning

Key Capabilities:
- Load tenant configs from Git or DB
- Store tenant configs with version control
- Validate configs (schema, tenant isolation, dependencies)
- Version configs (Git commits, DB snapshots, rollback)
- Support config types (domain_models, workflows, dashboards, etc.)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from bases.foundation_service_base import FoundationServiceBase

# Import SDK builders
from .sdk.config_loader_builder import ConfigLoaderBuilder
from .sdk.config_storage_builder import ConfigStorageBuilder
from .sdk.config_validator_builder import ConfigValidatorBuilder
from .sdk.config_versioner_builder import ConfigVersionerBuilder


class ClientConfigFoundationService(FoundationServiceBase):
    """
    Client Config Foundation Service - Customer Configuration Management
    
    Provides SDK for managing customer-specific configurations that don't fork the platform.
    Similar to Experience Foundation pattern (SDK builders).
    
    WHAT (Client Config Foundation Role): I provide customer configuration SDK to all realms
    HOW (Client Config Foundation Implementation): I provide SDK builders for config management
    
    Responsibilities:
    - Provide config SDK components (ConfigLoaderBuilder, ConfigStorageBuilder, ConfigValidatorBuilder, ConfigVersionerBuilder)
    - Enable config capabilities for all realms
    - Manage config instance lifecycle
    - Integrate with Public Works Foundation for storage
    - Integrate with Experience Foundation for config exposure
    """
    
    def __init__(self, di_container, public_works_foundation=None, curator_foundation=None):
        """Initialize Client Config Foundation Service."""
        super().__init__(
            service_name="client_config_foundation",
            di_container=di_container,
            security_provider=None,  # Will be set by DI container
            authorization_guard=None  # Will be set by DI container
        )
        
        # Foundation dependencies
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Config SDK builders (not instances - builders!)
        self.config_loader_builder = ConfigLoaderBuilder
        self.config_storage_builder = ConfigStorageBuilder
        self.config_validator_builder = ConfigValidatorBuilder
        self.config_versioner_builder = ConfigVersionerBuilder
        
        # Config capabilities registry
        self.config_capabilities = {}
        
        # Track created instances (for lifecycle management)
        self._created_loaders: Dict[str, Any] = {}
        self._created_storages: Dict[str, Any] = {}
        self._created_validators: Dict[str, Any] = {}
        self._created_versioners: Dict[str, Any] = {}
        
        self.logger.info("🏗️ Client Config Foundation Service initialized")
    
    async def initialize(self):
        """Initialize Client Config Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("client_config_foundation_initialize_start", success=True)
            
            self.logger.info("🔧 Initializing Client Config Foundation Service...")
            
            # Get Public Works Foundation if not provided
            if not self.public_works_foundation:
                try:
                    self.public_works_foundation = self.di_container.get_foundation_service("PublicWorksFoundationService")
                    if self.public_works_foundation:
                        self.logger.info("✅ Public Works Foundation discovered")
                except Exception as e:
                    self.logger.warning(f"⚠️ Public Works Foundation not available: {e}")
            
            # SDK builders are classes - they'll be initialized when creating instances
            # No additional initialization needed here
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            self.logger.info("✅ Client Config Foundation Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("client_config_foundation_initialized", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("client_config_foundation_initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "client_config_foundation_initialize")
            self.logger.error(f"❌ Client Config Foundation Service initialization failed: {e}")
            self.service_health = "error"
            raise
    
    # ========================================================================
    # SDK METHODS (Core Capabilities)
    # ========================================================================
    
    async def create_config_loader(
        self,
        tenant_id: str,
        storage_type: str = "db",
        config: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create config loader for tenant using SDK builder.
        
        Args:
            tenant_id: Tenant identifier
            storage_type: Storage type ("git", "db", or "hybrid")
            config: Optional loader configuration
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Initialized ConfigLoader instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_config_loader_start", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"🔧 Creating Config Loader for tenant: {tenant_id}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "config_loader_creation", "write"):
                        await self.record_health_metric("create_config_loader_access_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("create_config_loader_complete", success=False)
                        raise PermissionError("Access denied")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    user_tenant_id = user_context.get("tenant_id")
                    if user_tenant_id and user_tenant_id != tenant_id:
                        await self.record_health_metric("create_config_loader_tenant_mismatch", 1.0, {"tenant_id": tenant_id, "user_tenant_id": user_tenant_id})
                        await self.log_operation_with_telemetry("create_config_loader_complete", success=False)
                        raise PermissionError("Tenant access denied")
            
            # Create loader instance using builder
            loader_config = config or {}
            loader_config["tenant_id"] = tenant_id
            loader_config["storage_type"] = storage_type
            loader_config["public_works_foundation"] = self.public_works_foundation
            
            loader = self.config_loader_builder(
                tenant_id=tenant_id,
                storage_type=storage_type,
                public_works_foundation=self.public_works_foundation,
                config=loader_config,
                di_container=self.di_container
            )
            
            # Initialize loader
            await loader.initialize()
            
            # Track instance
            loader_key = f"{tenant_id}_{storage_type}"
            self._created_loaders[loader_key] = loader
            
            # Record health metric
            await self.record_health_metric("create_config_loader_success", 1.0, {"tenant_id": tenant_id, "storage_type": storage_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_config_loader_complete", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"✅ Config Loader created for tenant: {tenant_id}")
            
            return loader
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_config_loader", details={"tenant_id": tenant_id})
            await self.record_health_metric("create_config_loader_failed", 1.0, {"error": type(e).__name__})
            await self.log_operation_with_telemetry("create_config_loader_complete", success=False, details={"error": str(e)})
            raise
    
    async def create_config_storage(
        self,
        tenant_id: str,
        storage_type: str = "db",
        config: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create config storage for tenant using SDK builder.
        
        Args:
            tenant_id: Tenant identifier
            storage_type: Storage type ("git", "db", or "hybrid")
            config: Optional storage configuration
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Initialized ConfigStorage instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_config_storage_start", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"🔧 Creating Config Storage for tenant: {tenant_id}")
            
            # Security and tenant validation (same as loader)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "config_storage_creation", "write"):
                        await self.record_health_metric("create_config_storage_access_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("create_config_storage_complete", success=False)
                        raise PermissionError("Access denied")
            
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    user_tenant_id = user_context.get("tenant_id")
                    if user_tenant_id and user_tenant_id != tenant_id:
                        await self.record_health_metric("create_config_storage_tenant_mismatch", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("create_config_storage_complete", success=False)
                        raise PermissionError("Tenant access denied")
            
            # Create storage instance using builder
            storage_config = config or {}
            storage_config["tenant_id"] = tenant_id
            storage_config["storage_type"] = storage_type
            storage_config["public_works_foundation"] = self.public_works_foundation
            
            storage = self.config_storage_builder(
                tenant_id=tenant_id,
                storage_type=storage_type,
                public_works_foundation=self.public_works_foundation,
                config=storage_config,
                di_container=self.di_container
            )
            
            # Initialize storage
            await storage.initialize()
            
            # Track instance
            storage_key = f"{tenant_id}_{storage_type}"
            self._created_storages[storage_key] = storage
            
            # Record health metric
            await self.record_health_metric("create_config_storage_success", 1.0, {"tenant_id": tenant_id, "storage_type": storage_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_config_storage_complete", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"✅ Config Storage created for tenant: {tenant_id}")
            
            return storage
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_config_storage", details={"tenant_id": tenant_id})
            await self.record_health_metric("create_config_storage_failed", 1.0, {"error": type(e).__name__})
            await self.log_operation_with_telemetry("create_config_storage_complete", success=False, details={"error": str(e)})
            raise
    
    async def create_config_validator(
        self,
        tenant_id: str,
        config: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create config validator for tenant using SDK builder.
        
        Args:
            tenant_id: Tenant identifier
            config: Optional validator configuration
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Initialized ConfigValidator instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_config_validator_start", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"🔧 Creating Config Validator for tenant: {tenant_id}")
            
            # Security and tenant validation
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "config_validator_creation", "write"):
                        await self.record_health_metric("create_config_validator_access_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("create_config_validator_complete", success=False)
                        raise PermissionError("Access denied")
            
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    user_tenant_id = user_context.get("tenant_id")
                    if user_tenant_id and user_tenant_id != tenant_id:
                        await self.record_health_metric("create_config_validator_tenant_mismatch", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("create_config_validator_complete", success=False)
                        raise PermissionError("Tenant access denied")
            
            # Create validator instance using builder
            validator_config = config or {}
            validator_config["tenant_id"] = tenant_id
            
            validator = self.config_validator_builder(
                tenant_id=tenant_id,
                config=validator_config,
                di_container=self.di_container
            )
            
            # Initialize validator
            await validator.initialize()
            
            # Track instance
            validator_key = f"{tenant_id}"
            self._created_validators[validator_key] = validator
            
            # Record health metric
            await self.record_health_metric("create_config_validator_success", 1.0, {"tenant_id": tenant_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_config_validator_complete", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"✅ Config Validator created for tenant: {tenant_id}")
            
            return validator
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_config_validator", details={"tenant_id": tenant_id})
            await self.record_health_metric("create_config_validator_failed", 1.0, {"error": type(e).__name__})
            await self.log_operation_with_telemetry("create_config_validator_complete", success=False, details={"error": str(e)})
            raise
    
    async def create_config_versioner(
        self,
        tenant_id: str,
        storage_type: str = "db",
        config: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create config versioner for tenant using SDK builder.
        
        Args:
            tenant_id: Tenant identifier
            storage_type: Storage type ("git", "db", or "hybrid")
            config: Optional versioner configuration
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Initialized ConfigVersioner instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_config_versioner_start", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"🔧 Creating Config Versioner for tenant: {tenant_id}")
            
            # Security and tenant validation
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "config_versioner_creation", "write"):
                        await self.record_health_metric("create_config_versioner_access_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("create_config_versioner_complete", success=False)
                        raise PermissionError("Access denied")
            
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    user_tenant_id = user_context.get("tenant_id")
                    if user_tenant_id and user_tenant_id != tenant_id:
                        await self.record_health_metric("create_config_versioner_tenant_mismatch", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("create_config_versioner_complete", success=False)
                        raise PermissionError("Tenant access denied")
            
            # Create versioner instance using builder
            versioner_config = config or {}
            versioner_config["tenant_id"] = tenant_id
            versioner_config["storage_type"] = storage_type
            versioner_config["public_works_foundation"] = self.public_works_foundation
            
            versioner = self.config_versioner_builder(
                tenant_id=tenant_id,
                storage_type=storage_type,
                public_works_foundation=self.public_works_foundation,
                config=versioner_config,
                di_container=self.di_container
            )
            
            # Initialize versioner
            await versioner.initialize()
            
            # Track instance
            versioner_key = f"{tenant_id}_{storage_type}"
            self._created_versioners[versioner_key] = versioner
            
            # Record health metric
            await self.record_health_metric("create_config_versioner_success", 1.0, {"tenant_id": tenant_id, "storage_type": storage_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_config_versioner_complete", success=True, details={"tenant_id": tenant_id})
            
            self.logger.info(f"✅ Config Versioner created for tenant: {tenant_id}")
            
            return versioner
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_config_versioner", details={"tenant_id": tenant_id})
            await self.record_health_metric("create_config_versioner_failed", 1.0, {"error": type(e).__name__})
            await self.log_operation_with_telemetry("create_config_versioner_complete", success=False, details={"error": str(e)})
            raise
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from FoundationServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "public_works_available": self.public_works_foundation is not None,
            "loaders_created": len(self._created_loaders),
            "storages_created": len(self._created_storages),
            "validators_created": len(self._created_validators),
            "versioners_created": len(self._created_versioners),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from FoundationServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "foundation_service",
            "capabilities": [
                "config_loading",
                "config_storage",
                "config_validation",
                "config_versioning"
            ],
            "sdk_builders": [
                "ConfigLoaderBuilder",
                "ConfigStorageBuilder",
                "ConfigValidatorBuilder",
                "ConfigVersionerBuilder"
            ],
            "composes": "public_works_foundation, experience_foundation"
        }










