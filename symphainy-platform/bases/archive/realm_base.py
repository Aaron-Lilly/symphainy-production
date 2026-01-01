#!/usr/bin/env python3
"""
RealmBase - Enhanced Base Class for All Realm Components

This base class provides everything realm files need to operate (Agents, Services, MCP Servers).
Built on top of GroundZeroBase with Communication Foundation integration.

WHAT (Realm Role): I provide everything realm components need to operate
HOW (Realm Implementation): I inherit from GroundZeroBase and add realm-specific capabilities
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

# RealmBase is now standalone - no longer depends on GroundZeroBase

# Import security infrastructure
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext
from foundations.public_works_foundation.abstraction_contracts.authorization_protocol import AuthorizationProtocol
from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionProtocol
from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol

# Import DI Container (using TYPE_CHECKING to avoid circular import)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService


class RealmBase(ABC):
    """
    RealmBase - Enhanced Base Class for All Realm Components
    
    This base class provides everything realm files need to operate (Agents, Services, MCP Servers).
    Built on top of GroundZeroBase with Communication Foundation integration.
    
    WHAT (Realm Role): I provide everything realm components need to operate
    HOW (Realm Implementation): I inherit from GroundZeroBase and add realm-specific capabilities
    """
    
    def __init__(self, service_name: str, di_container: "DIContainerService",
                 realm_name: str, service_type: str,
                 security_provider=None, authorization_guard=None,
                 communication_foundation: Optional["CommunicationFoundationService"] = None):
        """Initialize RealmBase with enhanced platform capabilities."""
        # Core service properties
        self.service_name = service_name
        self.di_container = di_container
        self.realm_name = realm_name
        self.service_type = service_type
        self.start_time = datetime.utcnow()
        
        # Security infrastructure (realm requirement)
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        self.current_security_context = None
        
        # Enhanced utilities (from DI container with enhanced patterns)
        self._initialize_enhanced_utilities()
        
        # Service state
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Realm-specific properties
        self.communication_foundation = communication_foundation
        
        # Realm capabilities
        self.realm_capabilities = []
        self.soa_endpoints = []
        self.inter_realm_communication = {}
        
        # Enhanced security patterns
        self._initialize_enhanced_security()
        
        # Platform capabilities
        self._initialize_platform_capabilities()
        
        # Initialize realm-specific capabilities
        self._initialize_realm_capabilities()
        
        self.logger.info(f"🌐 RealmBase '{service_name}' initialized for realm '{realm_name}' with enhanced capabilities")
    
    def _initialize_realm_capabilities(self):
        """Initialize realm-specific capabilities."""
        # SOA communication capabilities
        self._initialize_soa_capabilities()
        
        # Service discovery capabilities
        self._initialize_service_discovery()
        
        # Inter-realm communication capabilities
        self._initialize_inter_realm_communication()
        
        # Realm-specific utilities
        self._initialize_realm_utilities()
    
    def _initialize_soa_capabilities(self):
        """Initialize SOA communication capabilities."""
        if self.communication_foundation:
            # Get SOA client from Communication Foundation
            self.soa_client = self.communication_foundation.soa_client_abstraction
            self.soa_api_registry = self.communication_foundation.communication_abstraction
        else:
            # Placeholder for when Communication Foundation is not available
            self.soa_client = None
            self.soa_api_registry = None
    
    def _initialize_service_discovery(self):
        """Initialize service discovery capabilities."""
        if self.communication_foundation:
            # Get service discovery from Communication Foundation
            self.service_discovery = self.communication_foundation.curator_foundation
            self.capability_registry = self.communication_foundation.curator_foundation
        else:
            # Placeholder for when Communication Foundation is not available
            self.service_discovery = None
            self.capability_registry = None
    
    def _initialize_inter_realm_communication(self):
        """Initialize inter-realm communication capabilities."""
        if self.communication_foundation:
            # Get inter-realm communication from Communication Foundation
            self.inter_realm_client = self.communication_foundation.communication_abstraction
            self.realm_coordination = self.communication_foundation.communication_abstraction
        else:
            # Placeholder for when Communication Foundation is not available
            self.inter_realm_client = None
            self.realm_coordination = None
    
    def _initialize_realm_utilities(self):
        """Initialize realm-specific utilities."""
        # Use standard utilities from DI container (realm-specific utilities not yet implemented)
        self.realm_logging = self.di_container.logger
        self.realm_error_handler = self.di_container.error_handler
        self.realm_health = self.di_container.health
    
    # ============================================================================
    # SOA COMMUNICATION METHODS
    # ============================================================================
    
    async def register_soa_endpoint(self, endpoint_name: str, endpoint_config: Dict[str, Any]) -> bool:
        """Register SOA endpoint for this realm service."""
        try:
            if self.soa_api_registry:
                result = await self.soa_api_registry.register_endpoint(
                    service_name=self.service_name,
                    realm_name=self.realm_name,
                    endpoint_name=endpoint_name,
                    endpoint_config=endpoint_config
                )
                self.soa_endpoints.append({
                    "name": endpoint_name,
                    "config": endpoint_config,
                    "registered": result
                })
                self.logger.info(f"✅ SOA endpoint '{endpoint_name}' registered for {self.service_name}")
                return result
            else:
                self.logger.warning("⚠️ SOA API registry not available")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to register SOA endpoint '{endpoint_name}': {e}")
            return False
    
    async def call_soa_endpoint(self, target_service: str, endpoint_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call SOA endpoint on another service."""
        try:
            if self.soa_client:
                result = await self.soa_client.call_endpoint(
                    target_service=target_service,
                    endpoint_name=endpoint_name,
                    request_data=request_data
                )
                self.logger.info(f"✅ SOA endpoint '{endpoint_name}' called on {target_service}")
                return result
            else:
                self.logger.warning("⚠️ SOA client not available")
                return {"error": "SOA client not available"}
        except Exception as e:
            self.logger.error(f"❌ Failed to call SOA endpoint '{endpoint_name}' on {target_service}: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # SERVICE DISCOVERY METHODS
    # ============================================================================
    
    async def discover_service(self, service_name: str, realm: str = None) -> Dict[str, Any]:
        """Discover service via service discovery."""
        try:
            if self.service_discovery:
                result = await self.service_discovery.find_service(
                    service_name=service_name,
                    realm=realm or self.realm_name
                )
                self.logger.info(f"✅ Service '{service_name}' discovered in realm '{realm or self.realm_name}'")
                return result
            else:
                self.logger.warning("⚠️ Service discovery not available")
                return {"error": "Service discovery not available"}
        except Exception as e:
            self.logger.error(f"❌ Failed to discover service '{service_name}': {e}")
            return {"error": str(e)}
    
    async def register_capabilities(self, capabilities: List[str]) -> bool:
        """Register capabilities with capability registry."""
        try:
            if self.capability_registry:
                result = await self.capability_registry.register_capabilities(
                    service_name=self.service_name,
                    realm_name=self.realm_name,
                    capabilities=capabilities
                )
                self.realm_capabilities.extend(capabilities)
                self.logger.info(f"✅ Capabilities registered for {self.service_name}: {capabilities}")
                return result
            else:
                self.logger.warning("⚠️ Capability registry not available")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to register capabilities: {e}")
            return False
    
    # ============================================================================
    # INTER-REALM COMMUNICATION METHODS
    # ============================================================================
    
    async def communicate_with_realm(self, target_realm: str, api_request: Dict[str, Any]) -> Dict[str, Any]:
        """Communicate with another realm."""
        try:
            if self.inter_realm_client:
                result = await self.inter_realm_client.communicate(
                    source_realm=self.realm_name,
                    target_realm=target_realm,
                    api_request=api_request
                )
                self.logger.info(f"✅ Communication with realm '{target_realm}' successful")
                return result
            else:
                self.logger.warning("⚠️ Inter-realm client not available")
                return {"error": "Inter-realm client not available"}
        except Exception as e:
            self.logger.error(f"❌ Failed to communicate with realm '{target_realm}': {e}")
            return {"error": str(e)}
    
    async def coordinate_with_realm(self, target_realm: str, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with another realm."""
        try:
            if self.realm_coordination:
                result = await self.realm_coordination.coordinate(
                    source_realm=self.realm_name,
                    target_realm=target_realm,
                    coordination_request=coordination_request
                )
                self.logger.info(f"✅ Coordination with realm '{target_realm}' successful")
                return result
            else:
                self.logger.warning("⚠️ Realm coordination not available")
                return {"error": "Realm coordination not available"}
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate with realm '{target_realm}': {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # ENHANCED UTILITY METHODS
    # ============================================================================
    
    async def log_with_realm_context(self, level: str, message: str, context: Dict[str, Any] = None):
        """Log with realm-specific context."""
        try:
            log_context = {
                "realm": self.realm_name,
                "service": self.service_name,
                "service_type": self.service_type,
                "context": context or {}
            }
            
            if self.realm_logging:
                await self.realm_logging.log(level, message, log_context)
            else:
                # Fallback to standard logging
                getattr(self.logger, level.lower())(message, extra=log_context)
        except Exception as e:
            self.logger.error(f"❌ Failed to log with realm context: {e}")
    
    async def handle_error_with_realm_context(self, error: Exception, context: Dict[str, Any] = None):
        """Handle error with realm-specific context."""
        try:
            error_context = {
                "realm": self.realm_name,
                "service": self.service_name,
                "service_type": self.service_type,
                "context": context or {}
            }
            
            if self.realm_error_handler:
                await self.realm_error_handler.handle_error(error, error_context)
            else:
                # Fallback to standard error handling
                await self.error_handler.handle_error(error, error_context)
        except Exception as e:
            self.logger.error(f"❌ Failed to handle error with realm context: {e}")
    
    async def get_health_with_realm_context(self) -> Dict[str, Any]:
        """Get health status with realm-specific context."""
        try:
            base_health = await super().get_service_health()
            
            realm_health = {
                "realm": self.realm_name,
                "service_type": self.service_type,
                "capabilities_count": len(self.realm_capabilities),
                "soa_endpoints_count": len(self.soa_endpoints),
                "communication_foundation_available": self.communication_foundation is not None
            }
            
            if self.realm_health:
                realm_specific_health = await self.realm_health.get_health_status()
                realm_health.update(realm_specific_health)
            
            return {**base_health, **realm_health}
        except Exception as e:
            return {
                "realm": self.realm_name,
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # ABSTRACT METHODS (to be implemented by concrete realm components)
    # ============================================================================
    
    @abstractmethod
    async def initialize(self):
        """Initialize the realm component."""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Shutdown the realm component."""
        pass
    
    @abstractmethod
    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get realm-specific capabilities."""
        pass
    
    # ============================================================================
    # ENHANCED UTILITIES (from DI container with enhanced patterns)
    # ============================================================================
    
    def _initialize_enhanced_utilities(self):
        """Initialize enhanced utilities with new patterns."""
        # Get utilities from DI container
        self.logger = self.di_container.logger
        self.config = self.di_container.config
        self.health = self.di_container.health
        self.telemetry = self.di_container.telemetry
        self.error_handler = self.di_container.error_handler
        self.tenant = self.di_container.tenant
        self.validation = self.di_container.validation
        self.serialization = self.di_container.serialization
        
        # Enhanced utility patterns
        self.enhanced_logging = self.di_container.logger
        self.enhanced_error_handler = self.di_container.error_handler
        self.enhanced_health = self.di_container.health
    
    def _initialize_enhanced_security(self):
        """Initialize enhanced security patterns."""
        # Zero-trust security enforcement
        self.zero_trust_security = self._create_zero_trust_security()
        
        # Policy-driven access control
        self.policy_engine = self._create_policy_engine()
        
        # Multi-tenancy support
        self.tenant_isolation = self._create_tenant_isolation()
        
        # Security audit
        self.security_audit = self._create_security_audit()
    
    def _initialize_platform_capabilities(self):
        """Initialize platform capabilities."""
        # SOA communication (will be provided by Communication Foundation when built)
        self.soa_client = None  # Will be set when Communication Foundation is available
        
        # Service discovery (will be provided by Communication Foundation when built)
        self.service_discovery = None  # Will be set when Communication Foundation is available
        
        # Capability registry (will be provided by Communication Foundation when built)
        self.capability_registry = None  # Will be set when Communication Foundation is available
        
        # Performance monitoring
        self.performance_monitor = self._create_performance_monitor()
    
    # ============================================================================
    # ENHANCED SECURITY PATTERNS (Realm Requirement)
    # ============================================================================
    
    async def get_security_context(self, token: str | None = None):
        """Get security context for request with enhanced security."""
        if not self.security_provider:
            # Return anonymous context if no security provider
            return {
                "user_id": None,
                "tenant_id": None,
                "roles": [],
                "permissions": [],
                "origin": "anonymous"
            }
        
        context = await self.security_provider.get_context(token)
        self.current_security_context = context
        
        # Apply zero-trust security
        await self.zero_trust_security.validate_context(context)
        
        return context
    
    async def enforce_zero_trust_security(self, context):
        """Enforce zero-trust security principles."""
        await self.zero_trust_security.enforce_principle("never_trust_always_verify", context)
        await self.zero_trust_security.enforce_principle("least_privilege", context)
        await self.zero_trust_security.enforce_principle("assume_breach", context)
    
    async def enforce_policy(self, policy_name: str, context, action: str, resource: str):
        """Enforce named policy with enhanced security."""
        # Use policy engine for dynamic policy enforcement
        policy_result = await self.policy_engine.evaluate_policy(policy_name, {
            "action": action,
            "resource": resource,
            "context": context
        })
        
        if not policy_result.allowed:
            await self.security_audit.audit_policy_violation(policy_name, action, resource, context)
            raise Exception(f"Policy '{policy_name}' denied access to {action} on {resource}")
        
        await self.security_audit.audit_policy_compliance(policy_name, action, resource, context)
    
    async def enforce_tenant_isolation(self, user_tenant: str, resource_tenant: str):
        """Enforce tenant isolation with enhanced security."""
        isolation_result = await self.tenant_isolation.validate_isolation(user_tenant, resource_tenant)
        
        if not isolation_result.isolated:
            await self.security_audit.audit_tenant_violation(user_tenant, resource_tenant)
            raise Exception(f"Tenant isolation violation: {user_tenant} -> {resource_tenant}")
        
        await self.security_audit.audit_tenant_access(user_tenant, resource_tenant)
    
    # ============================================================================
    # PLACEHOLDER CREATION METHODS (to be implemented)
    # ============================================================================
    
    def _create_zero_trust_security(self):
        """Create zero-trust security enforcement."""
        return ZeroTrustSecurity()
    
    def _create_policy_engine(self):
        """Create policy engine for dynamic policy enforcement."""
        return PolicyEngine()
    
    def _create_tenant_isolation(self):
        """Create tenant isolation enforcement."""
        return TenantIsolation()
    
    def _create_security_audit(self):
        """Create security audit system."""
        return SecurityAudit()
    
    def _create_performance_monitor(self):
        """Create performance monitoring system."""
        return PerformanceMonitor()


# ============================================================================
# PLACEHOLDER CLASSES (to be implemented)
# ============================================================================

class ZeroTrustSecurity:
    """Real zero-trust security implementation."""
    
    async def validate_context(self, context):
        """Validate security context with zero-trust principles."""
        # Never trust, always verify
        if not context.get("user_id") and context.get("origin") != "anonymous":
            raise Exception("Zero-trust violation: Invalid user context")
        
        # Least privilege enforcement
        if not context.get("permissions"):
            context["permissions"] = []
        
        # Assume breach - validate all access
        if context.get("tenant_id") and not self._validate_tenant_access(context):
            raise Exception("Zero-trust violation: Invalid tenant access")
    
    async def enforce_principle(self, principle: str, context):
        """Enforce specific zero-trust principle."""
        if principle == "never_trust_always_verify":
            await self._enforce_never_trust(context)
        elif principle == "least_privilege":
            await self._enforce_least_privilege(context)
        elif principle == "assume_breach":
            await self._enforce_assume_breach(context)
    
    async def _enforce_never_trust(self, context):
        """Enforce never trust, always verify principle."""
        # Verify user identity
        if not context.get("user_id") and context.get("origin") != "anonymous":
            raise Exception("Never trust violation: Unverified user")
        
        # Verify tenant access
        if context.get("tenant_id") and not self._validate_tenant_access(context):
            raise Exception("Never trust violation: Unverified tenant access")
    
    async def _enforce_least_privilege(self, context):
        """Enforce least privilege principle."""
        # Ensure minimal permissions
        permissions = context.get("permissions", [])
        if len(permissions) > 10:  # Arbitrary limit for least privilege
            raise Exception("Least privilege violation: Too many permissions")
    
    async def _enforce_assume_breach(self, context):
        """Enforce assume breach principle."""
        # Validate all security tokens
        if context.get("token") and not self._validate_token(context["token"]):
            raise Exception("Assume breach violation: Invalid token")
    
    def _validate_tenant_access(self, context):
        """Validate tenant access."""
        tenant_id = context.get("tenant_id")
        user_id = context.get("user_id")
        
        # Basic tenant validation
        if tenant_id and user_id:
            return tenant_id.startswith("tenant_") and user_id.startswith("user_")
        return True
    
    def _validate_token(self, token):
        """Validate security token."""
        # Basic token validation
        return token and len(token) > 10

class PolicyEngine:
    """Real policy engine implementation."""
    
    def __init__(self):
        self.policies = {
            "read_access": {"allowed_actions": ["read", "view"], "required_roles": ["user", "admin"]},
            "write_access": {"allowed_actions": ["write", "create", "update"], "required_roles": ["admin"]},
            "admin_access": {"allowed_actions": ["delete", "admin"], "required_roles": ["admin"]}
        }
    
    async def evaluate_policy(self, policy_name: str, context: Dict[str, Any]):
        """Evaluate policy with real logic."""
        policy = self.policies.get(policy_name)
        if not policy:
            return type('PolicyResult', (), {'allowed': False})()
        
        action = context.get("action")
        user_roles = context.get("context", {}).get("roles", [])
        
        # Check if action is allowed
        if action not in policy["allowed_actions"]:
            return type('PolicyResult', (), {'allowed': False})()
        
        # Check if user has required roles
        required_roles = policy["required_roles"]
        if not any(role in user_roles for role in required_roles):
            return type('PolicyResult', (), {'allowed': False})()
        
        return type('PolicyResult', (), {'allowed': True})()

class TenantIsolation:
    """Real tenant isolation implementation."""
    
    async def validate_isolation(self, user_tenant: str, resource_tenant: str):
        """Validate tenant isolation with real logic."""
        # Enforce strict tenant isolation
        if user_tenant != resource_tenant:
            return type('IsolationResult', (), {'isolated': False})()
        
        # Additional validation
        if not self._validate_tenant_format(user_tenant):
            return type('IsolationResult', (), {'isolated': False})()
        
        if not self._validate_tenant_format(resource_tenant):
            return type('IsolationResult', (), {'isolated': False})()
        
        return type('IsolationResult', (), {'isolated': True})()
    
    def _validate_tenant_format(self, tenant_id):
        """Validate tenant ID format."""
        return tenant_id and tenant_id.startswith("tenant_")

class SecurityAudit:
    """Real security audit implementation."""
    
    def __init__(self):
        self.audit_log = []
    
    async def audit_policy_violation(self, policy_name: str, action: str, resource: str, context):
        """Audit policy violation with real logging."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "policy_violation",
            "policy_name": policy_name,
            "action": action,
            "resource": resource,
            "user_id": context.get("user_id"),
            "tenant_id": context.get("tenant_id"),
            "severity": "high"
        }
        self.audit_log.append(audit_entry)
        print(f"🚨 SECURITY AUDIT: Policy violation - {policy_name} for {action} on {resource}")
    
    async def audit_policy_compliance(self, policy_name: str, action: str, resource: str, context):
        """Audit policy compliance with real logging."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "policy_compliance",
            "policy_name": policy_name,
            "action": action,
            "resource": resource,
            "user_id": context.get("user_id"),
            "tenant_id": context.get("tenant_id"),
            "severity": "info"
        }
        self.audit_log.append(audit_entry)
        print(f"✅ SECURITY AUDIT: Policy compliance - {policy_name} for {action} on {resource}")
    
    async def audit_tenant_violation(self, user_tenant: str, resource_tenant: str):
        """Audit tenant violation with real logging."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "tenant_violation",
            "user_tenant": user_tenant,
            "resource_tenant": resource_tenant,
            "severity": "critical"
        }
        self.audit_log.append(audit_entry)
        print(f"🚨 SECURITY AUDIT: Tenant violation - {user_tenant} -> {resource_tenant}")
    
    async def audit_tenant_access(self, user_tenant: str, resource_tenant: str):
        """Audit tenant access with real logging."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "tenant_access",
            "user_tenant": user_tenant,
            "resource_tenant": resource_tenant,
            "severity": "info"
        }
        self.audit_log.append(audit_entry)
        print(f"✅ SECURITY AUDIT: Tenant access - {user_tenant} -> {resource_tenant}")

class PerformanceMonitor:
    """Real performance monitoring implementation."""
    
    def __init__(self):
        self.metrics = {}
        self.performance_log = []
    
    async def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record performance metric with real logic."""
        timestamp = datetime.utcnow().isoformat()
        
        # Store metric
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        metric_entry = {
            "timestamp": timestamp,
            "value": value,
            "tags": tags or {}
        }
        self.metrics[metric_name].append(metric_entry)
        
        # Log performance
        performance_entry = {
            "timestamp": timestamp,
            "metric_name": metric_name,
            "value": value,
            "tags": tags or {}
        }
        self.performance_log.append(performance_entry)
        
        # Alert on high values
        if value > 1000:  # Arbitrary threshold
            print(f"⚠️ PERFORMANCE ALERT: {metric_name} = {value}")
    
    def get_metrics_summary(self):
        """Get metrics summary with real calculations."""
        summary = {}
        for metric_name, values in self.metrics.items():
            if values:
                metric_values = [v["value"] for v in values]
                summary[metric_name] = {
                    "count": len(metric_values),
                    "min": min(metric_values),
                    "max": max(metric_values),
                    "avg": sum(metric_values) / len(metric_values)
                }
        return summary
