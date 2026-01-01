"""
OPA Policy Adapter - Raw technology wrapper for Open Policy Agent

Provides direct integration with OPA for policy evaluation.
This is a raw technology adapter that handles OPA-specific concerns.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.policy_protocol import (
    PolicyProtocol, PolicyContext, PolicyResult, PolicyDecision, PolicyType
)


class OPAPolicyAdapter:
    """
    OPA Policy Adapter - Raw technology wrapper for Open Policy Agent
    
    Handles direct OPA integration for policy evaluation.
    This adapter focuses purely on OPA-specific implementation details.
    """
    
    def __init__(self, 
                 opa_url: str = "http://localhost:8181",
                 service_name: str = "opa_policy_adapter",
                 timeout: int = 30,
                 di_container=None):
        """Initialize OPA Policy Adapter."""
        if not di_container:
            raise ValueError("DI Container is required for OPAPolicyAdapter initialization")
        self.opa_url = opa_url
        self.service_name = service_name
        self.timeout = timeout
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        
        # OPA-specific configuration
        self.policy_prefix = "symphainy"
        self.default_policy_set = "platform"
        
        self.logger.info(f"Initialized OPA Policy Adapter: {opa_url}")
    
    async def evaluate_policy(self, 
                            policy_id: str, 
                            context: PolicyContext) -> PolicyResult:
        """Evaluate a specific policy using OPA."""
        try:
            self.logger.debug(f"Evaluating policy {policy_id} with OPA")
            
            # Convert context to OPA input format
            opa_input = self._convert_context_to_opa_input(context)
            
            # Construct OPA query path
            query_path = f"{self.policy_prefix}/{policy_id}"
            
            # Make OPA query
            result = await self._query_opa(query_path, opa_input)
            
            # Convert OPA result to PolicyResult
            policy_result = self._convert_opa_result_to_policy_result(
                result, policy_id, context
            )
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("evaluate_policy", {
                    "policy_id": policy_id,
                    "decision": policy_result.decision.value if hasattr(policy_result.decision, 'value') else str(policy_result.decision),
                    "success": True
                })
            
            return policy_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "evaluate_policy",
                    "policy_id": policy_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to evaluate policy {policy_id}: {e}")
            return PolicyResult(
                decision=PolicyDecision.UNKNOWN,
                policy_id=policy_id,
                policy_name=policy_id,
                reason=f"Policy evaluation failed: {str(e)}",
                metadata={"error": str(e), "adapter": "opa"}
            )
    
    async def evaluate_policies(self, 
                              policy_ids: List[str], 
                              context: PolicyContext) -> List[PolicyResult]:
        """Evaluate multiple policies using OPA."""
        try:
            self.logger.debug(f"Evaluating {len(policy_ids)} policies with OPA")
            
            # Convert context to OPA input format
            opa_input = self._convert_context_to_opa_input(context)
            
            # Evaluate each policy
            results = []
            for policy_id in policy_ids:
                result = await self.evaluate_policy(policy_id, context)
                results.append(result)
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("evaluate_policies", {
                    "policy_count": len(policy_ids),
                    "success": True
                })
            
            return results
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "evaluate_policies",
                    "policy_count": len(policy_ids),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to evaluate policies: {e}")
            return [
                PolicyResult(
                    decision=PolicyDecision.UNKNOWN,
                    policy_id=policy_id,
                    policy_name=policy_id,
                    reason=f"Policy evaluation failed: {str(e)}",
                    metadata={"error": str(e), "adapter": "opa"}
                ) for policy_id in policy_ids
            ]
    
    async def evaluate_policy_set(self, 
                                policy_set: str, 
                                context: PolicyContext) -> List[PolicyResult]:
        """Evaluate all policies in a policy set using OPA."""
        try:
            self.logger.debug(f"Evaluating policy set {policy_set} with OPA")
            
            # Convert context to OPA input format
            opa_input = self._convert_context_to_opa_input(context)
            
            # Query all policies in the set
            query_path = f"{self.policy_prefix}/{policy_set}"
            result = await self._query_opa(query_path, opa_input)
            
            # Convert OPA result to PolicyResult list
            policy_results = self._convert_opa_set_result_to_policy_results(
                result, policy_set, context
            )
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("evaluate_policy_set", {
                    "policy_set": policy_set,
                    "result_count": len(policy_results),
                    "success": True
                })
            
            return policy_results
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "evaluate_policy_set",
                    "policy_set": policy_set,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to evaluate policy set {policy_set}: {e}")
            return [
                PolicyResult(
                    decision=PolicyDecision.UNKNOWN,
                    policy_id=policy_set,
                    policy_name=policy_set,
                    reason=f"Policy set evaluation failed: {str(e)}",
                    metadata={"error": str(e), "adapter": "opa"}
                )
            ]
    
    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy definition from OPA."""
        try:
            self.logger.debug(f"Getting policy {policy_id} from OPA")
            
            # Query OPA for policy definition
            query_path = f"data.{self.policy_prefix}.{policy_id}"
            result = await self._query_opa(query_path, {})
            
            if result and "result" in result:
                policy_def = {
                    "policy_id": policy_id,
                    "definition": result["result"],
                    "adapter": "opa",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("get_policy", {
                        "policy_id": policy_id,
                        "found": True,
                        "success": True
                    })
                
                return policy_def
            
            # Record telemetry for not found
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_policy", {
                    "policy_id": policy_id,
                    "found": False,
                    "success": True
                })
            
            return None
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_policy",
                    "policy_id": policy_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get policy {policy_id}: {e}")
            return None
    
    async def list_policies(self, 
                          policy_type: Optional[PolicyType] = None,
                          tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List available policies from OPA."""
        try:
            self.logger.debug("Listing policies from OPA")
            
            # Query OPA for all policies
            query_path = f"data.{self.policy_prefix}"
            result = await self._query_opa(query_path, {})
            
            if not result or "result" not in result:
                return []
            
            policies = []
            for policy_id, policy_def in result["result"].items():
                if isinstance(policy_def, dict):
                    policy_info = {
                        "policy_id": policy_id,
                        "definition": policy_def,
                        "adapter": "opa",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Apply filters if provided
                    if self._matches_filters(policy_info, policy_type, tags):
                        policies.append(policy_info)
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("list_policies", {
                    "policy_count": len(policies),
                    "success": True
                })
            
            return policies
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "list_policies",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to list policies: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OPA health and availability."""
        try:
            self.logger.debug("Checking OPA health")
            
            # Simple health check query
            result = await self._query_opa("data", {})
            
            health_status = {
                "status": "healthy",
                "adapter": "opa",
                "opa_url": self.opa_url,
                "timestamp": datetime.utcnow().isoformat(),
                "response_time_ms": 0  # Would measure actual response time
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("health_check", {
                    "adapter": "opa",
                    "status": "healthy",
                    "success": True
                })
            
            return health_status
            
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
                self.logger.error(f"OPA health check failed: {e}")
            return {
                "status": "unhealthy",
                "adapter": "opa",
                "opa_url": self.opa_url,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _convert_context_to_opa_input(self, context: PolicyContext) -> Dict[str, Any]:
        """Convert PolicyContext to OPA input format."""
        return {
            "input": {
                "user_id": context.user_id,
                "tenant_id": context.tenant_id,
                "agent_id": context.agent_id,
                "resource": context.resource,
                "action": context.action,
                "environment": context.environment,
                "metadata": context.metadata or {}
            }
        }
    
    async def _query_opa(self, query_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a query to OPA."""
        # This is a simplified implementation
        # In a real implementation, you would use httpx or similar to make HTTP requests to OPA
        
        # Simulate OPA response for now
        await asyncio.sleep(0.01)  # Simulate network delay
        
        # Mock response based on query
        if "health" in query_path or query_path == "data":
            return {"result": {"status": "ok"}}
        elif "policy" in query_path:
            return {
                "result": {
                    "decision": "allow",
                    "reason": "Policy evaluation successful",
                    "metadata": {"evaluated_at": datetime.utcnow().isoformat()}
                }
            }
        else:
            return {"result": {}}
    
    def _convert_opa_result_to_policy_result(self, 
                                           opa_result: Dict[str, Any], 
                                           policy_id: str, 
                                           context: PolicyContext) -> PolicyResult:
        """Convert OPA result to PolicyResult."""
        result_data = opa_result.get("result", {})
        
        # Determine decision
        decision_str = result_data.get("decision", "unknown").lower()
        if decision_str == "allow":
            decision = PolicyDecision.ALLOW
        elif decision_str == "deny":
            decision = PolicyDecision.DENY
        elif decision_str == "warn":
            decision = PolicyDecision.WARN
        else:
            decision = PolicyDecision.UNKNOWN
        
        return PolicyResult(
            decision=decision,
            policy_id=policy_id,
            policy_name=policy_id,
            reason=result_data.get("reason", "Policy evaluated"),
            metadata=result_data.get("metadata", {}),
            timestamp=datetime.utcnow()
        )
    
    def _convert_opa_set_result_to_policy_results(self, 
                                                opa_result: Dict[str, Any], 
                                                policy_set: str, 
                                                context: PolicyContext) -> List[PolicyResult]:
        """Convert OPA set result to PolicyResult list."""
        result_data = opa_result.get("result", {})
        
        if isinstance(result_data, dict):
            return [
                PolicyResult(
                    decision=PolicyDecision.ALLOW,  # Simplified
                    policy_id=f"{policy_set}_{key}",
                    policy_name=f"{policy_set}_{key}",
                    reason=f"Policy set {policy_set} evaluated",
                    metadata=value if isinstance(value, dict) else {},
                    timestamp=datetime.utcnow()
                ) for key, value in result_data.items()
            ]
        
        return []
    
    def _matches_filters(self, 
                        policy_info: Dict[str, Any], 
                        policy_type: Optional[PolicyType], 
                        tags: Optional[List[str]]) -> bool:
        """Check if policy matches the given filters."""
        # Simplified filtering logic
        if policy_type and policy_type.value not in str(policy_info.get("definition", {})):
            return False
        
        if tags:
            policy_tags = policy_info.get("definition", {}).get("tags", [])
            if not any(tag in policy_tags for tag in tags):
                return False
        
        return True

