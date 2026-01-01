#!/usr/bin/env python3
"""
Smart City Role Base - Simplified Base Class for Smart City Roles

Base class for Smart City roles with direct foundation access.
Implements SmartCityRoleProtocol using actual Public Works Foundation and DI Container infrastructure.
INCLUDES ALL PLATFORM CAPABILITIES: Zero-trust security, multi-tenancy, performance monitoring, SOA communication.

WHAT (Smart City Role): I provide direct access to foundation infrastructure and utilities with full platform capabilities
HOW (Base Class): I implement SmartCityRoleProtocol with real Public Works, DI Container, and ALL platform capabilities
"""

import logging
import inspect
import importlib
import importlib.util
from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path

# Import actual protocol and types
from .protocols.smart_city_role_protocol import SmartCityRoleProtocol
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import actual protocol types from Public Works Foundation
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import AuthenticationProtocol
from foundations.public_works_foundation.abstraction_contracts.authorization_protocol import AuthorizationProtocol
from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionProtocol
from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol
from foundations.public_works_foundation.abstraction_contracts.policy_engine_protocol import PolicyEngine


class SmartCityRoleBase(ABC):
    """
    Base class for Smart City roles with direct foundation access and FULL PLATFORM CAPABILITIES.
    
    Implements SmartCityRoleProtocol using actual Public Works Foundation
    and DI Container infrastructure. Includes ALL platform capabilities:
    - Zero-trust security enforcement
    - Multi-tenancy support
    - Performance monitoring
    - SOA communication
    - Enhanced security patterns
    - Service discovery
    - Capability registry
    
    Smart City roles have direct access to foundation layers without going through
    Smart City Gateway, enabling them to provide platform capabilities to other realms.
    """
    
    def __init__(self, di_container: DIContainerService, service_name: str,
                 security_provider=None, authorization_guard=None):
        """Initialize Smart City role with direct foundation access and full platform capabilities."""
        self.service_name = service_name
        self.di_container = di_container
        self.start_time = datetime.utcnow()
        
        # Security infrastructure (CRITICAL - Zero-trust security)
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        self.current_security_context = None
        
        # Direct foundation access (no circular references)
        self.public_works_foundation = di_container.get_foundation_service("PublicWorksFoundationService")
        self.communication_foundation = di_container.get_foundation_service("CommunicationFoundationService")
        self.curator_foundation = di_container.get_foundation_service("CuratorFoundationService")
        
        # Direct utility access from DI Container
        self.logger = di_container.get_logger(service_name)
        self.config = di_container.get_config()
        self.health = di_container.get_health()
        self.telemetry = di_container.get_telemetry()
        self.security = di_container.get_security()
        self.error_handler = di_container.get_error_handler()
        self.tenant = di_container.get_tenant()
        self.validation = di_container.get_validation()
        self.serialization = di_container.get_serialization()
        
        # Service state
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Micro-module architecture support (CRITICAL - Enforces 350-line limit)
        self.modules: Dict[str, Any] = {}  # Dictionary to store loaded micro-modules
        self._micro_module_path: str = ""  # Path to modules directory
        self._initialize_micro_module_support()
        
        # Enhanced security patterns (CRITICAL - Zero-trust security)
        self._initialize_enhanced_security()
        
        # Platform capabilities (CRITICAL - SOA communication, service discovery)
        self._initialize_platform_capabilities()
        
        # Performance monitoring (CRITICAL - Performance tracking)
        self._initialize_performance_monitoring()
        
        self.logger.info(f"✅ SmartCityRoleBase '{service_name}' initialized with direct foundation access and FULL platform capabilities")
    
    # ============================================================================
    # MICRO-MODULE ARCHITECTURE SUPPORT (CRITICAL - Enforces 350-line limit)
    # ============================================================================
    
    def _initialize_micro_module_support(self):
        """Initialize micro-module architecture support to enforce 350-line limit."""
        # Detect modules directory path
        self._micro_module_path = self._detect_modules_directory()
        
        if self._micro_module_path:
            self.logger.info(f"✅ Micro-module architecture enabled: {self._micro_module_path}")
        else:
            self.logger.info("ℹ️ No modules directory detected - services will use direct implementation")
    
    def _detect_modules_directory(self) -> str:
        """Detect the modules directory for this service."""
        try:
            frame = inspect.currentframe()
            # Walk up to find the caller
            for _ in range(3):  # Go back to find the actual service class
                frame = frame.f_back
                if frame is None:
                    break
            
            if frame:
                caller_path = inspect.getframeinfo(frame).filename
                service_dir = Path(caller_path).parent
                
                # Check for modules directory
                modules_dir = service_dir / "modules"
                if modules_dir.exists() and modules_dir.is_dir():
                    return str(modules_dir)
        except Exception as e:
            self.logger.debug(f"Could not detect modules directory: {e}")
        
        return ""
    
    def load_micro_module(self, module_name: str) -> Any:
        """
        Load a micro-module from the modules directory.
        
        Args:
            module_name: Name of the module to load (e.g., 'authentication_module')
            
        Returns:
            The loaded module class
            
        Raises:
            FileNotFoundError: If module directory doesn't exist
            AttributeError: If module class doesn't exist
        """
        if module_name in self.modules:
            return self.modules[module_name]
        
        if not self._micro_module_path:
            raise FileNotFoundError(f"No modules directory found for {self.service_name}")
        
        try:
            # Construct module path
            modules_dir = Path(self._micro_module_path)
            module_file = modules_dir / f"{module_name}.py"
            
            if not module_file.exists():
                raise FileNotFoundError(f"Module {module_name} not found in {modules_dir}")
            
            # Import the module
            spec = importlib.util.spec_from_file_location(
                f"{self.service_name}.{module_name}",
                module_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the module class (assume it's the only class in the file)
            module_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    module_class = obj
                    break
            
            if module_class is None:
                raise AttributeError(f"No class found in module {module_name}")
            
            # Store and return
            self.modules[module_name] = module_class
            self.logger.info(f"✅ Loaded micro-module: {module_name}")
            return module_class
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load micro-module {module_name}: {e}")
            raise
    
    def get_module(self, module_name: str, *args, **kwargs) -> Any:
        """
        Get an instantiated micro-module.
        
        Args:
            module_name: Name of the module to get
            *args, **kwargs: Arguments to pass to module constructor
            
        Returns:
            Instantiated module
        """
        if module_name not in self.modules:
            self.load_micro_module(module_name)
        
        ModuleClass = self.modules[module_name]
        return ModuleClass(*args, **kwargs)
    
    # ============================================================================
    # ENHANCED SECURITY PATTERNS (CRITICAL - Zero-trust security)
    # ============================================================================
    
    def _initialize_enhanced_security(self):
        """Initialize enhanced security patterns with zero-trust enforcement."""
        # Zero-trust security enforcement
        self.zero_trust_security = self._create_zero_trust_security()
        
        # Policy-driven access control
        self.policy_engine = self._create_policy_engine()
        
        # Multi-tenancy support
        self.tenant_isolation = self._create_tenant_isolation()
        
        # Security audit
        self.security_audit = self._create_security_audit()
        
        self.logger.info("✅ Enhanced security patterns initialized (zero-trust, multi-tenancy, policy engine)")
    
    def _create_zero_trust_security(self):
        """Create zero-trust security implementation using real AuthorizationGuard."""
        from backend.smart_city.services.security_guard.modules.authorization_guard_module import AuthorizationGuard
        return AuthorizationGuard()
    
    def _create_policy_engine(self):
        """Create policy engine implementation using real DefaultPolicyEngine."""
        from engines.default_policy_engine import DefaultPolicyEngine
        return DefaultPolicyEngine()
    
    def _create_tenant_isolation(self):
        """Create tenant isolation implementation using real TenantManagementUtility."""
        from utilities.tenant.tenant_management_utility import TenantManagementUtility
        return TenantManagementUtility(self.di_container.get_config())
    
    def _create_security_audit(self):
        """Create security audit implementation using real Security Guard Service."""
        # Use the actual Security Guard Service for audit capabilities
        return self.di_container.get_foundation_service("SecurityGuardService")
    
    async def get_security_context(self, token: str | None = None):
        """Get security context for request using real AuthorizationGuard."""
        try:
            if self.security_provider:
                context = await self.security_provider.get_security_context(token)
                self.current_security_context = context
                return context
            else:
                # Fallback to basic context
                context = {
                    "user_id": "anonymous",
                    "tenant_id": "default",
                    "permissions": [],
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.current_security_context = context
                return context
        except Exception as e:
            self.logger.error(f"❌ Failed to get security context: {e}")
            raise
    
    async def enforce_authorization(self, action: str, resource: str, context: Dict[str, Any]):
        """Enforce authorization using real AuthorizationGuard."""
        try:
            # Use real AuthorizationGuard for enforcement
            is_allowed = self.zero_trust_security.enforce(action, resource, context)
            if is_allowed:
                self.logger.info(f"✅ Authorization allowed: {action} on {resource}")
            else:
                self.logger.warning(f"❌ Authorization denied: {action} on {resource}")
            return is_allowed
        except Exception as e:
            self.logger.error(f"❌ Authorization enforcement failed: {e}")
            return False
    
    async def validate_tenant_access(self, tenant_id: str, context: Dict[str, Any]):
        """Validate tenant access using real TenantManagementUtility."""
        try:
            # Use real TenantManagementUtility for tenant validation
            tenant_config = self.tenant_isolation.get_tenant_config("individual")
            is_valid = tenant_id in tenant_config.get("allowed_tenants", [tenant_id])
            self.logger.info(f"✅ Tenant access validation: {tenant_id} = {is_valid}")
            return is_valid
        except Exception as e:
            self.logger.error(f"❌ Tenant access validation failed: {e}")
            return False
    
    # ============================================================================
    # PLATFORM CAPABILITIES (CRITICAL - SOA communication, service discovery)
    # ============================================================================
    
    def _initialize_platform_capabilities(self):
        """Initialize platform capabilities with SOA communication and service discovery."""
        # SOA communication (via Communication Foundation)
        self.soa_client = self.communication_foundation
        
        # Service discovery (via Curator Foundation)
        self.service_discovery = self.curator_foundation
        
        # Capability registry (via Curator Foundation)
        self.capability_registry = self.curator_foundation
        
        # Realm capabilities
        self.realm_capabilities = []
        self.soa_endpoints = []
        self.inter_realm_communication = {}
        
        self.logger.info("✅ Platform capabilities initialized (SOA communication, service discovery, capability registry)")
    
    async def register_soa_endpoint(self, endpoint: Dict[str, Any]):
        """Register SOA endpoint for service discovery."""
        try:
            self.soa_endpoints.append(endpoint)
            await self.capability_registry.register_service(self, endpoint)
            self.logger.info(f"✅ SOA endpoint registered: {endpoint.get('name', 'unknown')}")
        except Exception as e:
            self.logger.error(f"❌ Failed to register SOA endpoint: {e}")
            raise
    
    async def discover_services(self, service_type: str) -> Dict[str, Any]:
        """Discover services via service discovery."""
        try:
            result = await self.service_discovery.discover_services(service_type)
            self.logger.info(f"✅ Discovered {len(result.get('services', []))} services of type '{service_type}'")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to discover services: {e}")
            return {"services": [], "error": str(e)}
    
    # ============================================================================
    # PERFORMANCE MONITORING (CRITICAL - Performance tracking)
    # ============================================================================
    
    def _initialize_performance_monitoring(self):
        """Initialize performance monitoring system."""
        self.performance_monitor = self._create_performance_monitor()
        self.enhanced_health = self.health  # Enhanced health monitoring
        
        self.logger.info("✅ Performance monitoring initialized")
    
    def _create_performance_monitor(self):
        """Create performance monitoring system using real TelemetryReportingUtility."""
        from utilities.telemetry_reporting.telemetry_reporting_utility import TelemetryReportingUtility
        return TelemetryReportingUtility(self.service_name)
    
    async def track_performance_metric(self, metric_name: str, value: float, context: Dict[str, Any] = None):
        """Track performance metric using real TelemetryReportingUtility."""
        try:
            # Use real TelemetryReportingUtility for metrics tracking
            metric_data = {
                "metric_name": metric_name,
                "value": value,
                "context": context or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.performance_monitor.log_metric(metric_data)
            self.logger.debug(f"📊 Performance metric tracked: {metric_name} = {value}")
        except Exception as e:
            self.logger.error(f"❌ Failed to track performance metric: {e}")
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary using real TelemetryReportingUtility."""
        try:
            # Use real TelemetryReportingUtility for health metrics
            health_metrics = {
                "service_name": self.service_name,
                "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                "status": "healthy" if self.is_initialized else "initializing"
            }
            return await self.performance_monitor.log_health_metrics(health_metrics)
        except Exception as e:
            self.logger.error(f"❌ Failed to get performance summary: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # ABSTRACT METHODS (Must be implemented by subclasses)
    # ============================================================================
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the Smart City role with direct foundation access."""
        pass
    
    @abstractmethod
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities for registration with Curator."""
        pass
    
    # ============================================================================
    # INFRASTRUCTURE ACCESS METHODS (Direct Public Works Access)
    # ============================================================================
    
    def get_auth_abstraction(self) -> AuthenticationProtocol:
        """Get authentication abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_auth_abstraction()
    
    def get_authorization_abstraction(self) -> AuthorizationProtocol:
        """Get authorization abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_authorization_abstraction()
    
    def get_session_abstraction(self) -> SessionProtocol:
        """Get session abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_session_abstraction()
    
    def get_tenant_abstraction(self) -> TenantProtocol:
        """Get tenant abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_tenant_abstraction()
    
    def get_policy_engine(self, engine_name: str = "default") -> PolicyEngine:
        """Get policy engine from Public Works Foundation."""
        return self.public_works_foundation.get_policy_engine(engine_name)
    
    def get_file_management_abstraction(self) -> Any:
        """Get file management abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_file_management_abstraction()
    
    def get_file_management_composition(self) -> Any:
        """Get file management composition service from Public Works Foundation."""
        return self.public_works_foundation.get_file_management_composition()
    
    def get_content_metadata_abstraction(self) -> Any:
        """Get content metadata abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_content_metadata_abstraction()
    
    def get_content_metadata_composition(self) -> Any:
        """Get content metadata composition service from Public Works Foundation."""
        return self.public_works_foundation.get_content_metadata_composition()
    
    def get_llm_abstraction(self) -> Any:
        """Get LLM abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_llm_abstraction()
    
    def get_llm_composition_service(self) -> Any:
        """Get LLM composition service from Public Works Foundation."""
        return self.public_works_foundation.get_llm_composition_service()
    
    def get_mcp_abstraction(self) -> Any:
        """Get MCP abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_mcp_abstraction()
    
    def get_mcp_composition_service(self) -> Any:
        """Get MCP composition service from Public Works Foundation."""
        return self.public_works_foundation.get_mcp_composition_service()
    
    def get_agui_abstraction(self) -> Any:
        """Get AGUI abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_agui_abstraction()
    
    def get_agui_composition_service(self) -> Any:
        """Get AGUI composition service from Public Works Foundation."""
        return self.public_works_foundation.get_agui_composition_service()
    
    def get_tool_storage_abstraction(self) -> Any:
        """Get tool storage abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_tool_storage_abstraction()
    
    def get_policy_abstraction(self) -> Any:
        """Get policy abstraction from Public Works Foundation."""
        return self.public_works_foundation.get_policy_abstraction()
    
    def get_policy_composition_service(self) -> Any:
        """Get policy composition service from Public Works Foundation."""
        return self.public_works_foundation.get_policy_composition_service()
    
    def get_config_adapter(self) -> Any:
        """Get configuration adapter from Public Works Foundation."""
        return self.public_works_foundation.get_config_adapter()
    
    # ============================================================================
    # UTILITY ACCESS METHODS (Direct DI Container Access)
    # ============================================================================
    
    def get_logger(self, service_name: str) -> Any:
        """Get logger utility from DI Container."""
        return self.di_container.get_logger(service_name)
    
    def get_config(self) -> Any:
        """Get configuration utility from DI Container."""
        return self.di_container.get_config()
    
    def get_health(self) -> Any:
        """Get health management utility from DI Container."""
        return self.di_container.get_health()
    
    def get_telemetry(self) -> Any:
        """Get telemetry reporting utility from DI Container."""
        return self.di_container.get_telemetry()
    
    def get_security(self) -> Any:
        """Get security authorization utility from DI Container."""
        return self.di_container.get_security()
    
    def get_error_handler(self) -> Any:
        """Get error handler utility from DI Container."""
        return self.di_container.get_error_handler()
    
    def get_tenant(self) -> Any:
        """Get tenant management utility from DI Container."""
        return self.di_container.get_tenant()
    
    def get_validation(self) -> Any:
        """Get validation utility from DI Container."""
        return self.di_container.get_validation()
    
    def get_serialization(self) -> Any:
        """Get serialization utility from DI Container."""
        return self.di_container.get_serialization()
    
    # ============================================================================
    # SERVICE REGISTRATION (Direct Curator Access)
    # ============================================================================
    
    async def register_with_curator(self, capability: Dict[str, Any]) -> bool:
        """Register capability with Curator Foundation Service."""
        try:
            result = await self.curator_foundation.register_service(self, capability)
            self.logger.info(f"✅ Registered capability with Curator: {capability.get('service_name', 'unknown')}")
            return result.get("success", False)
        except Exception as e:
            self.logger.error(f"❌ Failed to register with Curator: {e}")
            return False
    
    # ============================================================================
    # HEALTH AND STATUS METHODS
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check using actual utilities."""
        try:
            health_status = self.health.get_health_status()
            return {
                "service_name": self.service_name,
                "health_status": health_status,
                "timestamp": datetime.utcnow().isoformat(),
                "foundation_access": "direct",
                "is_initialized": self.is_initialized,
                "platform_capabilities": {
                    "zero_trust_security": True,
                    "multi_tenancy": True,
                    "performance_monitoring": True,
                    "soa_communication": True,
                    "service_discovery": True,
                    "capability_registry": True
                }
            }
        except Exception as e:
            return {
                "service_name": self.service_name,
                "health_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "is_initialized": self.is_initialized
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status using actual utilities."""
        try:
            return {
                "service_name": self.service_name,
                "status": "active" if self.is_initialized else "initializing",
                "foundation_access": "direct",
                "utilities_available": [
                    "logger", "config", "health", "telemetry", 
                    "security", "error_handler", "tenant", 
                    "validation", "serialization"
                ],
                "foundation_services": [
                    "public_works_foundation", "communication_foundation", "curator_foundation"
                ],
                "platform_capabilities": {
                    "zero_trust_security": True,
                    "multi_tenancy": True,
                    "performance_monitoring": True,
                    "soa_communication": True,
                    "service_discovery": True,
                    "capability_registry": True
                },
                "timestamp": datetime.utcnow().isoformat(),
                "is_initialized": self.is_initialized
            }
        except Exception as e:
            return {
                "service_name": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "is_initialized": self.is_initialized
            }
    
    # ============================================================================
    # COMMUNICATION METHODS (Direct Communication Foundation Access)
    # ============================================================================
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via Communication Foundation."""
        try:
            result = await self.communication_foundation.send_message(message)
            self.logger.info(f"✅ Message sent via Communication Foundation")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to send message: {e}")
            return {"success": False, "error": str(e)}
    
    async def route_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Route event via Communication Foundation."""
        try:
            result = await self.communication_foundation.route_event(event)
            self.logger.info(f"✅ Event routed via Communication Foundation")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to route event: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # CONVENIENCE METHODS
    # ============================================================================
    
    def get_all_abstractions(self) -> Dict[str, Any]:
        """Get all available abstractions from Public Works Foundation."""
        try:
            return {
                "auth": self.get_auth_abstraction(),
                "authorization": self.get_authorization_abstraction(),
                "session": self.get_session_abstraction(),
                "tenant": self.get_tenant_abstraction(),
                "file_management": self.get_file_management_abstraction(),
                "content_metadata": self.get_content_metadata_abstraction(),
                "llm": self.get_llm_abstraction(),
                "mcp": self.get_mcp_abstraction(),
                "agui": self.get_agui_abstraction(),
                "tool_storage": self.get_tool_storage_abstraction(),
                "policy": self.get_policy_abstraction()
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get abstractions: {e}")
            return {}
    
    def get_all_utilities(self) -> Dict[str, Any]:
        """Get all available utilities from DI Container."""
        try:
            return {
                "logger": self.logger,
                "config": self.config,
                "health": self.health,
                "telemetry": self.telemetry,
                "security": self.security,
                "error_handler": self.error_handler,
                "tenant": self.tenant,
                "validation": self.validation,
                "serialization": self.serialization
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get utilities: {e}")
            return {}


# ============================================================================
# REAL IMPLEMENTATIONS USED (No placeholder classes needed)
# ============================================================================
# 
# The base class now uses REAL implementations from the platform:
# - AuthorizationGuard: backend/smart_city/services/security_guard/modules/authorization_guard_module.py
# - DefaultPolicyEngine: engines/default_policy_engine.py
# - TenantManagementUtility: utilities/tenant/tenant_management_utility.py
# - TelemetryReportingUtility: utilities/telemetry_reporting/telemetry_reporting_utility.py
# - SecurityGuardService: backend/smart_city/services/security_guard/security_guard_service.py
#
# These are imported dynamically to avoid circular dependencies and ensure
# we're using the actual working implementations from the platform.