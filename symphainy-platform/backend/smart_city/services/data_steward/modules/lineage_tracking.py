#!/usr/bin/env python3
"""
Data Steward Service - Lineage Tracking Module

Micro-module for data lineage tracking operations.
"""

import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime


class LineageTracking:
    """Lineage tracking module for Data Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def record_lineage(self, lineage_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Record data lineage using State Management Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "record_lineage_start",
            success=True,
            details={"asset_id": lineage_data.get("asset_id", "unknown")}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "write"):
                        await self.service.record_health_metric("record_lineage_access_denied", 1.0, {"asset_id": lineage_data.get("asset_id")})
                        await self.service.log_operation_with_telemetry("record_lineage_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to record lineage")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        # validate_tenant_access requires both user_tenant_id and resource_tenant_id
                        # For lineage tracking, user is tracking lineage for their own tenant
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("record_lineage_tenant_denied", 1.0, {"asset_id": lineage_data.get("asset_id"), "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("record_lineage_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Generate lineage ID
            lineage_id = str(uuid.uuid4())
            
            # Create lineage record
            lineage_record = {
                "lineage_id": lineage_id,
                "lineage_data": lineage_data,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store lineage using State Management Abstraction (ArangoDB)
            # Lineage is stored as state relationships
            asset_id = lineage_data.get("asset_id", lineage_id)
            
            # Store lineage metadata
            await self.service.state_management_abstraction.store_state(
                state_id=f"lineage:{asset_id}",
                state_data=lineage_record,
                metadata={"type": "lineage", "asset_id": asset_id}
            )
            
            # If lineage has relationships (parent/child assets), store those as state relationships
            if "parent_assets" in lineage_data:
                for parent_id in lineage_data["parent_assets"]:
                    await self.service.state_management_abstraction.store_state(
                        state_id=f"lineage_relationship:{parent_id}:{asset_id}",
                        state_data={
                            "parent_id": parent_id,
                            "child_id": asset_id,
                            "relationship_type": "lineage",
                            "created_at": datetime.utcnow().isoformat()
                        },
                        metadata={"type": "lineage_relationship"}
                    )
            
            if "child_assets" in lineage_data:
                for child_id in lineage_data["child_assets"]:
                    await self.service.state_management_abstraction.store_state(
                        state_id=f"lineage_relationship:{asset_id}:{child_id}",
                        state_data={
                            "parent_id": asset_id,
                            "child_id": child_id,
                            "relationship_type": "lineage",
                            "created_at": datetime.utcnow().isoformat()
                        },
                        metadata={"type": "lineage_relationship"}
                    )
            
            # Store in local tracking for backward compatibility
            self.service.lineage_tracking[lineage_id] = lineage_record
            
            # Record health metric
            await self.service.record_health_metric(
                "lineage_recorded",
                1.0,
                {"lineage_id": lineage_id, "asset_id": asset_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "record_lineage_complete",
                success=True,
                details={"lineage_id": lineage_id, "asset_id": asset_id}
            )
            
            return lineage_id
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "record_lineage")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "record_lineage_complete",
                success=False,
                details={"asset_id": lineage_data.get("asset_id"), "error": str(e)}
            )
            raise
    
    async def get_lineage(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get lineage for asset using State Management Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_lineage_start",
            success=True,
            details={"asset_id": asset_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "read"):
                        await self.service.record_health_metric("get_lineage_access_denied", 1.0, {"asset_id": asset_id})
                        await self.service.log_operation_with_telemetry("get_lineage_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read lineage")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_lineage_tenant_denied", 1.0, {"asset_id": asset_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_lineage_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get lineage from State Management Abstraction
            lineage_state = await self.service.state_management_abstraction.get_state(
                state_key=f"lineage:{asset_id}"
            )
            
            if lineage_state:
                # Get related lineage relationships
                # This would require querying ArangoDB graph, but for now return the stored lineage
                lineage_data = lineage_state.get("state_data") if isinstance(lineage_state, dict) else lineage_state
                
                # Record health metric
                await self.service.record_health_metric(
                    "lineage_retrieved",
                    1.0,
                    {"asset_id": asset_id, "source": "state_management"}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_lineage_complete",
                    success=True,
                    details={"asset_id": asset_id, "source": "state_management"}
                )
                
                return {
                    "lineage": lineage_data,
                    "success": True,
                    "message": "Lineage found"
                }
            
            # Fallback: Check local tracking
            for lineage_id, lineage_record in self.service.lineage_tracking.items():
                if lineage_record.get("lineage_data", {}).get("asset_id") == asset_id:
                    # Record health metric
                    await self.service.record_health_metric(
                        "lineage_retrieved",
                        1.0,
                        {"asset_id": asset_id, "source": "local"}
                    )
                    
                    # End telemetry tracking
                    await self.service.log_operation_with_telemetry(
                        "get_lineage_complete",
                        success=True,
                        details={"asset_id": asset_id, "source": "local"}
                    )
                    
                    return {
                        "lineage": lineage_record,
                        "success": True,
                        "message": "Lineage found (local)"
                    }
            
            # No lineage found
            await self.service.record_health_metric(
                "lineage_not_found",
                1.0,
                {"asset_id": asset_id}
            )
            
            await self.service.log_operation_with_telemetry(
                "get_lineage_complete",
                success=False,
                details={"asset_id": asset_id, "reason": "not_found"}
            )
            
            return {
                "lineage": None,
                "success": False,
                "message": f"No lineage found for asset: {asset_id}"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_lineage")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_lineage_complete",
                success=False,
                details={"asset_id": asset_id, "error": str(e)}
            )
            return {
                "lineage": None,
                "success": False,
                "message": str(e)
            }
    
    async def query_lineage(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query lineage with filters (SOA API - Phase 3.3).
        
        Args:
            filters: Optional filters (asset_id, operation, timestamp_range, etc.)
            user_context: Optional user context for security
            
        Returns:
            List of lineage records matching filters
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "query_lineage_start",
            success=True,
            details={"filters": filters}
        )
        
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "read"):
                        await self.service.record_health_metric("query_lineage_access_denied", 1.0, {})
                        await self.service.log_operation_with_telemetry("query_lineage_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to query lineage")
            
            # Tenant validation
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        # validate_tenant_access requires both user_tenant_id and resource_tenant_id
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("query_lineage_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("query_lineage_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            results = []
            
            # Query from State Management Abstraction if filters provided
            if filters:
                asset_id = filters.get("asset_id")
                if asset_id:
                    # Get specific lineage
                    lineage = await self.get_lineage(asset_id, user_context)
                    if lineage.get("success"):
                        results.append(lineage.get("lineage"))
                else:
                    # Query by operation or other filters
                    # For now, return local tracking matches
                    operation = filters.get("operation")
                    for lineage_id, lineage_record in self.service.lineage_tracking.items():
                        lineage_data = lineage_record.get("lineage_data", {})
                        if not operation or lineage_data.get("operation") == operation:
                            results.append({
                                "lineage_id": lineage_id,
                                "lineage_data": lineage_data
                            })
            else:
                # Return all lineage from local tracking
                for lineage_id, lineage_record in self.service.lineage_tracking.items():
                    results.append({
                        "lineage_id": lineage_id,
                        "lineage_data": lineage_record.get("lineage_data", {})
                    })
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "query_lineage_complete",
                success=True,
                details={"count": len(results)}
            )
            
            return results
            
        except (PermissionError, ValueError):
            raise
        except Exception as e:
            await self.service.handle_error_with_audit(e, "query_lineage")
            await self.service.log_operation_with_telemetry(
                "query_lineage_complete",
                success=False,
                details={"error": str(e)}
            )
            return []






