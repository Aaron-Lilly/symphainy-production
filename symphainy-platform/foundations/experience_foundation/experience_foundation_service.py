#!/usr/bin/env python3
"""
Experience Foundation Service - Experience SDK and Capabilities

Provides experience SDK and capabilities to all realms.
Similar to Agentic Foundation pattern.

WHAT (Experience Foundation Role): I provide experience SDK and capabilities to all realms
HOW (Experience Foundation Implementation): I provide SDK builders for Frontend Gateway, Session Manager, User Experience
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from bases.foundation_service_base import FoundationServiceBase

# Import SDK builders (will be created)
from .sdk.frontend_gateway_builder import FrontendGatewayBuilder
from .sdk.session_manager_builder import SessionManagerBuilder
from .sdk.user_experience_builder import UserExperienceBuilder
from .sdk.websocket_sdk import WebSocketSDK
from .sdk.realm_bridges_sdk import RealmBridgesSDK
from .sdk.unified_agent_websocket_sdk import UnifiedAgentWebSocketSDK


class ExperienceFoundationService(FoundationServiceBase):
    """
    Experience Foundation Service - Experience SDK and Capabilities
    
    Provides experience SDK and capabilities to all realms.
    Similar to Agentic Foundation pattern.
    
    WHAT (Experience Foundation Role): I provide experience SDK and capabilities to all realms
    HOW (Experience Foundation Implementation): I provide SDK builders for experience components
    
    Responsibilities:
    - Provide experience SDK components (FrontendGatewayBuilder, SessionManagerBuilder, UserExperienceBuilder)
    - Enable experience capabilities for all realms
    - Manage experience instance lifecycle
    """
    
    def __init__(self, di_container, public_works_foundation=None, curator_foundation=None):
        """Initialize Experience Foundation Service."""
        super().__init__(
            service_name="experience_foundation",
            di_container=di_container,
            security_provider=None,  # Will be set by DI container
            authorization_guard=None  # Will be set by DI container
        )
        
        # Foundation dependencies
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Experience SDK builders (not instances - builders!)
        self.frontend_gateway_builder = FrontendGatewayBuilder
        self.session_manager_builder = SessionManagerBuilder
        self.user_experience_builder = UserExperienceBuilder
        
        # WebSocket SDK (instance - initialized during foundation initialization)
        self._websocket_sdk: Optional[WebSocketSDK] = None
        
        # Realm Bridges SDK (instance - initialized during foundation initialization)
        self._realm_bridges_sdk: Optional[RealmBridgesSDK] = None
        
        # Unified Agent WebSocket SDK (instance - initialized on-demand)
        self._unified_agent_websocket_sdk: Optional[UnifiedAgentWebSocketSDK] = None
        
        # Experience capabilities registry
        self.experience_capabilities = {}
        
        # Track created instances (for lifecycle management)
        self._created_gateways: Dict[str, Any] = {}
        self._created_session_managers: Dict[str, Any] = {}
        self._created_user_experiences: Dict[str, Any] = {}
        
        # Platform FrontendGatewayService instance (created during initialization)
        # This is the strategic service that routes all API requests
        self._platform_frontend_gateway: Optional[Any] = None
        
        self.logger.info("🏗️ Experience Foundation Service initialized")
    
    async def initialize(self):
        """Initialize Experience Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("experience_foundation_initialize_start", success=True)
            
            self.logger.info("🔧 Initializing Experience Foundation Service...")
            
            # SDK builders are classes - they'll be initialized when creating instances
            # No additional initialization needed here
            
            # Initialize WebSocket SDK
            try:
                self.logger.info("🔧 Initializing WebSocket SDK...")
                self._websocket_sdk = WebSocketSDK(self)
                await self._websocket_sdk.initialize()
                self.logger.info("✅ WebSocket SDK initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize WebSocket SDK: {e}")
                self.logger.warning("   WebSocket capabilities may not be available")
                # Don't fail initialization - WebSocket SDK can be initialized on-demand
            
            # Initialize Realm Bridges SDK
            try:
                self.logger.info("🔧 Initializing Realm Bridges SDK...")
                # Get FastAPI Router Manager from DI Container
                router_manager = self.di_container.service_registry.get("FastAPIRouterManager")
                if not router_manager:
                    # Try to get from infrastructure services
                    if hasattr(self.di_container, 'get_foundation_service'):
                        # Router Manager is a utility, not a foundation service
                        # Try to get from platform orchestrator if available
                        platform_orchestrator = self.di_container.service_registry.get("PlatformOrchestrator")
                        if platform_orchestrator and hasattr(platform_orchestrator, 'router_manager'):
                            router_manager = platform_orchestrator.router_manager
                
                if router_manager:
                    self._realm_bridges_sdk = RealmBridgesSDK(
                        di_container=self.di_container,
                        public_works_foundation=self.public_works_foundation,
                        curator_foundation=self.curator_foundation,
                        router_manager=router_manager
                    )
                    await self._realm_bridges_sdk.initialize()
                    self.logger.info("✅ Realm Bridges SDK initialized")
                else:
                    self.logger.warning("⚠️ FastAPI Router Manager not available - Realm Bridges SDK will be initialized on-demand")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize Realm Bridges SDK: {e}")
                self.logger.warning("   Realm bridges may not be available")
                # Don't fail initialization - Realm Bridges SDK can be initialized on-demand
            
            # Create platform FrontendGatewayService during initialization
            # This is the strategic service that routes all API requests
            # It's created here (not via SDK) because it's required for platform startup
            try:
                self.logger.info("🔧 Creating platform FrontendGatewayService...")
                platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                if not platform_gateway:
                    self.logger.warning("⚠️ PlatformInfrastructureGateway not available - platform FrontendGatewayService will be created on-demand")
                else:
                    # Create platform FrontendGatewayService using SDK builder
                    # ✅ Use "solution" realm (platform-wide gateway routes all API requests)
                    gateway_config = {
                        "realm_name": "solution",
                        "enable_traefik": True,
                        "enable_route_discovery": True
                    }
                    platform_frontend_gateway = await self.create_frontend_gateway(
                        realm_name="solution",
                        config=gateway_config
                    )
                    self._platform_frontend_gateway = platform_frontend_gateway
                    self.logger.info("✅ Platform FrontendGatewayService created and stored")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to create platform FrontendGatewayService during initialization: {e}")
                self.logger.warning("   It will be created on-demand when accessed via get_platform_frontend_gateway()")
                # Don't fail initialization - gateway can be created on-demand
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            self.logger.info("✅ Experience Foundation Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("experience_foundation_initialized", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("experience_foundation_initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "experience_foundation_initialize")
            self.logger.error(f"❌ Experience Foundation Service initialization failed: {e}")
            self.service_health = "error"
            raise
    
    # ========================================================================
    # SDK METHODS (Core Capabilities)
    # ========================================================================
    
    async def create_frontend_gateway(
        self,
        realm_name: str,
        config: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> Any:
        """
        Create frontend gateway for realm using SDK builder.
        
        Args:
            realm_name: Name of realm creating the gateway
            config: Gateway configuration
                - composes: List of orchestrators/services to compose (e.g., ["content_analysis", "insights"])
                - api_prefix: API prefix (e.g., "/api/mvp")
                - transforms: Response transformation config
                - journey_type: Optional journey type (e.g., "mvp")
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Initialized FrontendGateway instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_frontend_gateway_start", success=True)
            
            self.logger.info(f"🔧 Creating Frontend Gateway for realm: {realm_name}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "frontend_gateway_creation", "write"):
                        await self.record_health_metric("create_frontend_gateway_access_denied", 1.0, {"realm_name": realm_name})
                        await self.log_operation_with_telemetry("create_frontend_gateway_complete", success=False)
                        raise PermissionError("Access denied")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("create_frontend_gateway_tenant_denied", 1.0, {"realm_name": realm_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("create_frontend_gateway_complete", success=False)
                            raise PermissionError("Tenant access denied")
            
            # Get platform gateway
            platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
            if not platform_gateway:
                raise RuntimeError("PlatformInfrastructureGateway not available")
            
            # Create gateway using builder
            gateway = self.frontend_gateway_builder(
                realm_name=realm_name,
                config=config,
                di_container=self.di_container,
                platform_gateway=platform_gateway,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            
            # Initialize gateway
            success = await gateway.initialize()
            if not success:
                raise RuntimeError(f"Failed to initialize Frontend Gateway for realm: {realm_name}")
            
            # Get the gateway instance from builder
            gateway_instance = gateway.get_gateway()
            
            # Track created instance
            gateway_key = f"{realm_name}_gateway"
            self._created_gateways[gateway_key] = gateway_instance
            
            self.logger.info(f"✅ Frontend Gateway created for realm: {realm_name}")
            
            # Record success metric
            await self.record_health_metric("create_frontend_gateway_success", 1.0, {"realm_name": realm_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_frontend_gateway_complete", success=True)
            
            return gateway_instance
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_frontend_gateway")
            self.logger.error(f"❌ Failed to create Frontend Gateway: {e}")
            raise
    
    async def create_session_manager(
        self,
        realm_name: str,
        config: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> Any:
        """
        Create session manager for realm using SDK builder.
        
        Args:
            realm_name: Name of realm creating the session manager
            config: Session manager configuration
                - session_ttl: Session time-to-live in seconds (default: 3600)
                - max_sessions_per_user: Maximum sessions per user (default: 5)
                - persistence_backend: Backend for persistence ("traffic_cop", "librarian")
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Initialized SessionManager instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_session_manager_start", success=True)
            
            self.logger.info(f"🔧 Creating Session Manager for realm: {realm_name}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "session_manager_creation", "write"):
                        await self.record_health_metric("create_session_manager_access_denied", 1.0, {"realm_name": realm_name})
                        await self.log_operation_with_telemetry("create_session_manager_complete", success=False)
                        raise PermissionError("Access denied")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("create_session_manager_tenant_denied", 1.0, {"realm_name": realm_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("create_session_manager_complete", success=False)
                            raise PermissionError("Tenant access denied")
            
            # Get platform gateway
            platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
            if not platform_gateway:
                raise RuntimeError("PlatformInfrastructureGateway not available")
            
            # Create session manager using builder
            session_manager = self.session_manager_builder(
                realm_name=realm_name,
                config=config,
                di_container=self.di_container,
                platform_gateway=platform_gateway,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            
            # Initialize session manager
            success = await session_manager.initialize()
            if not success:
                raise RuntimeError(f"Failed to initialize Session Manager for realm: {realm_name}")
            
            # Get the session manager instance from builder
            session_manager_instance = session_manager.get_session_manager()
            
            # Track created instance
            manager_key = f"{realm_name}_session_manager"
            self._created_session_managers[manager_key] = session_manager_instance
            
            self.logger.info(f"✅ Session Manager created for realm: {realm_name}")
            
            # Record success metric
            await self.record_health_metric("create_session_manager_success", 1.0, {"realm_name": realm_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_session_manager_complete", success=True)
            
            return session_manager_instance
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_session_manager")
            self.logger.error(f"❌ Failed to create Session Manager: {e}")
            raise
    
    async def create_user_experience(
        self,
        realm_name: str,
        config: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> Any:
        """
        Create user experience service for realm using SDK builder.
        
        Args:
            realm_name: Name of realm creating the user experience service
            config: User experience configuration
                - personalization_enabled: Enable personalization (default: True)
                - analytics_enabled: Enable UX analytics (default: True)
                - preference_storage: Backend for preferences ("librarian", "data_steward")
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Initialized UserExperience instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_user_experience_start", success=True)
            
            self.logger.info(f"🔧 Creating User Experience service for realm: {realm_name}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "user_experience_creation", "write"):
                        await self.record_health_metric("create_user_experience_access_denied", 1.0, {"realm_name": realm_name})
                        await self.log_operation_with_telemetry("create_user_experience_complete", success=False)
                        raise PermissionError("Access denied")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("create_user_experience_tenant_denied", 1.0, {"realm_name": realm_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("create_user_experience_complete", success=False)
                            raise PermissionError("Tenant access denied")
            
            # Get platform gateway
            platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
            if not platform_gateway:
                raise RuntimeError("PlatformInfrastructureGateway not available")
            
            # Create user experience using builder
            user_experience = self.user_experience_builder(
                realm_name=realm_name,
                config=config,
                di_container=self.di_container,
                platform_gateway=platform_gateway,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            
            # Initialize user experience
            success = await user_experience.initialize()
            if not success:
                raise RuntimeError(f"Failed to initialize User Experience service for realm: {realm_name}")
            
            # Get the user experience instance from builder
            user_experience_instance = user_experience.get_user_experience()
            
            # Track created instance
            ux_key = f"{realm_name}_user_experience"
            self._created_user_experiences[ux_key] = user_experience_instance
            
            self.logger.info(f"✅ User Experience service created for realm: {realm_name}")
            
            # Record success metric
            await self.record_health_metric("create_user_experience_success", 1.0, {"realm_name": realm_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_user_experience_complete", success=True)
            
            return user_experience_instance
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_user_experience")
            self.logger.error(f"❌ Failed to create User Experience service: {e}")
            raise
    
    async def get_platform_frontend_gateway(self) -> Any:
        """
        Get the platform FrontendGatewayService instance (SDK method).
        
        This is the strategic service that routes all API requests.
        It's created during Experience Foundation initialization and exposed via SDK.
        
        Foundation Services don't register with Curator (since Curator is itself a foundation),
        so we expose strategic services via SDK methods instead.
        
        Returns:
            FrontendGatewayService instance for solution realm (platform-wide gateway routes all API requests)
        """
        try:
            # Return cached instance if available
            if self._platform_frontend_gateway:
                return self._platform_frontend_gateway
            
            # Create on-demand if not created during initialization
            self.logger.info("🔧 Creating platform FrontendGatewayService on-demand...")
            self.logger.info(f"🔍 [get_platform_frontend_gateway] DI container service_registry keys: {list(self.di_container.service_registry.keys())}")
            # Try multiple ways to get PlatformInfrastructureGateway
            platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
            self.logger.info(f"🔍 [get_platform_frontend_gateway] get_foundation_service('PlatformInfrastructureGateway') returned: {platform_gateway is not None} ({type(platform_gateway).__name__ if platform_gateway else 'None'})")
            if not platform_gateway:
                # Try direct access from service_registry
                platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
                if platform_gateway:
                    from foundations.di_container.service_registration import ServiceRegistration
                    if isinstance(platform_gateway, ServiceRegistration):
                        platform_gateway = None
            if not platform_gateway:
                # Try getting from PlatformGatewayFoundationService
                gateway_foundation = self.di_container.service_registry.get("PlatformGatewayFoundationService")
                if gateway_foundation and hasattr(gateway_foundation, 'get_platform_gateway'):
                    from foundations.di_container.service_registration import ServiceRegistration
                    if not isinstance(gateway_foundation, ServiceRegistration):
                        platform_gateway = gateway_foundation.get_platform_gateway()
            if not platform_gateway:
                self.logger.error(f"❌ PlatformInfrastructureGateway not available. service_registry keys: {list(self.di_container.service_registry.keys())}")
                raise RuntimeError("PlatformInfrastructureGateway not available")
            
            gateway_config = {
                "realm_name": "solution",  # ✅ Use "solution" realm (platform-wide gateway routes all API requests)
                "enable_traefik": True,
                "enable_route_discovery": True
            }
            platform_frontend_gateway = await self.create_frontend_gateway(
                realm_name="solution",
                config=gateway_config
            )
            self._platform_frontend_gateway = platform_frontend_gateway
            self.logger.info("✅ Platform FrontendGatewayService created and cached")
            
            return platform_frontend_gateway
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get platform FrontendGatewayService: {e}")
            raise
    
    async def get_experience_sdk(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get Experience SDK components (builders).
        
        Args:
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with SDK builders
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_experience_sdk_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "experience_sdk", "read"):
                        await self.record_health_metric("get_experience_sdk_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_experience_sdk_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            result = {
                "frontend_gateway_builder": self.frontend_gateway_builder,
                "session_manager_builder": self.session_manager_builder,
                "user_experience_builder": self.user_experience_builder,
                "websocket_sdk": self._websocket_sdk
            }
            
            # Record success metric
            await self.record_health_metric("get_experience_sdk_success", 1.0, {"sdk_components_count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_experience_sdk_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_experience_sdk")
            self.logger.error(f"❌ Failed to get experience SDK: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def get_realm_bridges_sdk(self) -> Optional[RealmBridgesSDK]:
        """
        Get Realm Bridges SDK instance.
        
        Returns:
            RealmBridgesSDK instance, or None if not available
        """
        # If not initialized, try to initialize now
        if not self._realm_bridges_sdk:
            try:
                self.logger.info("🔧 Initializing Realm Bridges SDK on-demand...")
                # Get FastAPI Router Manager from DI Container
                router_manager = self.di_container.service_registry.get("FastAPIRouterManager")
                if not router_manager:
                    # Try to get from platform orchestrator
                    platform_orchestrator = self.di_container.service_registry.get("PlatformOrchestrator")
                    if platform_orchestrator and hasattr(platform_orchestrator, 'router_manager'):
                        router_manager = platform_orchestrator.router_manager
                
                if router_manager:
                    self._realm_bridges_sdk = RealmBridgesSDK(
                        di_container=self.di_container,
                        public_works_foundation=self.public_works_foundation,
                        curator_foundation=self.curator_foundation,
                        router_manager=router_manager
                    )
                    await self._realm_bridges_sdk.initialize()
                    self.logger.info("✅ Realm Bridges SDK initialized on-demand")
                else:
                    self.logger.warning("⚠️ FastAPI Router Manager not available - cannot initialize Realm Bridges SDK")
                    return None
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Realm Bridges SDK on-demand: {e}")
                return None
        
        return self._realm_bridges_sdk
    
    async def get_websocket_sdk(self) -> Optional[WebSocketSDK]:
        """
        Get WebSocket SDK instance.
        
        Returns:
            WebSocketSDK instance, or None if not available
        """
        try:
            # Initialize if not already initialized
            if not self._websocket_sdk:
                self.logger.info("🔧 Initializing WebSocket SDK on-demand...")
                self._websocket_sdk = WebSocketSDK(self)
                await self._websocket_sdk.initialize()
                self.logger.info("✅ WebSocket SDK initialized")
            
            return self._websocket_sdk
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get WebSocket SDK: {e}")
            return None
    
    async def get_unified_agent_websocket_sdk(self) -> Optional[UnifiedAgentWebSocketSDK]:
        """
        Get Unified Agent WebSocket SDK instance.
        
        Returns:
            UnifiedAgentWebSocketSDK instance, or None if not available
        """
        try:
            # Initialize if not already initialized
            if not self._unified_agent_websocket_sdk:
                self.logger.info("🔧 Initializing Unified Agent WebSocket SDK on-demand...")
                self._unified_agent_websocket_sdk = UnifiedAgentWebSocketSDK(self)
                await self._unified_agent_websocket_sdk.initialize()
                self.logger.info("✅ Unified Agent WebSocket SDK initialized")
            
            return self._unified_agent_websocket_sdk
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get Unified Agent WebSocket SDK: {e}")
            return None
    
    # ========================================================================
    # COMPATIBILITY METHODS (for Journey Manager and other services)
    # ========================================================================
    
    async def coordinate_experience(self, experience_request: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Coordinate experience services for user interactions (compatibility method).
        
        This method provides backward compatibility for Journey Manager and other services
        that expect Experience Manager-style orchestration. It uses the SDK builders
        to create the appropriate experience components.
        
        Args:
            experience_request: Experience coordination request
                - realm_name: Name of realm requesting experience coordination
                - experience_type: Type of experience ("frontend_gateway", "session_manager", "user_experience")
                - config: Configuration for the experience component
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with coordination result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("coordinate_experience_start", success=True)
            
            experience_type = experience_request.get('experience_type', 'unknown')
            self.logger.info(f"🔧 Coordinating experience: {experience_type}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "experience_coordination", "write"):
                        await self.record_health_metric("coordinate_experience_access_denied", 1.0, {"experience_type": experience_type})
                        await self.log_operation_with_telemetry("coordinate_experience_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("coordinate_experience_tenant_denied", 1.0, {"experience_type": experience_type, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("coordinate_experience_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            realm_name = experience_request.get("realm_name", "default")
            config = experience_request.get("config", {})
            
            # Route to appropriate SDK builder based on experience type
            if experience_type == "frontend_gateway":
                gateway = await self.create_frontend_gateway(realm_name, config, user_context)
                result = {
                    "success": True,
                    "experience_type": "frontend_gateway",
                    "gateway": gateway,
                    "realm_name": realm_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif experience_type == "session_manager":
                session_manager = await self.create_session_manager(realm_name, config, user_context)
                result = {
                    "success": True,
                    "experience_type": "session_manager",
                    "session_manager": session_manager,
                    "realm_name": realm_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif experience_type == "user_experience":
                user_experience = await self.create_user_experience(realm_name, config, user_context)
                result = {
                    "success": True,
                    "experience_type": "user_experience",
                    "user_experience": user_experience,
                    "realm_name": realm_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                result = {
                    "success": False,
                    "error": f"Unknown experience type: {experience_type}",
                    "error_code": "UNKNOWN_EXPERIENCE_TYPE",
                    "supported_types": ["frontend_gateway", "session_manager", "user_experience"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Record success metric
            await self.record_health_metric("coordinate_experience_success", 1.0, {"experience_type": experience_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("coordinate_experience_complete", success=True)
            
            return result
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "coordinate_experience")
            self.logger.error(f"❌ Failed to coordinate experience: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__,
                "experience_request": experience_request,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Health check."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("health_check_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "health_check", "read"):
                        await self.record_health_metric("health_check_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("health_check_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            result = {
                "status": "healthy" if self.is_initialized else "unhealthy",
                "service_name": self.service_name,
                "created_gateways": len(self._created_gateways),
                "created_session_managers": len(self._created_session_managers),
                "created_user_experiences": len(self._created_user_experiences),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("health_check_success", 1.0, {"status": result["status"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("health_check_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "health_check")
            self.logger.error(f"❌ Failed to perform health check: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "unhealthy"}
    
    async def get_service_capabilities(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get service capabilities."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_service_capabilities_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "service_capabilities", "read"):
                        await self.record_health_metric("get_service_capabilities_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_service_capabilities_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            sdk = await self.get_experience_sdk(user_context)
            
            result = {
                "service_name": self.service_name,
                "service_type": "foundation",
                "capabilities": ["frontend_gateway", "session_manager", "user_experience"],
                "sdk_components": list(sdk.keys()) if isinstance(sdk, dict) else [],
                "created_instances": {
                    "gateways": list(self._created_gateways.keys()),
                    "session_managers": list(self._created_session_managers.keys()),
                    "user_experiences": list(self._created_user_experiences.keys())
                }
            }
            
            # Record success metric
            await self.record_health_metric("get_service_capabilities_success", 1.0, {"capabilities_count": len(result["capabilities"])})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_service_capabilities_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_service_capabilities")
            self.logger.error(f"❌ Failed to get service capabilities: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}

