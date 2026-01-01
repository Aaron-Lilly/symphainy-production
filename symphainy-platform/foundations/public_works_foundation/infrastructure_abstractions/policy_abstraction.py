"""
Policy Abstraction - Infrastructure abstraction for policy management

Coordinates policy adapters and handles infrastructure-level concerns like
error handling, retries, logging, and adapter selection.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.policy_protocol import (
    PolicyProtocol, PolicyContext, PolicyResult, PolicyDecision, PolicyType
)

# Alias for backward compatibility
PolicyEvaluationResult = PolicyResult

class PolicyAbstraction:
    """
    Policy Abstraction - Infrastructure abstraction for policy management
    
    Coordinates different policy adapters and handles infrastructure-level concerns.
    This layer provides swappable policy engines and infrastructure coordination.
    
    NOTE: This abstraction accepts a policy adapter via dependency injection.
          All adapter creation happens in Public Works Foundation Service.
    """
    
    def __init__(self,
                 policy_adapter: PolicyProtocol,  # Required: Accept adapter via DI
                 config_adapter=None,
                 service_name: str = "policy_abstraction",
                 di_container=None):
        """
        Initialize Policy Abstraction.
        
        Args:
            policy_adapter: Policy adapter implementing PolicyProtocol (required)
            config_adapter: Configuration adapter (optional)
            service_name: Service name for logging (optional)
            di_container: DI Container for logging (required)
        """
        if not policy_adapter:
            raise ValueError("PolicyAbstraction requires policy_adapter via dependency injection")
        if not di_container:
            raise ValueError("DI Container is required for PolicyAbstraction initialization")
        
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        self.config_adapter = config_adapter
        
        # Use injected adapter
        self.adapter = policy_adapter
        self.adapter_type = getattr(policy_adapter, 'adapter_type', 'unknown')
        
        # Infrastructure-level configuration
        self.max_retries = 3
        self.retry_delay = 0.1
        self.timeout = 30
        
        self.logger.info(f"Initialized Policy Abstraction with {self.adapter_type} adapter")
    
    async def evaluate_policy(self, 
                            policy_id: str,
                            context: Dict[str, Any] = None) -> PolicyEvaluationResult:
        """Evaluate a specific policy with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Evaluating policy {policy_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Evaluate with retry logic
            result = await self._evaluate_with_retry(
                self.adapter.evaluate_policy,
                policy_id,
                enhanced_context
            )
            
            # Add infrastructure-level metadata
            result.metadata = result.metadata or {}
            result.metadata.update({
                "adapter_type": self.adapter_type,
                "abstraction_layer": "policy_abstraction",
                "evaluated_at": datetime.utcnow().isoformat()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Policy evaluation failed for {policy_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def evaluate_multiple_policies(self,
                              policy_ids: List[str],
                              context: Dict[str, Any] = None) -> List[PolicyEvaluationResult]: 
        """Evaluate multiple policies with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Evaluating {len(policy_ids)} policies with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Evaluate with retry logic
            results = await self._evaluate_with_retry(
                self.adapter.evaluate_policies,
                policy_ids,
                enhanced_context
            )
            
            # Add infrastructure-level metadata to all results
            for result in results:
                result.metadata = result.metadata or {}
                result.metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "policy_abstraction",
                    "evaluated_at": datetime.utcnow().isoformat()
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Policy evaluation failed for {len(policy_ids)} policies: {e}")
            raise  # Re-raise for service layer to handle
    
    async def evaluate_policy_set(self,
                                policy_set: str,
                                context: Dict[str, Any] = None) -> List[PolicyEvaluationResult]:
        """Evaluate all policies in a policy set with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Evaluating policy set {policy_set} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Evaluate with retry logic
            results = await self._evaluate_with_retry(
                self.adapter.evaluate_policy_set,
                policy_set,
                enhanced_context
            )
            
            # Add infrastructure-level metadata to all results
            for result in results:
                result.metadata = result.metadata or {}
                result.metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "policy_abstraction",
                    "evaluated_at": datetime.utcnow().isoformat()
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Policy set evaluation failed for {policy_set}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_policy_definition(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy definition with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting policy {policy_id} with {self.adapter_type}")
            
            # Get policy with retry logic
            policy = await self._evaluate_with_retry(
                self.adapter.get_policy,
                policy_id
            )
            
            if policy:
                policy["adapter_type"] = self.adapter_type
                policy["abstraction_layer"] = "policy_abstraction"
                policy["retrieved_at"] = datetime.utcnow().isoformat()
            
            return policy
            
        except Exception as e:
            self.logger.error(f"Failed to get policy {policy_id}: {e}")
            raise  # Re-raise for service layer to handle

        """List available policies with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Listing policies with {self.adapter_type}")
            
            # List policies with retry logic
            policies = await self._evaluate_with_retry(
                self.adapter.list_policies,
                policy_type,
                tags
            )
            
            # Add infrastructure-level metadata to all policies
            for policy in policies:
                policy["adapter_type"] = self.adapter_type
                policy["abstraction_layer"] = "policy_abstraction"
                policy["listed_at"] = datetime.utcnow().isoformat()
            
            return policies
            
        except Exception as e:
            self.logger.error(f"Failed to list policies: {e}")
            raise  # Re-raise for service layer to handle

        """Check policy infrastructure health."""
        try:
            self.logger.debug("Checking policy infrastructure health")
            
            # Check adapter health
            adapter_health = await self.adapter.health_check()
            
            # Add abstraction-level health info
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "unhealthy",
                "abstraction_layer": "policy_abstraction",
                "adapter_type": self.adapter_type,
                "adapter_health": adapter_health,
                "infrastructure_metrics": {
                    "max_retries": self.max_retries,
                    "retry_delay": self.retry_delay,
                    "timeout": self.timeout
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Policy infrastructure health check failed: {e}")
    
            raise  # Re-raise for service layer to handle
    
    def _enhance_context(self, context: PolicyContext) -> PolicyContext:
        """Add infrastructure-level context enhancements."""
        # Add infrastructure metadata
        enhanced_metadata = context.metadata or {}
        enhanced_metadata.update({
            "abstraction_layer": "policy_abstraction",
            "adapter_type": self.adapter_type,
            "evaluation_timestamp": datetime.utcnow().isoformat()
        })
        
        # Create enhanced context
        return PolicyContext(
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            resource=context.resource,
            action=context.action,
            environment=context.environment,
            metadata=enhanced_metadata
        )
    
    async def _evaluate_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
                raise  # Re-raise for service layer to handle

