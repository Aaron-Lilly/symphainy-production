#!/usr/bin/env python3
"""
Data Steward Service - Policy Management Module

Micro-module for content policy management operations.
"""

import uuid
from typing import Any, Dict, Optional
from datetime import datetime


class PolicyManagement:
    """Policy management module for Data Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def create_content_policy(self, data_type: str, rules: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create content policy using Knowledge Governance Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "create_content_policy_start",
            success=True,
            details={"data_type": data_type}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "write"):
                        await self.service.record_health_metric("create_content_policy_access_denied", 1.0, {"data_type": data_type})
                        await self.service.log_operation_with_telemetry("create_content_policy_complete", success=False)
                        raise PermissionError(f"Access denied: insufficient permissions to create content policy for {data_type}")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("create_content_policy_tenant_denied", 1.0, {"data_type": data_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("create_content_policy_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Generate policy ID
            policy_id = str(uuid.uuid4())
            
            # Create governance policy using Knowledge Governance Abstraction
            from foundations.public_works_foundation.abstraction_contracts.knowledge_governance_protocol import PolicyType
            
            # Determine policy type based on rules
            policy_type = PolicyType.DATA_QUALITY  # Default
            if "access_control" in rules:
                policy_type = PolicyType.ACCESS_CONTROL
            elif "retention" in rules:
                policy_type = PolicyType.RETENTION
            elif "classification" in rules:
                policy_type = PolicyType.CLASSIFICATION
            
            # Create policy using Knowledge Governance Abstraction
            created_policy_id = await self.service.knowledge_governance_abstraction.create_governance_policy(
                policy_name=f"{data_type}_policy_{policy_id}",
                policy_type=policy_type,
                policy_data={
                    "policy_id": policy_id,
                    "data_type": data_type,
                    "rules": rules
                },
                description=f"Content policy for {data_type}"
            )
            
            if created_policy_id:
                # Store policy metadata for quick lookup by data_type
                await self.service.knowledge_governance_abstraction.create_asset_metadata(
                    asset_id=f"policy_{data_type}",
                    metadata={
                        "policy_id": created_policy_id,
                        "data_type": data_type,
                        "rules": rules,
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    }
                )
                
                # Cache in Redis
                cache_key = f"policy:{data_type}"
                await self.service.messaging_abstraction.set_value(
                    key=cache_key,
                    value={"policy_id": created_policy_id, "data_type": data_type, "rules": rules},
                    ttl=3600  # 1 hour
                )
                
                # Store in local registry for backward compatibility
                self.service.policy_registry[policy_id] = {
                    "policy_id": policy_id,
                    "governance_policy_id": created_policy_id,
                    "data_type": data_type,
                    "rules": rules,
                    "created_at": datetime.utcnow(),
                    "status": "active"
                }
                
                # Record health metric
                await self.service.record_health_metric(
                    "content_policy_created",
                    1.0,
                    {"data_type": data_type, "policy_id": created_policy_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "create_content_policy_complete",
                    success=True,
                    details={"data_type": data_type, "policy_id": created_policy_id}
                )
                
                return created_policy_id
            else:
                raise Exception("Failed to create governance policy")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "create_content_policy")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "create_content_policy_complete",
                success=False,
                details={"data_type": data_type, "error": str(e)}
            )
            raise
    
    async def get_policy_for_content(self, content_type: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get policy for content type using Knowledge Governance Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_policy_for_content_start",
            success=True,
            details={"content_type": content_type}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "read"):
                        await self.service.record_health_metric("get_policy_for_content_access_denied", 1.0, {"content_type": content_type})
                        await self.service.log_operation_with_telemetry("get_policy_for_content_complete", success=False)
                        raise PermissionError(f"Access denied: insufficient permissions to read policy for {content_type}")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_policy_for_content_tenant_denied", 1.0, {"content_type": content_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_policy_for_content_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Try Redis cache first
            cache_key = f"policy:{content_type}"
            cached_policy = await self.service.messaging_abstraction.get_value(cache_key)
            if cached_policy:
                # Get full policy from Knowledge Governance
                policy_id = cached_policy.get("policy_id")
                if policy_id:
                    # Get policy details from governance abstraction
                    policies = await self.service.knowledge_governance_abstraction.get_governance_policies()
                    policy = next((p for p in policies if p.get("_key") == policy_id), None)
                    
                    if policy:
                        # Record health metric
                        await self.service.record_health_metric(
                            "policy_retrieved",
                            1.0,
                            {"content_type": content_type, "source": "cache"}
                        )
                        
                        # End telemetry tracking
                        await self.service.log_operation_with_telemetry(
                            "get_policy_for_content_complete",
                            success=True,
                            details={"content_type": content_type, "source": "cache"}
                        )
                        
                        return {
                            "policy": policy,
                            "success": True,
                            "message": "Policy found (from cache)"
                        }
            
            # Fallback: Get from asset metadata
            metadata = await self.service.knowledge_governance_abstraction.get_asset_metadata(
                asset_id=f"policy_{content_type}"
            )
            
            if metadata and metadata.get("policy_id"):
                policy_id = metadata.get("policy_id")
                # Get full policy details
                policies = await self.service.knowledge_governance_abstraction.get_governance_policies()
                policy = next((p for p in policies if p.get("_key") == policy_id), None)
                
                if policy:
                    # Record health metric
                    await self.service.record_health_metric(
                        "policy_retrieved",
                        1.0,
                        {"content_type": content_type, "source": "metadata"}
                    )
                    
                    # End telemetry tracking
                    await self.service.log_operation_with_telemetry(
                        "get_policy_for_content_complete",
                        success=True,
                        details={"content_type": content_type, "source": "metadata"}
                    )
                    
                    return {
                        "policy": policy,
                        "success": True,
                        "message": "Policy found"
                    }
            
            # No policy found
            await self.service.record_health_metric(
                "policy_not_found",
                1.0,
                {"content_type": content_type}
            )
            
            await self.service.log_operation_with_telemetry(
                "get_policy_for_content_complete",
                success=False,
                details={"content_type": content_type, "reason": "not_found"}
            )
            
            return {
                "policy": None,
                "success": False,
                "message": f"No policy found for content type: {content_type}"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_policy_for_content")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_policy_for_content_complete",
                success=False,
                details={"content_type": content_type, "error": str(e)}
            )
            return {
                "policy": None,
                "success": False,
                "message": str(e)
            }






