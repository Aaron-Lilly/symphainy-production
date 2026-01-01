#!/usr/bin/env python3
"""
City Manager Service

The Smart City Governance Hub that manages policies, resources, governance
enforcement, strategic coordination, city health, and emergency response with multi-tenant awareness.

WHAT (Service Role): I govern and coordinate all Smart City roles and dimensions with tenant awareness
HOW (Service Implementation): I provide tenant-aware policy management, SLA enforcement, and cross-role coordination
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from config.environment_loader import EnvironmentLoader
from config import Environment
from utilities import UserContext

# Import infrastructure abstractions
from foundations.infrastructure_foundation.abstractions.policy_management_abstraction import PolicyManagementAbstraction

# Import micro-modules
from .micro_modules.policy_management import PolicyManagementModule
from .micro_modules.resource_allocation import ResourceAllocationModule
from .micro_modules.governance_enforcement import GovernanceEnforcementModule
from .micro_modules.strategic_coordination import StrategicCoordinationModule
from .micro_modules.city_health_monitoring import CityHealthMonitoringModule
from .micro_modules.emergency_coordination import EmergencyCoordinationModule


class CityManagerService(SOAServiceBase):
    """
    City Manager Service - Multi-Tenant Smart City Governance Hub
    
    The Smart City Governance Hub that provides comprehensive governance,
    coordination, and management capabilities across all city roles and dimensions
    with proper tenant isolation and security integration.
    """
    
    def __init__(self, utility_foundation, curator_foundation=None, 
                 public_works_foundation=None, environment: Optional[Environment] = None):
        """Initialize City Manager Service with multi-tenant capabilities."""
        super().__init__("CityManagerService", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.environment = environment or Environment.DEVELOPMENT
        
        # Initialize environment loader
        self.env_loader = EnvironmentLoader(environment)
        self.config = self.env_loader.get_all_config()
        self.api_config = self.env_loader.get_api_config()
        self.feature_flags = self.env_loader.get_feature_flags()
        
        # Initialize SOA protocol
        self.soa_protocol = CityManagerSOAProtocol("CityManagerService", self, curator_foundation), public_works_foundation
        self.city_manager_config = self.env_loader.get_city_manager_config()
        
        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # Initialize infrastructure abstractions
        self.policy_abstraction = PolicyManagementAbstraction(
            policy_storage_type=self.city_manager_config.get("policy_storage_type", "arangodb"),
            policy_collection=self.city_manager_config.get("policy_storage_collection", "city_policies"),
            policy_cache_ttl_seconds=self.city_manager_config.get("policy_cache_ttl_seconds", 3600),
            validation_enabled=self.city_manager_config.get("policy_validation_enabled", True),
            enforcement_enabled=self.city_manager_config.get("policy_enforcement_enabled", True)
        )
        
        # Initialize micro-modules with tenant awareness
        self._initialize_tenant_aware_modules()
        
        # Service capabilities
        self.capabilities = [
            "policy_management",
            "resource_allocation", 
            "governance_enforcement",
            "strategic_coordination",
            "city_health_monitoring",
            "emergency_coordination",
            "multi_tenant_governance"
        ]
        
        self.logger.info("🏛️ City Manager Service initialized - Multi-Tenant Smart City Governance Hub")
    
    def _initialize_tenant_aware_modules(self):
        """Initialize micro-modules with tenant awareness."""
        self.policy_management = PolicyManagementModule(self.logger, self.env_loader, self.policy_abstraction)
        self.resource_allocation = ResourceAllocationModule(self.logger, self.env_loader)
        self.governance_enforcement = GovernanceEnforcementModule(self.logger, self.env_loader)
        self.strategic_coordination = StrategicCoordinationModule(self.logger, self.env_loader)
        self.city_health_monitoring = CityHealthMonitoringModule(self.logger, self.env_loader)
        self.emergency_coordination = EmergencyCoordinationModule(self.logger, self.env_loader)
    
    async def initialize(self):
        """Initialize City Manager Service with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")
            
            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions from public works
            if self.public_works_foundation:
                await self.soa_protocol.load_smart_city_abstractions()
            self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions")
            
            self.logger.info("✅ City Manager Service initialized with multi-tenant capabilities")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="city_manager_initialize")
            raise
    
    # ============================================================================
    # POLICY MANAGEMENT OPERATIONS
    # ============================================================================
    
    async def create_city_policy(self, policy_definition: Dict[str, Any], 
                               user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Create a new city-wide policy with tenant awareness."""
        try:
            # Validate tenant access
            if user_context and self.multi_tenant_coordinator:
                tenant_validation = await self.multi_tenant_coordinator.validate_tenant_feature_access(
                    user_context.tenant_id, "policy_management"
                )
                if not tenant_validation.get("allowed", False):
                    return {"success": False, "error": "Insufficient tenant permissions for policy management"}
            
            # Add tenant context to policy
            if user_context and user_context.tenant_id:
                policy_definition["tenant_id"] = user_context.tenant_id
                policy_definition["created_by"] = user_context.user_id
            
            # Create policy with tenant awareness
            result = await self.policy_management.create_policy(policy_definition)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "create_city_policy", "policy_management", 
                    {"policy_id": result.get("policy_id")}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="create_city_policy")
            return {"success": False, "error": str(e)}
    
    async def update_city_policy(self, policy_id: str, updates: Dict[str, Any], 
                               user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Update an existing city policy with tenant awareness."""
        try:
            # Get policy to check tenant access
            policy = await self.policy_management.get_policy(policy_id)
            if not policy:
                return {"success": False, "error": "Policy not found"}
            
            # Check tenant access to policy
            if user_context and user_context.tenant_id:
                if policy.get("tenant_id") and policy["tenant_id"] != user_context.tenant_id:
                    return {"success": False, "error": "Access denied: Policy belongs to different tenant"}
            
            # Update policy
            result = await self.policy_management.update_policy(policy_id, updates)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "update_city_policy", "policy_management",
                    {"policy_id": policy_id}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="update_city_policy")
            return {"success": False, "error": str(e)}
    
    async def delete_city_policy(self, policy_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Delete a city policy with tenant awareness."""
        try:
            # Get policy to check tenant access
            policy = await self.policy_management.get_policy(policy_id)
            if not policy:
                return {"success": False, "error": "Policy not found"}
            
            # Check tenant access to policy
            if user_context and user_context.tenant_id:
                if policy.get("tenant_id") and policy["tenant_id"] != user_context.tenant_id:
                    return {"success": False, "error": "Access denied: Policy belongs to different tenant"}
            
            # Delete policy
            result = await self.policy_management.delete_policy(policy_id)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "delete_city_policy", "policy_management",
                    {"policy_id": policy_id}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="delete_city_policy")
            return {"success": False, "error": str(e)}
    
    async def enforce_city_policy(self, policy_id: str, context: Dict[str, Any], 
                                user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Enforce a city policy against a context with tenant awareness."""
        try:
            # Get policy with tenant validation
            policy = await self.policy_management.get_policy(policy_id)
            if not policy:
                return {"success": False, "error": "Policy not found"}
            
            # Check tenant access to policy
            if user_context and user_context.tenant_id:
                if policy.get("tenant_id") and policy["tenant_id"] != user_context.tenant_id:
                    return {"success": False, "error": "Access denied: Policy belongs to different tenant"}
            
            # Add tenant context to enforcement context
            if user_context and user_context.tenant_id:
                context["tenant_id"] = user_context.tenant_id
                context["user_id"] = user_context.user_id
            
            # Enforce policy
            result = await self.policy_management.enforce_policy(policy_id, context)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "enforce_city_policy", "policy_management",
                    {"policy_id": policy_id, "enforcement_result": result.get("success")}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="enforce_city_policy")
            return {"success": False, "error": str(e)}
    
    async def list_city_policies(self, filter_criteria: Optional[Dict[str, Any]] = None, 
                               user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """List all city policies with tenant awareness."""
        try:
            # Add tenant filter if user context provided
            if user_context and user_context.tenant_id:
                if not filter_criteria:
                    filter_criteria = {}
                filter_criteria["tenant_id"] = user_context.tenant_id
            
            result = await self.policy_management.list_policies(filter_criteria)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "list_city_policies", "policy_management",
                    {"policy_count": len(result.get("policies", []))}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="list_city_policies")
            return {"success": False, "error": str(e)}
    
    async def get_policy_status(self, policy_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get status of a specific policy with tenant awareness."""
        try:
            # Get policy to check tenant access
            policy = await self.policy_management.get_policy(policy_id)
            if not policy:
                return {"success": False, "error": "Policy not found"}
            
            # Check tenant access to policy
            if user_context and user_context.tenant_id:
                if policy.get("tenant_id") and policy["tenant_id"] != user_context.tenant_id:
                    return {"success": False, "error": "Access denied: Policy belongs to different tenant"}
            
            result = await self.policy_management.get_policy_status(policy_id)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_policy_status", "policy_management",
                    {"policy_id": policy_id}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_policy_status")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # RESOURCE ALLOCATION OPERATIONS
    # ============================================================================
    
    async def allocate_city_resources(self, allocation_request: Dict[str, Any], 
                                    user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Allocate resources for city operations with tenant awareness."""
        try:
            # Validate tenant access and limits
            if user_context and self.multi_tenant_coordinator:
                # Check tenant resource limits
                tenant_limits = await self.multi_tenant_coordinator.get_tenant_limits(user_context.tenant_id)
                requested_resources = allocation_request.get("resources", {})
                
                # Validate against tenant limits
                for resource_type, amount in requested_resources.items():
                    if amount > tenant_limits.get(f"max_{resource_type}", float('inf')):
                        return {"success": False, "error": f"Resource allocation exceeds tenant limits for {resource_type}"}
            
            # Add tenant context to allocation
            if user_context and user_context.tenant_id:
                allocation_request["tenant_id"] = user_context.tenant_id
                allocation_request["allocated_by"] = user_context.user_id
            
            # Allocate resources
            result = await self.resource_allocation.allocate_resources(allocation_request)
            
            # Record telemetry
            await self.telemetry_service.record_metric(
                "resource_allocation_count", 1,
                {"tenant_id": user_context.tenant_id if user_context else "system"}
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "allocate_city_resources", "resource_management",
                    {"allocation_id": result.get("allocation_id")}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="allocate_city_resources")
            return {"success": False, "error": str(e)}
    
    async def deallocate_city_resources(self, allocation_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Deallocate previously allocated resources with tenant awareness."""
        try:
            # Get allocation to check tenant access
            allocation = await self.resource_allocation.get_allocation(allocation_id)
            if not allocation:
                return {"success": False, "error": "Allocation not found"}
            
            # Check tenant access to allocation
            if user_context and user_context.tenant_id:
                if allocation.get("tenant_id") and allocation["tenant_id"] != user_context.tenant_id:
                    return {"success": False, "error": "Access denied: Allocation belongs to different tenant"}
            
            # Deallocate resources
            result = await self.resource_allocation.deallocate_resources(allocation_id)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "deallocate_city_resources", "resource_management",
                    {"allocation_id": allocation_id}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="deallocate_city_resources")
            return {"success": False, "error": str(e)}
    
    async def get_city_budget_status(self, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get current city budget status with tenant awareness."""
        try:
            # Get budget status
            result = await self.resource_allocation.get_budget_status()
            
            # Filter by tenant if user context provided
            if user_context and user_context.tenant_id:
                # Add tenant-specific budget information
                tenant_allocations = await self.resource_allocation.list_allocations(
                    {"tenant_id": user_context.tenant_id}
                )
                tenant_budget = sum(
                    alloc.get("amount", 0) for alloc in tenant_allocations.get("allocations", [])
                )
                result["tenant_budget"] = tenant_budget
                result["tenant_id"] = user_context.tenant_id
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_city_budget_status", "resource_management",
                    {"tenant_id": user_context.tenant_id}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_city_budget_status")
            return {"success": False, "error": str(e)}
    
    async def update_city_budget(self, new_budget: float, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Update total city budget with tenant awareness."""
        try:
            # Validate tenant access for budget updates
            if user_context and self.multi_tenant_coordinator:
                tenant_validation = await self.multi_tenant_coordinator.validate_tenant_feature_access(
                    user_context.tenant_id, "budget_management"
                )
                if not tenant_validation.get("allowed", False):
                    return {"success": False, "error": "Insufficient tenant permissions for budget management"}
            
            # Update budget
            result = await self.resource_allocation.update_budget(new_budget)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "update_city_budget", "resource_management",
                    {"new_budget": new_budget}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="update_city_budget")
            return {"success": False, "error": str(e)}
    
    async def optimize_city_resources(self, optimization_criteria: Dict[str, Any], 
                                    user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Optimize current resource allocations with tenant awareness."""
        try:
            # Add tenant context to optimization criteria
            if user_context and user_context.tenant_id:
                optimization_criteria["tenant_id"] = user_context.tenant_id
            
            # Optimize resources
            result = await self.resource_allocation.optimize_allocations(optimization_criteria)
            
            # Record telemetry
            await self.telemetry_service.record_metric(
                "resource_optimization_count", 1,
                {"tenant_id": user_context.tenant_id if user_context else "system"}
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "optimize_city_resources", "resource_management",
                    {"optimization_criteria": optimization_criteria}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="optimize_city_resources")
            return {"success": False, "error": str(e)}
    
    async def list_resource_allocations(self, filter_criteria: Optional[Dict[str, Any]] = None, 
                                      user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """List all resource allocations with tenant awareness."""
        try:
            # Add tenant filter if user context provided
            if user_context and user_context.tenant_id:
                if not filter_criteria:
                    filter_criteria = {}
                filter_criteria["tenant_id"] = user_context.tenant_id
            
            result = await self.resource_allocation.list_allocations(filter_criteria)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "list_resource_allocations", "resource_management",
                    {"allocation_count": len(result.get("allocations", []))}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="list_resource_allocations")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # GOVERNANCE ENFORCEMENT OPERATIONS
    # ============================================================================
    
    async def check_city_compliance(self, component_id: str, governance_layer: str, 
                                  component_data: Dict[str, Any], 
                                  user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Check compliance for a specific component and governance layer with tenant awareness."""
        try:
            # Add tenant context to component data
            if user_context and user_context.tenant_id:
                component_data["tenant_id"] = user_context.tenant_id
                component_data["checked_by"] = user_context.user_id
            
            # Check compliance
            result = await self.governance_enforcement.check_compliance(
                component_id, governance_layer, component_data
            )
            
            # Record telemetry
            await self.telemetry_service.record_metric(
                "compliance_check_count", 1,
                {
                    "governance_layer": governance_layer,
                    "tenant_id": user_context.tenant_id if user_context else "system",
                    "compliant": result.get("compliant", False)
                }
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "check_city_compliance", "governance_enforcement",
                    {
                        "component_id": component_id,
                        "governance_layer": governance_layer,
                        "compliant": result.get("compliant", False)
                    }
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="check_city_compliance")
            return {"success": False, "error": str(e)}
    
    async def check_multi_layer_compliance(self, component_id: str, component_data: Dict[str, Any], 
                                         user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Check compliance across all governance layers with tenant awareness."""
        try:
            # Add tenant context to component data
            if user_context and user_context.tenant_id:
                component_data["tenant_id"] = user_context.tenant_id
                component_data["checked_by"] = user_context.user_id
            
            # Check multi-layer compliance
            result = await self.governance_enforcement.check_multi_layer_compliance(component_id, component_data)
            
            # Record telemetry
            await self.telemetry_service.record_metric(
                "multi_layer_compliance_check_count", 1,
                {
                    "tenant_id": user_context.tenant_id if user_context else "system",
                    "layers_checked": len(result.get("layer_results", {}))
                }
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "check_multi_layer_compliance", "governance_enforcement",
                    {
                        "component_id": component_id,
                        "layers_checked": len(result.get("layer_results", {}))
                    }
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="check_multi_layer_compliance")
            return {"success": False, "error": str(e)}
    
    async def check_sla_compliance(self, service_id: str, sla_metrics: Dict[str, Any], 
                                 user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Check SLA compliance for a service with tenant awareness."""
        try:
            # Add tenant context to SLA metrics
            if user_context and user_context.tenant_id:
                sla_metrics["tenant_id"] = user_context.tenant_id
                sla_metrics["checked_by"] = user_context.user_id
            
            # Check SLA compliance
            result = await self.governance_enforcement.check_sla_compliance(service_id, sla_metrics)
            
            # Record telemetry
            await self.telemetry_service.record_metric(
                "sla_compliance_check_count", 1,
                {
                    "service_id": service_id,
                    "tenant_id": user_context.tenant_id if user_context else "system",
                    "sla_compliant": result.get("sla_compliant", False)
                }
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "check_sla_compliance", "governance_enforcement",
                    {
                        "service_id": service_id,
                        "sla_compliant": result.get("sla_compliant", False)
                    }
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="check_sla_compliance")
            return {"success": False, "error": str(e)}
    
    async def run_city_governance_audit(self, audit_scope: Optional[List[str]] = None, 
                                      user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Run a comprehensive city governance audit with tenant awareness."""
        try:
            # Add tenant scope to audit if user context provided
            if user_context and user_context.tenant_id:
                if not audit_scope:
                    audit_scope = []
                audit_scope.append(f"tenant:{user_context.tenant_id}")
            
            # Run governance audit
            result = await self.governance_enforcement.run_governance_audit(audit_scope)
            
            # Record telemetry
            await self.telemetry_service.record_metric(
                "governance_audit_count", 1,
                {
                    "tenant_id": user_context.tenant_id if user_context else "system",
                    "audit_scope": len(audit_scope) if audit_scope else 0
                }
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "run_city_governance_audit", "governance_enforcement",
                    {
                        "audit_scope": audit_scope,
                        "violations_found": len(result.get("violations", []))
                    }
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="run_city_governance_audit")
            return {"success": False, "error": str(e)}
    
    async def get_governance_violations(self, filter_criteria: Optional[Dict[str, Any]] = None, 
                                      user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get governance violations with tenant awareness."""
        try:
            # Add tenant filter if user context provided
            if user_context and user_context.tenant_id:
                if not filter_criteria:
                    filter_criteria = {}
                filter_criteria["tenant_id"] = user_context.tenant_id
            
            result = await self.governance_enforcement.get_violations(filter_criteria)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_governance_violations", "governance_enforcement",
                    {"violation_count": len(result.get("violations", []))}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_governance_violations")
            return {"success": False, "error": str(e)}
    
    async def resolve_governance_violation(self, violation_id: str, resolution_data: Dict[str, Any], 
                                         user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Resolve a governance violation with tenant awareness."""
        try:
            # Get violation to check tenant access
            violation = await self.governance_enforcement.get_violation(violation_id)
            if not violation:
                return {"success": False, "error": "Violation not found"}
            
            # Check tenant access to violation
            if user_context and user_context.tenant_id:
                if violation.get("tenant_id") and violation["tenant_id"] != user_context.tenant_id:
                    return {"success": False, "error": "Access denied: Violation belongs to different tenant"}
            
            # Add tenant context to resolution data
            if user_context and user_context.tenant_id:
                resolution_data["tenant_id"] = user_context.tenant_id
                resolution_data["resolved_by"] = user_context.user_id
            
            # Resolve violation
            result = await self.governance_enforcement.resolve_violation(violation_id, resolution_data)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "resolve_governance_violation", "governance_enforcement",
                    {
                        "violation_id": violation_id,
                        "resolution_successful": result.get("success", False)
                    }
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="resolve_governance_violation")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # STRATEGIC COORDINATION OPERATIONS
    # ============================================================================
    
    async def create_coordination_plan(self, business_operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a strategic coordination plan."""
        return await self.strategic_coordination.create_coordination_plan(business_operation, parameters)
    
    async def execute_coordination_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute a coordination plan."""
        return await self.strategic_coordination.execute_coordination_plan(plan_id)
    
    async def coordinate_city_roles(self, coordination_request: Dict[str, Any], 
                                  user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Coordinate operations between multiple city roles with tenant awareness."""
        try:
            # Validate tenant access to coordination
            if user_context and self.multi_tenant_coordinator:
                tenant_validation = await self.multi_tenant_coordinator.validate_tenant_feature_access(
                    user_context.tenant_id, "role_coordination"
                )
                if not tenant_validation.get("allowed", False):
                    return {"success": False, "error": "Insufficient tenant permissions for role coordination"}
            
            # Add tenant context to coordination request
            if user_context and user_context.tenant_id:
                coordination_request["tenant_id"] = user_context.tenant_id
                coordination_request["coordinated_by"] = user_context.user_id
            
            # Coordinate roles
            result = await self.strategic_coordination.coordinate_roles(coordination_request)
            
            # Record telemetry
            await self.telemetry_service.record_metric(
                "role_coordination_count", 1,
                {
                    "roles_involved": len(coordination_request.get("roles", [])),
                    "tenant_id": user_context.tenant_id if user_context else "system"
                }
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "coordinate_city_roles", "strategic_coordination",
                    {"coordination_id": result.get("coordination_id")}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="coordinate_city_roles")
            return {"success": False, "error": str(e)}
    
    async def facilitate_role_communication(self, communication_request: Dict[str, Any]) -> Dict[str, Any]:
        """Facilitate communication between city roles."""
        return await self.strategic_coordination.facilitate_role_communication(communication_request)
    
    async def orchestrate_city_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a city-wide workflow."""
        return await self.strategic_coordination.orchestrate_workflow(workflow_definition)
    
    async def sync_city_state(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize city-wide state across all roles."""
        return await self.strategic_coordination.sync_city_state(state_data)
    
    async def get_city_state_summary(self) -> Dict[str, Any]:
        """Get summary of current city state."""
        return await self.strategic_coordination.get_city_state_summary()
    
    # ============================================================================
    # CITY HEALTH MONITORING OPERATIONS
    # ============================================================================
    
    async def check_city_health(self) -> Dict[str, Any]:
        """Check overall city health status."""
        return await self.city_health_monitoring.check_city_health()
    
    async def get_city_health_status(self) -> Dict[str, Any]:
        """Get current city health status."""
        return await self.city_health_monitoring.get_city_health_status()
    
    async def monitor_service_health(self, service_id: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor health of a specific service."""
        return await self.city_health_monitoring.monitor_service_health(service_id, service_data)
    
    async def get_health_alerts(self, filter_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get city health alerts."""
        return await self.city_health_monitoring.get_health_alerts(filter_criteria)
    
    async def resolve_health_alert(self, alert_id: str, resolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a health alert."""
        return await self.city_health_monitoring.resolve_health_alert(alert_id, resolution_data)
    
    # ============================================================================
    # EMERGENCY COORDINATION OPERATIONS
    # ============================================================================
    
    async def detect_emergency(self, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect and initiate emergency response."""
        return await self.emergency_coordination.detect_emergency(emergency_data)
    
    async def initiate_emergency_response(self, emergency_id: str) -> Dict[str, Any]:
        """Initiate emergency response for a detected emergency."""
        return await self.emergency_coordination.initiate_emergency_response(emergency_id)
    
    async def escalate_emergency(self, emergency_id: str, escalation_reason: str) -> Dict[str, Any]:
        """Escalate an emergency to the next level."""
        return await self.emergency_coordination.escalate_emergency(emergency_id, escalation_reason)
    
    async def coordinate_emergency_response(self, emergency_id: str, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate emergency response across city roles."""
        return await self.emergency_coordination.coordinate_emergency_response(emergency_id, coordination_request)
    
    async def send_emergency_notification(self, emergency_id: str, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send emergency notification to relevant parties."""
        return await self.emergency_coordination.send_emergency_notification(emergency_id, notification_data)
    
    async def resolve_emergency(self, emergency_id: str, resolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve an emergency."""
        return await self.emergency_coordination.resolve_emergency(emergency_id, resolution_data)
    
    async def get_active_emergencies(self) -> Dict[str, Any]:
        """Get all active emergencies."""
        return await self.emergency_coordination.get_active_emergencies()
    
    # ============================================================================
    # COMPREHENSIVE CITY MANAGEMENT OPERATIONS
    # ============================================================================
    
    async def get_city_overview(self) -> Dict[str, Any]:
        """Get comprehensive city overview."""
        try:
            # Get health status
            health_status = await self.city_health_monitoring.get_city_health_status()
            
            # Get active emergencies
            active_emergencies = await self.emergency_coordination.get_active_emergencies()
            
            # Get governance metrics
            governance_metrics = await self.governance_enforcement.get_governance_metrics()
            
            # Get resource allocation metrics
            resource_metrics = await self.resource_allocation.get_allocation_metrics()
            
            # Get coordination metrics
            coordination_metrics = await self.strategic_coordination.get_coordination_metrics()
            
            # Get policy metrics
            policy_metrics = await self.policy_management.get_policy_metrics()
            
            return {
                "success": True,
                "city_overview": {
                    "health_status": health_status.get("city_health", {}),
                    "active_emergencies": active_emergencies.get("count", 0),
                    "governance_metrics": governance_metrics.get("metrics", {}),
                    "resource_metrics": resource_metrics.get("metrics", {}),
                    "coordination_metrics": coordination_metrics.get("metrics", {}),
                    "policy_metrics": policy_metrics.get("metrics", {})
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get city overview: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_city_maintenance(self) -> Dict[str, Any]:
        """Run comprehensive city maintenance."""
        try:
            maintenance_results = {}
            
            # Check city health
            health_result = await self.city_health_monitoring.check_city_health()
            maintenance_results["health_check"] = health_result
            
            # Run governance audit
            audit_result = await self.governance_enforcement.run_governance_audit()
            maintenance_results["governance_audit"] = audit_result
            
            # Optimize resources
            optimization_result = await self.resource_allocation.optimize_allocations({})
            maintenance_results["resource_optimization"] = optimization_result
            
            # Sync city state
            state_sync_result = await self.strategic_coordination.sync_city_state({})
            maintenance_results["state_sync"] = state_sync_result
            
            self.logger.info("✅ City maintenance completed")
            
            return {
                "success": True,
                "maintenance_results": maintenance_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to run city maintenance: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ============================================================================
    # SERVICE METADATA AND CAPABILITIES
    # ============================================================================
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get City Manager service information."""
        return {
            "service_name": "City Manager",
            "service_type": "Smart City Governance Hub",
            "version": "1.0.0",
            "capabilities": self.capabilities,
            "micro_modules": [
                "policy_management",
                "resource_allocation",
                "governance_enforcement", 
                "strategic_coordination",
                "city_health_monitoring",
                "emergency_coordination"
            ],
            "description": "Comprehensive governance and coordination service for Smart City operations",
            "status": "active"
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of service capabilities."""
        return self.capabilities
    
    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        try:
            # Basic health check - in production, this would be more comprehensive
            return (
                self.policy_management is not None and
                self.resource_allocation is not None and
                self.governance_enforcement is not None and
                self.strategic_coordination is not None and
                self.city_health_monitoring is not None and
                self.emergency_coordination is not None
            )
        except Exception:
            return False
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC METHODS
    # ============================================================================
    
    async def get_tenant_policies(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get all policies for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's policies"}
            
            # Get tenant-specific policies
            filter_criteria = {"tenant_id": tenant_id}
            result = await self.policy_management.list_policies(filter_criteria)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_policies", "policy_management",
                    {"tenant_id": tenant_id, "policy_count": len(result.get("policies", []))}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_policies")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_resource_usage(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get resource usage for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's resource usage"}
            
            # Get tenant-specific resource allocations
            filter_criteria = {"tenant_id": tenant_id}
            result = await self.resource_allocation.list_allocations(filter_criteria)
            
            # Calculate usage metrics
            usage_metrics = {
                "total_allocated": sum(alloc.get("amount", 0) for alloc in result.get("allocations", [])),
                "active_allocations": len([alloc for alloc in result.get("allocations", []) if alloc.get("status") == "active"]),
                "tenant_id": tenant_id
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_resource_usage", "resource_management",
                    {"tenant_id": tenant_id, "total_allocated": usage_metrics["total_allocated"]}
                )
            
            return {"success": True, "usage_metrics": usage_metrics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_resource_usage")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_governance_summary(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get governance summary for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's governance summary"}
            
            # Get tenant-specific governance data
            filter_criteria = {"tenant_id": tenant_id}
            violations = await self.governance_enforcement.get_violations(filter_criteria)
            policies = await self.policy_management.list_policies(filter_criteria)
            
            # Calculate governance metrics
            governance_summary = {
                "tenant_id": tenant_id,
                "total_policies": len(policies.get("policies", [])),
                "active_violations": len([v for v in violations.get("violations", []) if v.get("status") == "active"]),
                "resolved_violations": len([v for v in violations.get("violations", []) if v.get("status") == "resolved"]),
                "compliance_score": self._calculate_compliance_score(violations.get("violations", []))
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_governance_summary", "governance_enforcement",
                    {"tenant_id": tenant_id, "compliance_score": governance_summary["compliance_score"]}
                )
            
            return {"success": True, "governance_summary": governance_summary}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_governance_summary")
            return {"success": False, "error": str(e)}
    
    def _calculate_compliance_score(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate compliance score based on violations."""
        if not violations:
            return 100.0
        
        active_violations = [v for v in violations if v.get("status") == "active"]
        total_violations = len(violations)
        active_count = len(active_violations)
        
        if total_violations == 0:
            return 100.0
        
        # Calculate score: 100 - (active_violations / total_violations * 100)
        score = 100.0 - (active_count / total_violations * 100.0)
        return max(0.0, score)


class CityManagerSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for City Manager Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize City Manager SOA Protocol."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="CityManagerService",
            version="1.0.0",
            description="City Manager Service - Multi-tenant smart city governance and coordination",
            interface_name="ICityManager",
            endpoints=self._create_all_endpoints(),
            tags=["governance", "coordination", "multi-tenant", "city-management"],
            contact={"email": "citymanager@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/city-manager", "description": "City Manager Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for City Manager Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # City Manager specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/governance/policies",
                method="GET",
                summary="List Governance Policies",
                description="List all governance policies for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "policies": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Governance", "Policies"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/governance/policies",
                method="POST",
                summary="Create Governance Policy",
                description="Create a new governance policy",
                request_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "rules": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["name", "description", "rules"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "policy_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Governance", "Policies"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/resources/allocations",
                method="GET",
                summary="List Resource Allocations",
                description="List all resource allocations for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "allocations": {"type": "array", "items": {"type": "object"}},
                        "total_allocated": {"type": "number"}
                    }
                }),
                tags=["Resources", "Allocations"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/resources/allocations",
                method="POST",
                summary="Create Resource Allocation",
                description="Create a new resource allocation",
                request_schema={
                    "type": "object",
                    "properties": {
                        "resource_type": {"type": "string"},
                        "amount": {"type": "number"},
                        "priority": {"type": "string"}
                    },
                    "required": ["resource_type", "amount", "priority"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "allocation_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Resources", "Allocations"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/resource-usage",
                method="GET",
                summary="Get Tenant Resource Usage",
                description="Get resource usage metrics for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_allocated": {"type": "number"},
                        "active_allocations": {"type": "integer"}
                    }
                }),
                tags=["Tenant", "Resources"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/governance-summary",
                method="GET",
                summary="Get Tenant Governance Summary",
                description="Get governance summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_policies": {"type": "integer"},
                        "active_violations": {"type": "integer"},
                        "compliance_score": {"type": "number"}
                    }
                }),
                tags=["Tenant", "Governance"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths
