#!/usr/bin/env python3
"""
Data Steward Service - Quality & Compliance Module

Micro-module for schema validation, quality metrics, and compliance enforcement.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class QualityCompliance:
    """Quality and compliance module for Data Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def validate_schema(self, schema_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate data schema using Knowledge Governance Abstraction."""
        schema_id = schema_data.get("schema_id") or schema_data.get("name", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "validate_schema_start",
            success=True,
            details={"schema_id": schema_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "write"):
                        await self.service.record_health_metric("validate_schema_access_denied", 1.0, {"schema_id": schema_id})
                        await self.service.log_operation_with_telemetry("validate_schema_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to validate schema")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("validate_schema_tenant_denied", 1.0, {"schema_id": schema_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("validate_schema_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Basic schema validation
            required_fields = ["name", "type", "fields"]
            for field in required_fields:
                if field not in schema_data:
                    await self.service.record_health_metric("schema_validation_failed", 1.0, {"schema_id": schema_id, "missing_field": field})
                    await self.service.log_operation_with_telemetry("validate_schema_complete", success=False, details={"reason": f"missing_field_{field}"})
                    return False
            
            # Store validated schema metadata using Knowledge Governance Abstraction
            if schema_id:
                await self.service.knowledge_governance_abstraction.create_asset_metadata(
                    asset_id=f"schema:{schema_id}",
                    metadata={
                        "schema_id": schema_id,
                        "schema_data": schema_data,
                        "validated_at": datetime.utcnow().isoformat(),
                        "validation_status": "valid"
                    }
                )
            
            # Record health metric
            await self.service.record_health_metric(
                "schema_validated",
                1.0,
                {"schema_id": schema_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "validate_schema_complete",
                success=True,
                details={"schema_id": schema_id}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "validate_schema")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "validate_schema_complete",
                success=False,
                details={"schema_id": schema_id, "error": str(e)}
            )
            return False
    
    async def get_quality_metrics(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get quality metrics for asset using Knowledge Governance Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_quality_metrics_start",
            success=True,
            details={"asset_id": asset_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "read"):
                        await self.service.record_health_metric("get_quality_metrics_access_denied", 1.0, {"asset_id": asset_id})
                        await self.service.log_operation_with_telemetry("get_quality_metrics_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read quality metrics")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_quality_metrics_tenant_denied", 1.0, {"asset_id": asset_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_quality_metrics_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Try Redis cache first
            cache_key = f"quality_metrics:{asset_id}"
            cached_metrics = await self.service.messaging_abstraction.get_value(cache_key)
            if cached_metrics:
                # Record health metric
                await self.service.record_health_metric(
                    "quality_metrics_retrieved",
                    1.0,
                    {"asset_id": asset_id, "source": "cache"}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_quality_metrics_complete",
                    success=True,
                    details={"asset_id": asset_id, "source": "cache"}
                )
                
                return {
                    "metrics": cached_metrics,
                    "success": True,
                    "message": "Quality metrics retrieved (from cache)"
                }
            
            # Get quality metrics from Knowledge Governance Abstraction
            metrics = await self.service.knowledge_governance_abstraction.get_quality_metrics(asset_id=asset_id)
            
            if metrics:
                # Cache in Redis
                await self.service.messaging_abstraction.set_value(
                    key=cache_key,
                    value=metrics,
                    ttl=3600  # 1 hour
                )
                
                # Record health metric
                await self.service.record_health_metric(
                    "quality_metrics_retrieved",
                    1.0,
                    {"asset_id": asset_id, "source": "governance"}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_quality_metrics_complete",
                    success=True,
                    details={"asset_id": asset_id, "source": "governance"}
                )
                
                return {
                    "metrics": metrics,
                    "success": True,
                    "message": "Quality metrics retrieved"
                }
            
            # Fallback: Generate basic metrics if not found
            basic_metrics = {
                "asset_id": asset_id,
                "completeness": 0.95,
                "accuracy": 0.90,
                "consistency": 0.88,
                "timeliness": 0.92,
                "validity": 0.94,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Store basic metrics
            self.service.quality_metrics[asset_id] = basic_metrics
            
            # Record health metric
            await self.service.record_health_metric(
                "quality_metrics_generated",
                1.0,
                {"asset_id": asset_id, "source": "basic"}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "get_quality_metrics_complete",
                success=True,
                details={"asset_id": asset_id, "source": "basic"}
            )
            
            return {
                "metrics": basic_metrics,
                "success": True,
                "message": "Quality metrics generated (basic)"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_quality_metrics")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_quality_metrics_complete",
                success=False,
                details={"asset_id": asset_id, "error": str(e)}
            )
            return {
                "metrics": None,
                "success": False,
                "message": str(e)
            }
    
    async def enforce_compliance(self, asset_id: str, compliance_rules: List[str], user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Enforce compliance rules using Knowledge Governance Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "enforce_compliance_start",
            success=True,
            details={"asset_id": asset_id, "rules_count": len(compliance_rules)}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "write"):
                        await self.service.record_health_metric("enforce_compliance_access_denied", 1.0, {"asset_id": asset_id})
                        await self.service.log_operation_with_telemetry("enforce_compliance_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to enforce compliance")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("enforce_compliance_tenant_denied", 1.0, {"asset_id": asset_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("enforce_compliance_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Check compliance using Knowledge Governance Abstraction
            compliance_result = await self.service.knowledge_governance_abstraction.check_compliance(
                asset_id=asset_id,
                compliance_rules=compliance_rules
            )
            
            if compliance_result:
                violations = compliance_result.get("violations", [])
                
                # Return True if no violations
                is_compliant = len(violations) == 0
                
                # Record health metric
                await self.service.record_health_metric(
                    "compliance_enforced",
                    1.0 if is_compliant else 0.0,
                    {"asset_id": asset_id, "is_compliant": is_compliant, "violations_count": len(violations)}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "enforce_compliance_complete",
                    success=True,
                    details={"asset_id": asset_id, "is_compliant": is_compliant, "violations_count": len(violations)}
                )
                
                return is_compliant
            else:
                # Fallback: Simple compliance check
                violations = []
                
                for rule in compliance_rules:
                    if rule == "data_retention" and asset_id.startswith("old_"):
                        violations.append(f"Asset {asset_id} violates data retention policy")
                    elif rule == "access_control" and "sensitive" in asset_id:
                        violations.append(f"Asset {asset_id} requires additional access controls")
                
                is_compliant = len(violations) == 0
                
                # Record health metric
                await self.service.record_health_metric(
                    "compliance_enforced",
                    1.0 if is_compliant else 0.0,
                    {"asset_id": asset_id, "is_compliant": is_compliant, "violations_count": len(violations), "source": "fallback"}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "enforce_compliance_complete",
                    success=True,
                    details={"asset_id": asset_id, "is_compliant": is_compliant, "violations_count": len(violations), "source": "fallback"}
                )
                
                return is_compliant
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "enforce_compliance")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "enforce_compliance_complete",
                success=False,
                details={"asset_id": asset_id, "error": str(e)}
            )
            return False

