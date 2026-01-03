#!/usr/bin/env python3
"""
Security Guard Service - Micro-Modular Refactored

Clean micro-modular implementation using dynamic module loading via mixin.

WHAT (Smart City Role): I enforce security, zero-trust, multi-tenancy, and security communication gateway
HOW (Service Implementation): I use SmartCityRoleBase with micro-modules loaded dynamically
"""

from typing import Dict, Any, Optional

# Import ONLY our new base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.security_guard_service_protocol import SecurityGuardServiceProtocol


class SecurityGuardService(SmartCityRoleBase, SecurityGuardServiceProtocol):
    """
    Security Guard Service - Micro-Modular Refactored
    
    Clean implementation using micro-modules loaded dynamically via mixin.
    
    WHAT (Smart City Role): I enforce security, zero-trust, multi-tenancy, and security communication gateway
    HOW (Service Implementation): I use SmartCityRoleBase with micro-modules loaded dynamically
    """
    
    def __init__(self, di_container: Any):
        """Initialize Security Guard Service with micro-module support."""
        super().__init__(
            service_name="SecurityGuardService",
            role_name="security_guard",
            di_container=di_container
        )
        
        # Core Security State
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.security_policies: Dict[str, Dict[str, Any]] = {}
        self.tenant_contexts: Dict[str, Dict[str, Any]] = {}
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        self.mcp_server_enabled = False
        
        # Micro-modules (loaded dynamically via mixin)
        self.initialization_module = None
        self.authentication_module = None
        self.orchestration_module = None
        self.soa_mcp_module = None
        self.utilities_module = None
        
        # Logger is initialized by SmartCityRoleBase
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Security Guard Service initialized")
    
    def _log(self, level: str, message: str):
        """Safe logging method."""
        # Try multiple logger sources
        logger = None
        if hasattr(self, 'logger') and self.logger:
            logger = self.logger
        elif hasattr(self, 'di_container') and self.di_container:
            logger = self.di_container.get_logger(self.__class__.__name__)
        
        if logger:
            if level == "info":
                logger.info(message)
            elif level == "error":
                logger.error(message)
            elif level == "warning":
                logger.warning(message)
            elif level == "debug":
                logger.debug(message)
        else:
            # Fallback to print if no logger available
            print(f"[{level.upper()}] {self.__class__.__name__}: {message}")
    
    async def initialize(self) -> bool:
        """
        Initialize Security Guard Service with lazy-loaded modules.
        
        NORMAL PATTERN: This method doesn't provide security, so we can use utilities normally.
        """
        # Start telemetry tracking (Security Guard can use telemetry utilities for non-security operations)
        await self.log_operation_with_telemetry(
            "security_guard_initialize_start",
            success=True
        )
        
        try:
            self._log("info", "🚀 Initializing Security Guard Service with micro-modules...")
            
            # Debug: Check if micro-module path is set
            if hasattr(self, '_micro_module_path'):
                self._log("info", f"   Micro-module path: {self._micro_module_path}")
            else:
                self._log("warning", "   ⚠️ Micro-module path not set")
            
            # Load initialization module
            self._log("info", "   Loading initialization module...")
            try:
                # Try to get the module with detailed error reporting
                self._log("info", f"   Calling get_module('initialization')...")
                self.initialization_module = self.get_module("initialization")
                self._log("info", f"   get_module returned: {self.initialization_module}")
                if not self.initialization_module:
                    # Check if there's a logger from the mixin that might have more details
                    if hasattr(self, 'logger'):
                        mixin_logger = getattr(self, 'logger', None)
                        if mixin_logger:
                            self._log("info", f"   Mixin logger available: {mixin_logger}")
                    error_msg = "Failed to load initialization module"
                    self._log("error", f"   ❌ {error_msg}")
                    if hasattr(self, '_micro_module_path'):
                        self._log("error", f"   Module path was: {self._micro_module_path}")
                    # Try to get more details from the mixin
                    if hasattr(self, 'modules'):
                        self._log("info", f"   Loaded modules cache: {list(self.modules.keys())}")
                    raise Exception(error_msg)
                self._log("info", "   ✅ Initialization module loaded")
            except Exception as module_error:
                self._log("error", f"   Exception during module loading: {module_error}")
                import traceback
                self._log("error", f"   Traceback: {traceback.format_exc()}")
                raise
            
            # Initialize security capabilities
            self._log("info", "   Initializing security capabilities...")
            await self.initialization_module.initialize_security_capabilities()
            self._log("info", "   ✅ Security capabilities initialized")
            
            # Load other modules
            self._log("info", "   Loading other modules...")
            self.authentication_module = self.get_module("authentication")
            self._log("info", f"   Authentication module: {'✅' if self.authentication_module else '❌'}")
            
            self.orchestration_module = self.get_module("orchestration")
            self._log("info", f"   Orchestration module: {'✅' if self.orchestration_module else '❌'}")
            
            self.soa_mcp_module = self.get_module("soa_mcp")
            self._log("info", f"   SOA/MCP module: {'✅' if self.soa_mcp_module else '❌'}")
            
            self.utilities_module = self.get_module("utilities")
            self._log("info", f"   Utilities module: {'✅' if self.utilities_module else '❌'}")
            
            if not all([self.authentication_module, self.orchestration_module,
                       self.soa_mcp_module, self.utilities_module]):
                missing = []
                if not self.authentication_module:
                    missing.append("authentication")
                if not self.orchestration_module:
                    missing.append("orchestration")
                if not self.soa_mcp_module:
                    missing.append("soa_mcp")
                if not self.utilities_module:
                    missing.append("utilities")
                error_msg = f"Failed to load required modules: {', '.join(missing)}"
                self._log("error", f"   ❌ {error_msg}")
                raise Exception(error_msg)
            
            # Initialize SOA/MCP
            self._log("info", "   Initializing SOA/MCP...")
            await self.soa_mcp_module.initialize_soa_api_exposure()
            await self.soa_mcp_module.initialize_mcp_server_integration()
            self._log("info", "   ✅ SOA/MCP initialized")
            
            # Register capabilities
            self._log("info", "   Registering capabilities...")
            # Register capabilities with curator (Phase 2 pattern - simplified for Smart City)
            await self.soa_mcp_module.register_capabilities()
            self._log("info", "   ✅ Capabilities registered")
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric(
                "security_guard_initialized",
                1.0,
                {"service": "SecurityGuardService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "security_guard_initialize_complete",
                success=True
            )
            
            self._log("info", "✅ Security Guard Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e,
                "security_guard_initialize",
                {
                    "service": "SecurityGuardService",
                    "error_type": type(e).__name__
                }
            )
            
            self.service_health = "unhealthy"
            # Store error for debugging
            self.last_error = str(e)
            
            # Log failure
            await self.log_operation_with_telemetry(
                "security_guard_initialize_complete",
                success=False,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Record health metric
            await self.record_health_metric(
                "security_guard_initialized",
                0.0,
                metadata={"error_type": type(e).__name__}
            )
            
            error_msg = f"❌ Failed to initialize Security Guard Service: {e}"
            self._log("error", error_msg)
            import traceback
            self._log("error", f"Traceback: {traceback.format_exc()}")
            return False
    
    # ============================================================================
    # AUTHENTICATION METHODS - Delegate to authentication module
    # ============================================================================
    
    async def register_user(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Register new user via AuthAbstraction."""
        return await self.authentication_module.register_user(request)
    
    async def authenticate_user(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user credentials."""
        return await self.authentication_module.authenticate_user(request)
    
    async def authorize_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Authorize user action on resource."""
        return await self.authentication_module.authorize_action(request)
    
    # ============================================================================
    # ORCHESTRATION METHODS - Delegate to orchestration module
    # ============================================================================
    
    async def orchestrate_security_communication(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate security communication gateway."""
        return await self.orchestration_module.orchestrate_security_communication(request)
    
    async def orchestrate_zero_trust_policy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate zero-trust policy enforcement."""
        return await self.orchestration_module.orchestrate_zero_trust_policy(request)
    
    async def orchestrate_tenant_isolation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate tenant isolation enforcement."""
        return await self.orchestration_module.orchestrate_tenant_isolation(request)
    
    # ============================================================================
    # UTILITY METHODS - Delegate to utilities module
    # ============================================================================
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Security Guard service capabilities."""
        return await self.utilities_module.get_service_capabilities()
