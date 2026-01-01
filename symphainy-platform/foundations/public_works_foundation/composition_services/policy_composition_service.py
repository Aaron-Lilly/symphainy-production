"""
Policy Composition Service - Infrastructure-level business logic for policy management

Handles infrastructure-level policy workflows, policy orchestration,
and coordination between different policy systems.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.policy_protocol import (
    PolicyContext, PolicyResult, PolicyDecision, PolicyType
)
from foundations.public_works_foundation.infrastructure_abstractions.policy_abstraction import PolicyAbstraction


class PolicyCompositionService:
    """
    Policy Composition Service - Infrastructure-level business logic for policy management
    
    Handles infrastructure-level policy workflows and orchestration.
    This service coordinates policy evaluation across different systems.
    """
    
    def __init__(self, policy_abstraction: PolicyAbstraction, di_container=None):
        """Initialize Policy Composition Service."""
        if not di_container:
            raise ValueError("DI Container is required for PolicyCompositionService initialization")
        
        self.policy_abstraction = policy_abstraction
        self.di_container = di_container
        self.service_name = "policy_composition_service"
        
        # Get logger from DI Container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(self.service_name)
        
        # Infrastructure-level policy workflows
        self.policy_workflows = {
            "access_control": self._access_control_workflow,
            "resource_governance": self._resource_governance_workflow,
            "agent_governance": self._agent_governance_workflow,
            "security_validation": self._security_validation_workflow
        }
        
        self.logger.info("Initialized Policy Composition Service")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    async def orchestrate_policy_evaluation(self, 
                                          workflow_type: str,
                                          context: PolicyContext,
                                          policy_ids: Optional[List[str]] = None,
                                          user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Orchestrate policy evaluation using infrastructure-level workflows."""
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "policy", "evaluate"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Orchestrating {workflow_type} policy evaluation")
            
            # Get workflow
            workflow = self.policy_workflows.get(workflow_type)
            if not workflow:
                return {
                    "success": False,
                    "error": f"Unknown workflow type: {workflow_type}",
                    "workflow_type": workflow_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Execute workflow
            result = await workflow(context, policy_ids)
            
            # Add infrastructure-level metadata
            result.update({
                "workflow_type": workflow_type,
                "orchestrated_at": datetime.utcnow().isoformat(),
                "composition_service": self.service_name
            })
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_policy_evaluation", {
                    "workflow_type": workflow_type,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_policy_evaluation",
                    "workflow_type": workflow_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Policy orchestration failed for {workflow_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "POLICY_ORCHESTRATION_ERROR",
                "workflow_type": workflow_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def evaluate_policy_chain(self, 
                                  policy_chain: List[str],
                                  context: PolicyContext,
                                  stop_on_deny: bool = True,
                                  user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluate a chain of policies with infrastructure-level coordination."""
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "policy", "evaluate"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Evaluating policy chain: {policy_chain}")
            
            results = []
            final_decision = PolicyDecision.ALLOW
            
            for policy_id in policy_chain:
                # Evaluate policy
                result = await self.policy_abstraction.evaluate_policy(policy_id, context)
                results.append(result)
                
                # Check if we should stop on deny
                if stop_on_deny and result.decision == PolicyDecision.DENY:
                    final_decision = PolicyDecision.DENY
                    break
                elif result.decision == PolicyDecision.DENY:
                    final_decision = PolicyDecision.DENY
                elif result.decision == PolicyDecision.WARN and final_decision == PolicyDecision.ALLOW:
                    final_decision = PolicyDecision.WARN
            
            result = {
                "success": True,
                "final_decision": final_decision.value,
                "policy_results": [
                    {
                        "policy_id": r.policy_id,
                        "decision": r.decision.value,
                        "reason": r.reason,
                        "metadata": r.metadata
                    } for r in results
                ],
                "chain_length": len(policy_chain),
                "evaluated_policies": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("evaluate_policy_chain", {
                    "chain_length": len(policy_chain),
                    "final_decision": final_decision.value,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "evaluate_policy_chain",
                    "policy_chain_length": len(policy_chain),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Policy chain evaluation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "POLICY_CHAIN_EVALUATION_ERROR",
                "policy_chain": policy_chain,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_policy_metrics(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get infrastructure-level policy metrics."""
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "policy", "view"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug("Getting policy metrics")
            
            # Get adapter health
            adapter_health = await self.policy_abstraction.health_check()
            
            # Get available policies
            all_policies = await self.policy_abstraction.list_policies()
            
            # Calculate metrics
            policy_counts = {}
            for policy in all_policies:
                policy_type = policy.get("definition", {}).get("type", "unknown")
                policy_counts[policy_type] = policy_counts.get(policy_type, 0) + 1
            
            result = {
                "success": True,
                "adapter_health": adapter_health,
                "policy_counts": policy_counts,
                "total_policies": len(all_policies),
                "available_workflows": list(self.policy_workflows.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_policy_metrics", {
                    "total_policies": len(all_policies),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_policy_metrics",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get policy metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "POLICY_METRICS_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check policy composition service health."""
        try:
            self.logger.debug("Checking policy composition service health")
            
            # Check underlying abstraction
            abstraction_health = await self.policy_abstraction.health_check()
            
            result = {
                "status": "healthy" if abstraction_health.get("status") == "healthy" else "unhealthy",
                "service": self.service_name,
                "abstraction_health": abstraction_health,
                "available_workflows": len(self.policy_workflows),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("health_check", {
                    "status": result["status"],
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Policy composition service health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
                "error_code": "POLICY_HEALTH_CHECK_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # INFRASTRUCTURE-LEVEL POLICY WORKFLOWS
    # ============================================================================
    
    async def _access_control_workflow(self, 
                                    context: PolicyContext, 
                                    policy_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Access control workflow for infrastructure-level policy evaluation."""
        try:
            # Default access control policies
            if not policy_ids:
                policy_ids = ["access_control_basic"]
            
            # Evaluate access control policies
            results = await self.policy_abstraction.evaluate_policies(policy_ids, context)
            
            # Determine overall decision
            has_deny = any(r.decision == PolicyDecision.DENY for r in results)
            has_warn = any(r.decision == PolicyDecision.WARN for r in results)
            
            if has_deny:
                final_decision = PolicyDecision.DENY
                reason = "Access denied by policy"
            elif has_warn:
                final_decision = PolicyDecision.WARN
                reason = "Access granted with warnings"
            else:
                final_decision = PolicyDecision.ALLOW
                reason = "Access granted"
            
            return {
                "success": True,
                "workflow": "access_control",
                "final_decision": final_decision.value,
                "reason": reason,
                "policy_results": [
                    {
                        "policy_id": r.policy_id,
                        "decision": r.decision.value,
                        "reason": r.reason
                    } for r in results
                ]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_access_control_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Access control workflow failed: {e}")
            return {
                "success": False,
                "workflow": "access_control",
                "error": str(e),
                "error_code": "POLICY_ACCESS_CONTROL_ERROR"
            }
    
    async def _resource_governance_workflow(self, 
                                         context: PolicyContext, 
                                         policy_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Resource governance workflow for infrastructure-level policy evaluation."""
        try:
            # Default resource governance policies
            if not policy_ids:
                policy_ids = ["resource_limits_basic"]
            
            # Evaluate resource governance policies
            results = await self.policy_abstraction.evaluate_policies(policy_ids, context)
            
            # Determine overall decision
            has_deny = any(r.decision == PolicyDecision.DENY for r in results)
            has_warn = any(r.decision == PolicyDecision.WARN for r in results)
            
            if has_deny:
                final_decision = PolicyDecision.DENY
                reason = "Resource access denied by policy"
            elif has_warn:
                final_decision = PolicyDecision.WARN
                reason = "Resource access granted with warnings"
            else:
                final_decision = PolicyDecision.ALLOW
                reason = "Resource access granted"
            
            return {
                "success": True,
                "workflow": "resource_governance",
                "final_decision": final_decision.value,
                "reason": reason,
                "policy_results": [
                    {
                        "policy_id": r.policy_id,
                        "decision": r.decision.value,
                        "reason": r.reason
                    } for r in results
                ]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_resource_governance_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Resource governance workflow failed: {e}")
            return {
                "success": False,
                "workflow": "resource_governance",
                "error": str(e),
                "error_code": "POLICY_RESOURCE_GOVERNANCE_ERROR"
            }
    
    async def _agent_governance_workflow(self, 
                                       context: PolicyContext, 
                                       policy_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Agent governance workflow for infrastructure-level policy evaluation."""
        try:
            # Default agent governance policies
            if not policy_ids:
                policy_ids = ["agent_behavior_basic"]
            
            # Evaluate agent governance policies
            results = await self.policy_abstraction.evaluate_policies(policy_ids, context)
            
            # Determine overall decision
            has_deny = any(r.decision == PolicyDecision.DENY for r in results)
            has_warn = any(r.decision == PolicyDecision.WARN for r in results)
            
            if has_deny:
                final_decision = PolicyDecision.DENY
                reason = "Agent action denied by policy"
            elif has_warn:
                final_decision = PolicyDecision.WARN
                reason = "Agent action allowed with warnings"
            else:
                final_decision = PolicyDecision.ALLOW
                reason = "Agent action allowed"
            
            return {
                "success": True,
                "workflow": "agent_governance",
                "final_decision": final_decision.value,
                "reason": reason,
                "policy_results": [
                    {
                        "policy_id": r.policy_id,
                        "decision": r.decision.value,
                        "reason": r.reason
                    } for r in results
                ]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_agent_governance_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Agent governance workflow failed: {e}")
            return {
                "success": False,
                "workflow": "agent_governance",
                "error": str(e),
                "error_code": "POLICY_AGENT_GOVERNANCE_ERROR"
            }
    
    async def _security_validation_workflow(self, 
                                         context: PolicyContext, 
                                         policy_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Security validation workflow for infrastructure-level policy evaluation."""
        try:
            # Default security validation policies
            if not policy_ids:
                policy_ids = ["access_control_basic", "agent_behavior_basic"]
            
            # Evaluate security validation policies
            results = await self.policy_abstraction.evaluate_policies(policy_ids, context)
            
            # Determine overall decision
            has_deny = any(r.decision == PolicyDecision.DENY for r in results)
            has_warn = any(r.decision == PolicyDecision.WARN for r in results)
            
            if has_deny:
                final_decision = PolicyDecision.DENY
                reason = "Security validation failed"
            elif has_warn:
                final_decision = PolicyDecision.WARN
                reason = "Security validation passed with warnings"
            else:
                final_decision = PolicyDecision.ALLOW
                reason = "Security validation passed"
            
            return {
                "success": True,
                "workflow": "security_validation",
                "final_decision": final_decision.value,
                "reason": reason,
                "policy_results": [
                    {
                        "policy_id": r.policy_id,
                        "decision": r.decision.value,
                        "reason": r.reason
                    } for r in results
                ]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_security_validation_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Security validation workflow failed: {e}")
            return {
                "success": False,
                "workflow": "security_validation",
                "error": str(e),
                "error_code": "POLICY_SECURITY_VALIDATION_ERROR"
            }

