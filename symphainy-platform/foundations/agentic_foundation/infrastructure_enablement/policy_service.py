"""
Policy Service - Agent-specific policy enforcement business logic

Handles agent-specific policy enforcement, compliance monitoring,
and policy application to LLM, MCP, and Tool operations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.policy_protocol import (
    PolicyContext, PolicyResult, PolicyDecision, PolicyType
)
from foundations.public_works_foundation.infrastructure_abstractions.policy_abstraction import PolicyAbstraction
from foundations.public_works_foundation.composition_services.policy_composition_service import PolicyCompositionService

# Import utility mixins (minimal - AgenticFoundationService wraps calls)
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class PolicyService(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Policy Service - Agent-specific policy enforcement business logic
    
    Handles agent-specific policy enforcement and compliance monitoring.
    This service applies policies to agent operations and behaviors.
    """
    
    def __init__(self, 
                 policy_abstraction: PolicyAbstraction,
                 policy_composition_service: PolicyCompositionService,
                 curator_foundation=None,
                 di_container=None):
        """Initialize Policy Service."""
        if not di_container:
            raise ValueError("DI Container is required for PolicyService initialization")
        
        # Initialize utility mixins (minimal - AgenticFoundationService wraps calls)
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.policy_abstraction = policy_abstraction
        self.policy_composition_service = policy_composition_service
        self.curator_foundation = curator_foundation
        self.service_name = "policy_service"
        
        # Agent-specific policy enforcement
        self.agent_policy_enforcement = {
            "llm_operations": self._enforce_llm_policies,
            "mcp_operations": self._enforce_mcp_policies,
            "tool_operations": self._enforce_tool_policies,
            "agent_behavior": self._enforce_agent_behavior_policies
        }
        
        self.logger.info("Initialized Policy Service for agent-specific enforcement")
    
    async def enforce_agent_policies(self, 
                                   operation_type: str,
                                   context: PolicyContext,
                                   operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce policies for agent operations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("enforce_agent_policies_start", success=True, details={"operation_type": operation_type})
            
            self.logger.debug(f"Enforcing policies for {operation_type} operation")
            
            # Get enforcement function
            enforcement_func = self.agent_policy_enforcement.get(operation_type)
            if not enforcement_func:
                await self.record_health_metric("enforce_agent_policies_unknown_operation", 1.0, {"operation_type": operation_type})
                await self.log_operation_with_telemetry("enforce_agent_policies_complete", success=False)
                return {
                    "success": False,
                    "error": f"Unknown operation type: {operation_type}",
                    "operation_type": operation_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Enforce policies
            result = await enforcement_func(context, operation_data)
            
            # Add service metadata
            result.update({
                "operation_type": operation_type,
                "enforced_at": datetime.utcnow().isoformat(),
                "policy_service": self.service_name
            })
            
            # Record success metric
            await self.record_health_metric("enforce_agent_policies_success", 1.0, {"operation_type": operation_type, "success": result.get("success", False)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("enforce_agent_policies_complete", success=True, details={"operation_type": operation_type})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "enforce_agent_policies", details={"operation_type": operation_type})
            self.logger.error(f"Policy enforcement failed for {operation_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation_type": operation_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_agent_compliance(self, 
                                   agent_id: str,
                                   context: PolicyContext,
                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check agent compliance with all applicable policies."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("check_agent_compliance_start", success=True, details={"agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_compliance", "read"):
                        await self.record_health_metric("check_agent_compliance_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("check_agent_compliance_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("check_agent_compliance_tenant_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("check_agent_compliance_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Checking compliance for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = PolicyContext(
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                agent_id=agent_id,
                resource=context.resource,
                action=context.action,
                environment=context.environment,
                metadata=context.metadata or {}
            )
            
            # Evaluate agent behavior policies
            behavior_result = await self.policy_composition_service.orchestrate_policy_evaluation(
                "agent_governance",
                agent_context
            )
            
            # Check compliance status
            is_compliant = behavior_result.get("success", False) and \
                          behavior_result.get("final_decision") != "deny"
            
            result = {
                "success": True,
                "agent_id": agent_id,
                "is_compliant": is_compliant,
                "compliance_result": behavior_result,
                "checked_at": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("check_agent_compliance_success", 1.0, {"agent_id": agent_id, "is_compliant": is_compliant})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("check_agent_compliance_complete", success=True, details={"agent_id": agent_id, "is_compliant": is_compliant})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "check_agent_compliance", details={"agent_id": agent_id})
            self.logger.error(f"Compliance check failed for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_agent_policy_recommendations(self, 
                                             agent_id: str,
                                             context: PolicyContext) -> Dict[str, Any]:
        """Get policy recommendations for an agent."""
        try:
            self.logger.debug(f"Getting policy recommendations for agent {agent_id}")
            
            # Get available policies
            all_policies = await self.policy_abstraction.list_policies()
            
            # Filter policies relevant to agents
            agent_policies = [
                policy for policy in all_policies
                if policy.get("definition", {}).get("type") == "agent_behavior"
            ]
            
            # Get policy metrics
            metrics = await self.policy_composition_service.get_policy_metrics()
            
            return {
                "success": True,
                "agent_id": agent_id,
                "recommended_policies": agent_policies,
                "policy_metrics": metrics,
                "recommendations_generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get policy recommendations for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check policy service health."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("health_check_start", success=True)
            
            self.logger.debug("Checking policy service health")
            
            # Check underlying services
            abstraction_health = await self.policy_abstraction.health_check()
            composition_health = await self.policy_composition_service.health_check()
            
            result = {
                "status": "healthy" if all(
                    h.get("status") == "healthy" 
                    for h in [abstraction_health, composition_health]
                ) else "unhealthy",
                "service": self.service_name,
                "abstraction_health": abstraction_health,
                "composition_health": composition_health,
                "enforcement_types": list(self.agent_policy_enforcement.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("health_check_success", 1.0, {"status": result["status"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("health_check_complete", success=True, details={"status": result["status"]})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "health_check")
            self.logger.error(f"Policy service health check failed: {e}")
            return {
                "status": "error",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # AGENT-SPECIFIC POLICY ENFORCEMENT
    # ============================================================================
    
    async def _enforce_llm_policies(self, 
                                  context: PolicyContext, 
                                  operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce policies for LLM operations."""
        try:
            # Get LLM-specific policies
            llm_policies = ["agent_behavior_basic"]  # Default policies
            
            # Evaluate policies
            result = await self.policy_composition_service.orchestrate_policy_evaluation(
                "agent_governance",
                context,
                llm_policies
            )
            
            # Check if LLM operation is allowed
            is_allowed = result.get("success", False) and \
                        result.get("final_decision") != "deny"
            
            return {
                "success": True,
                "operation_allowed": is_allowed,
                "policy_result": result,
                "enforcement_type": "llm_operations"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "enforcement_type": "llm_operations"
            }
    
    async def _enforce_mcp_policies(self, 
                                  context: PolicyContext, 
                                  operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce policies for MCP operations."""
        try:
            # Get MCP-specific policies
            mcp_policies = ["access_control_basic", "agent_behavior_basic"]
            
            # Evaluate policies
            result = await self.policy_composition_service.orchestrate_policy_evaluation(
                "access_control",
                context,
                mcp_policies
            )
            
            # Check if MCP operation is allowed
            is_allowed = result.get("success", False) and \
                        result.get("final_decision") != "deny"
            
            return {
                "success": True,
                "operation_allowed": is_allowed,
                "policy_result": result,
                "enforcement_type": "mcp_operations"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "enforcement_type": "mcp_operations"
            }
    
    async def _enforce_tool_policies(self, 
                                   context: PolicyContext, 
                                   operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce policies for Tool operations."""
        try:
            # Get tool-specific policies
            tool_policies = ["resource_limits_basic", "agent_behavior_basic"]
            
            # Evaluate policies
            result = await self.policy_composition_service.orchestrate_policy_evaluation(
                "resource_governance",
                context,
                tool_policies
            )
            
            # Check if tool operation is allowed
            is_allowed = result.get("success", False) and \
                        result.get("final_decision") != "deny"
            
            return {
                "success": True,
                "operation_allowed": is_allowed,
                "policy_result": result,
                "enforcement_type": "tool_operations"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "enforcement_type": "tool_operations"
            }
    
    async def _enforce_agent_behavior_policies(self, 
                                             context: PolicyContext, 
                                             operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce policies for general agent behavior."""
        try:
            # Get agent behavior policies
            behavior_policies = ["agent_behavior_basic"]
            
            # Evaluate policies
            result = await self.policy_composition_service.orchestrate_policy_evaluation(
                "agent_governance",
                context,
                behavior_policies
            )
            
            # Check if agent behavior is allowed
            is_allowed = result.get("success", False) and \
                        result.get("final_decision") != "deny"
            
            return {
                "success": True,
                "operation_allowed": is_allowed,
                "policy_result": result,
                "enforcement_type": "agent_behavior"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "enforcement_type": "agent_behavior"
            }

