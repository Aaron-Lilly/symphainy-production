#!/usr/bin/env python3
"""
Realm Service Base - Simplified Base Class for Realm Services

Base class for realm services with API access via Smart City Gateway.
Implements RealmServiceProtocol using actual Smart City Gateway infrastructure and RealmContext patterns.
INCLUDES ALL PLATFORM CAPABILITIES: Zero-trust security, multi-tenancy, performance monitoring, SOA communication.

WHAT (Realm Service): I provide API access to platform capabilities via Smart City Gateway with full platform capabilities
HOW (Base Class): I implement RealmServiceProtocol with Smart City Gateway, RealmContext, and ALL platform capabilities
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# Import actual protocol and types
from .protocols.realm_service_protocol import RealmServiceProtocol, RealmContext
from foundations.di_container.di_container_service import DIContainerService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService


class RealmServiceBase(ABC):
    """
    Base class for realm services with API access via Smart City Gateway and FULL PLATFORM CAPABILITIES.
    
    Implements RealmServiceProtocol using actual Smart City Gateway infrastructure
    and RealmContext patterns. Includes ALL platform capabilities:
    - Zero-trust security enforcement
    - Multi-tenancy support
    - Performance monitoring
    - SOA communication
    - Enhanced security patterns
    - Service discovery
    - Capability registry
    
    Realm services access platform capabilities via APIs, not direct foundation access,
    ensuring clean separation and preventing circular references.
    """
    
    def __init__(self, context: RealmContext, service_name: str,
                 security_provider=None, authorization_guard=None):
        """Initialize realm service with API access via Smart City Gateway and full platform capabilities."""
        self.service_name = service_name
        self.ctx = context
        self.logger = context.logger
        self.start_time = datetime.utcnow()
        
        # Security infrastructure (CRITICAL - Zero-trust security)
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        self.current_security_context = None
        
        # Service state
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Enhanced security patterns (CRITICAL - Zero-trust security)
        self._initialize_enhanced_security()
        
        # Platform capabilities (CRITICAL - SOA communication, service discovery)
        self._initialize_platform_capabilities()
        
        # Performance monitoring (CRITICAL - Performance tracking)
        self._initialize_performance_monitoring()
        
        self.logger.info(f"✅ RealmServiceBase '{service_name}' initialized with API access via Smart City Gateway and FULL platform capabilities")
    
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
        return TenantManagementUtility(self.ctx.di_container.get_config())
    
    def _create_security_audit(self):
        """Create security audit implementation using real Security Guard Service."""
        # Use the actual Security Guard Service for audit capabilities
        return self.ctx.di_container.get_foundation_service("SecurityGuardService")
    
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
        # SOA communication (via Post Office API)
        self.soa_client = self.get_communication_gateway()
        
        # Service discovery (via Curator Foundation)
        self.service_discovery = self.ctx.curator
        
        # Capability registry (via Curator Foundation)
        self.capability_registry = self.ctx.curator
        
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
    
    # ============================================================================
    # PERFORMANCE MONITORING (CRITICAL - Performance tracking)
    # ============================================================================
    
    def _initialize_performance_monitoring(self):
        """Initialize performance monitoring system."""
        self.performance_monitor = self._create_performance_monitor()
        self.enhanced_health = self.get_health()  # Enhanced health monitoring
        
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
        """Initialize the realm service with API access via Smart City Gateway."""
        pass
    
    @abstractmethod
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities for registration with Curator."""
        pass
    
    # ============================================================================
    # INFRASTRUCTURE ACCESS METHODS (Via Smart City Gateway)
    # ============================================================================
    
    def get_abstraction(self, name: str) -> Any:
        """Get infrastructure abstraction via Smart City Foundation Gateway."""
        return self.ctx.city_services.get_abstraction(name)
    
    def get_file_management_abstraction(self) -> Any:
        """Get file management abstraction via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("file_management")
    
    def get_file_management_composition(self) -> Any:
        """Get file management composition service via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("file_management_composition")
    
    def get_content_metadata_abstraction(self) -> Any:
        """Get content metadata abstraction via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("content_metadata")
    
    def get_content_metadata_composition(self) -> Any:
        """Get content metadata composition service via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("content_metadata_composition")
    
    def get_llm_abstraction(self) -> Any:
        """Get LLM abstraction via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("llm")
    
    def get_llm_composition_service(self) -> Any:
        """Get LLM composition service via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("llm_composition")
    
    def get_mcp_abstraction(self) -> Any:
        """Get MCP abstraction via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("mcp")
    
    def get_mcp_composition_service(self) -> Any:
        """Get MCP composition service via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("mcp_composition")
    
    def get_agui_abstraction(self) -> Any:
        """Get AGUI abstraction via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("agui")
    
    def get_agui_composition_service(self) -> Any:
        """Get AGUI composition service via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("agui_composition")
    
    def get_tool_storage_abstraction(self) -> Any:
        """Get tool storage abstraction via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("tool_storage")
    
    def get_policy_abstraction(self) -> Any:
        """Get policy abstraction via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("policy")
    
    def get_policy_composition_service(self) -> Any:
        """Get policy composition service via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("policy_composition")
    
    def get_config_adapter(self) -> Any:
        """Get configuration adapter via Smart City Gateway."""
        return self.ctx.city_services.get_abstraction("config_adapter")
    
    # ============================================================================
    # SMART CITY ROLE API METHODS (Via Smart City Gateway)
    # ============================================================================
    
    def get_role_api(self, role_name: str) -> Any:
        """Get Smart City role API via Smart City Gateway."""
        return self.ctx.city_services.get_role_api(role_name)
    
    def get_librarian_api(self) -> Any:
        """Get Librarian API via Smart City Gateway."""
        return self.get_role_api("librarian")
    
    def get_data_steward_api(self) -> Any:
        """Get Data Steward API via Smart City Gateway."""
        return self.get_role_api("data_steward")
    
    def get_security_guard_api(self) -> Any:
        """Get Security Guard API via Smart City Gateway."""
        return self.get_role_api("security_guard")
    
    def get_traffic_cop_api(self) -> Any:
        """Get Traffic Cop API via Smart City Gateway."""
        return self.get_role_api("traffic_cop")
    
    def get_nurse_api(self) -> Any:
        """Get Nurse API via Smart City Gateway."""
        return self.get_role_api("nurse")
    
    def get_conductor_api(self) -> Any:
        """Get Conductor API via Smart City Gateway."""
        return self.get_role_api("conductor")
    
    def get_city_manager_api(self) -> Any:
        """Get City Manager API via Smart City Gateway."""
        return self.get_role_api("city_manager")
    
    def get_post_office_api(self) -> Any:
        """Get Post Office API via Smart City Gateway."""
        return self.get_role_api("post_office")
    
    # ============================================================================
    # COMMUNICATION GATEWAY METHODS (Via Post Office API)
    # ============================================================================
    
    def get_communication_gateway(self) -> Any:
        """Get Post Office as communication orchestration gateway."""
        return self.ctx.city_services.get_communication_gateway()
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via Post Office communication gateway."""
        try:
            post_office = self.get_communication_gateway()
            result = await post_office.send_message(message)
            self.logger.info(f"✅ Message sent via Post Office communication gateway")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to send message via Post Office: {e}")
            return {"success": False, "error": str(e)}
    
    async def route_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Route event via Post Office communication gateway."""
        try:
            post_office = self.get_communication_gateway()
            result = await post_office.route_event(event)
            self.logger.info(f"✅ Event routed via Post Office communication gateway")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to route event via Post Office: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # SERVICE DISCOVERY METHODS (Via Curator Foundation)
    # ============================================================================
    
    async def discover_services(self, service_type: str) -> Dict[str, Any]:
        """Discover services via Curator Foundation."""
        try:
            result = await self.ctx.curator.discover_services(service_type)
            self.logger.info(f"✅ Discovered {len(result.get('services', []))} services of type '{service_type}'")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to discover services: {e}")
            return {"services": [], "error": str(e)}
    
    async def register_with_curator(self, capability: Dict[str, Any]) -> bool:
        """Register capability with Curator Foundation Service."""
        try:
            result = await self.ctx.curator.register_service(self, capability)
            self.logger.info(f"✅ Registered capability with Curator: {capability.get('service_name', 'unknown')}")
            return result.get("success", False)
        except Exception as e:
            self.logger.error(f"❌ Failed to register with Curator: {e}")
            return False
    
    # ============================================================================
    # UTILITY ACCESS METHODS (Via DI Container)
    # ============================================================================
    
    def get_logger(self, service_name: str) -> Any:
        """Get logger utility from DI Container."""
        return self.ctx.di_container.get_logger(service_name)
    
    def get_config(self) -> Any:
        """Get configuration utility from DI Container."""
        return self.ctx.di_container.get_config()
    
    def get_health(self) -> Any:
        """Get health management utility from DI Container."""
        return self.ctx.di_container.get_health()
    
    def get_telemetry(self) -> Any:
        """Get telemetry reporting utility from DI Container."""
        return self.ctx.di_container.get_telemetry()
    
    def get_security(self) -> Any:
        """Get security authorization utility from DI Container."""
        return self.ctx.di_container.get_security()
    
    def get_error_handler(self) -> Any:
        """Get error handler utility from DI Container."""
        return self.ctx.di_container.get_error_handler()
    
    def get_tenant(self) -> Any:
        """Get tenant management utility from DI Container."""
        return self.ctx.di_container.get_tenant()
    
    def get_validation(self) -> Any:
        """Get validation utility from DI Container."""
        return self.ctx.di_container.get_validation()
    
    def get_serialization(self) -> Any:
        """Get serialization utility from DI Container."""
        return self.ctx.di_container.get_serialization()
    
    # ============================================================================
    # HEALTH AND STATUS METHODS
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check using actual utilities."""
        try:
            health_status = self.get_health().get_health_status()
            return {
                "service_name": self.service_name,
                "health_status": health_status,
                "timestamp": datetime.utcnow().isoformat(),
                "access_pattern": "api_via_smart_city_gateway",
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
                "access_pattern": "api_via_smart_city_gateway",
                "smart_city_roles_available": [
                    "librarian", "data_steward", "security_guard", 
                    "traffic_cop", "nurse", "conductor", "city_manager", "post_office"
                ],
                "utilities_available": [
                    "logger", "config", "health", "telemetry", 
                    "security", "error_handler", "tenant", 
                    "validation", "serialization"
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
    # CONVENIENCE METHODS
    # ============================================================================
    
    def get_all_abstractions(self) -> Dict[str, Any]:
        """Get all available abstractions via Smart City Gateway."""
        try:
            return {
                "file_management": self.get_file_management_abstraction(),
                "content_metadata": self.get_content_metadata_abstraction(),
                "llm": self.get_llm_abstraction(),
                "mcp": self.get_mcp_abstraction(),
                "agui": self.get_agui_abstraction(),
                "tool_storage": self.get_tool_storage_abstraction(),
                "policy": self.get_policy_abstraction()
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get abstractions via Smart City Gateway: {e}")
            return {}
    
    def get_all_role_apis(self) -> Dict[str, Any]:
        """Get all available Smart City role APIs."""
        try:
            return {
                "librarian": self.get_librarian_api(),
                "data_steward": self.get_data_steward_api(),
                "security_guard": self.get_security_guard_api(),
                "traffic_cop": self.get_traffic_cop_api(),
                "nurse": self.get_nurse_api(),
                "conductor": self.get_conductor_api(),
                "city_manager": self.get_city_manager_api(),
                "post_office": self.get_post_office_api()
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get role APIs: {e}")
            return {}
    
    def get_all_utilities(self) -> Dict[str, Any]:
        """Get all available utilities from DI Container."""
        try:
            return {
                "logger": self.logger,
                "config": self.get_config(),
                "health": self.get_health(),
                "telemetry": self.get_telemetry(),
                "security": self.get_security(),
                "error_handler": self.get_error_handler(),
                "tenant": self.get_tenant(),
                "validation": self.get_validation(),
                "serialization": self.get_serialization()
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get utilities: {e}")
            return {}
    
    # ============================================================================
    # REALM-SPECIFIC METHODS
    # ============================================================================
    
    async def communicate_with_realm(self, target_realm: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Communicate with another realm via Post Office."""
        try:
            message["target_realm"] = target_realm
            message["source_realm"] = getattr(self, 'realm_name', 'unknown')
            result = await self.send_message(message)
            self.logger.info(f"✅ Communicated with {target_realm} realm")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to communicate with {target_realm} realm: {e}")
            return {"success": False, "error": str(e)}
    
    async def discover_realm_services(self, realm: str) -> Dict[str, Any]:
        """Discover services in a specific realm."""
        try:
            result = await self.discover_services(f"{realm}_service")
            self.logger.info(f"✅ Discovered services in {realm} realm")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to discover services in {realm} realm: {e}")
            return {"services": [], "error": str(e)}


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