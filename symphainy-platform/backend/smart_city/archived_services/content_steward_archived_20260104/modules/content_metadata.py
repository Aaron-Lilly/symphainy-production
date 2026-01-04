#!/usr/bin/env python3
"""
Content Steward Service - Content Metadata & Lineage Module

Micro-module for content metadata and lineage operations using Content Metadata Abstraction (ArangoDB).
"""

from typing import Any, Dict, Optional
from datetime import datetime


class ContentMetadata:
    """Content metadata and lineage module for Content Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def get_asset_metadata(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comprehensive metadata using Content Metadata Abstraction (ArangoDB)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_asset_metadata_start",
            success=True,
            details={"asset_id": asset_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "content_metadata", "read"):
                        await self.service.record_health_metric("get_asset_metadata_access_denied", 1.0, {"asset_id": asset_id})
                        await self.service.log_operation_with_telemetry("get_asset_metadata_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read asset metadata")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("get_asset_metadata_tenant_denied", 1.0, {"asset_id": asset_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_asset_metadata_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get content metadata from ArangoDB
            content_metadata = await self.service.content_metadata_abstraction.get_content_metadata(asset_id)
            
            # Get file metadata from Supabase via File Management
            file_record = await self.service.file_management_abstraction.get_file(asset_id)
            
            if content_metadata or file_record:
                # Build comprehensive metadata matching original format
                file_info = file_record or {}
                metadata_dict = content_metadata.get("metadata", {}) if content_metadata else file_record.get("metadata", {})
                
                # Record health metric
                await self.service.record_health_metric(
                    "asset_metadata_retrieved",
                    1.0,
                    {"asset_id": asset_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_asset_metadata_complete",
                    success=True,
                    details={"asset_id": asset_id}
                )
                
                return {
                    "asset_id": asset_id,
                    "status": "success",
                    "metadata": metadata_dict,
                    "content_type": file_info.get("file_type") or content_metadata.get("content_type") if content_metadata else None,
                    "file_size": len(file_info.get("file_content", b"")) if file_info.get("file_content") else content_metadata.get("file_size") if content_metadata else None,
                    "created_at": file_info.get("created_at") or content_metadata.get("created_at") if content_metadata else None,
                    "processing_result": metadata_dict.get("processing_result", {}) if metadata_dict else {},
                    "message": "Asset metadata retrieved successfully"
                }
            else:
                await self.service.record_health_metric("asset_metadata_not_found", 1.0, {"asset_id": asset_id})
                await self.service.log_operation_with_telemetry("get_asset_metadata_complete", success=False, details={"asset_id": asset_id, "reason": "not_found"})
                return {
                    "asset_id": asset_id,
                    "status": "error",
                    "error": "Asset not found",
                    "message": f"Asset {asset_id} not found"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_asset_metadata")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_asset_metadata_complete",
                success=False,
                details={"asset_id": asset_id, "error": str(e)}
            )
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get asset metadata"
            }
    
    async def get_lineage(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get lineage information using Content Metadata Abstraction."""
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
                    if not await security.check_permissions(user_context, "content_metadata", "read"):
                        await self.service.record_health_metric("get_lineage_access_denied", 1.0, {"asset_id": asset_id})
                        await self.service.log_operation_with_telemetry("get_lineage_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read lineage")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("get_lineage_tenant_denied", 1.0, {"asset_id": asset_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_lineage_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get content metadata which may contain lineage info
            content_metadata = await self.service.content_metadata_abstraction.get_content_metadata(asset_id)
            
            # Get file links from File Management Abstraction
            file_record = await self.service.file_management_abstraction.get_file(asset_id)
            
            # Extract lineage from metadata - build transformation history
            metadata = content_metadata.get("metadata", {}) if content_metadata else {}
            
            lineage_info = {
                "asset_id": asset_id,
                "source_file_id": metadata.get("source_file_id") if metadata else None,
                "conversion_date": metadata.get("conversion_date") if metadata else None,
                "optimization_date": metadata.get("optimization_date") if metadata else None,
                "compression_date": metadata.get("compression_date") if metadata else None,
                "created_at": content_metadata.get("created_at") if content_metadata else None,
                "transformations": []
            }
            
            # Build transformation history from metadata
            if metadata.get("source_file_id"):
                lineage_info["transformations"].append({
                    "type": "conversion",
                    "source": metadata["source_file_id"],
                    "date": metadata.get("conversion_date")
                })
            
            if metadata.get("optimization_date"):
                lineage_info["transformations"].append({
                    "type": "optimization",
                    "date": metadata.get("optimization_date")
                })
            
            if metadata.get("compression_date"):
                lineage_info["transformations"].append({
                    "type": "compression",
                    "date": metadata.get("compression_date")
                })
            
            # Try to get file links if available
            if file_record:
                lineage_info["file_uuid"] = file_record.get("uuid")
                lineage_info["file_type"] = file_record.get("file_type")
            
                # Record health metric
                await self.service.record_health_metric(
                    "lineage_retrieved",
                    1.0,
                    {"asset_id": asset_id, "transformation_count": len(lineage_info.get("transformations", []))}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_lineage_complete",
                    success=True,
                    details={"asset_id": asset_id, "transformation_count": len(lineage_info.get("transformations", []))}
                )
                
                return {
                    "asset_id": asset_id,
                    "status": "success",
                    "lineage": lineage_info,
                    "message": "Lineage information retrieved successfully"
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
                "status": "error",
                "error": str(e),
                "message": "Failed to get lineage"
            }
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status and statistics."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get processing statistics matching original format
            status = {
                "total_files": len(self.service.content_registry),  # Backward compatibility
                "processing_queue_size": len(self.service.processing_queue),  # Backward compatibility
                "content_processing_enabled": self.service.content_processing_enabled,
                "metadata_extraction_enabled": self.service.metadata_extraction_enabled,
                "policy_enforcement_enabled": self.service.policy_enforcement_enabled,
                "format_conversion_enabled": self.service.format_conversion_enabled,
                "infrastructure_connected": self.service.is_infrastructure_connected,
                "capabilities": {
                    "file_processing": self.service.file_management_abstraction is not None,
                    "content_metadata": self.service.content_metadata_abstraction is not None,
                    "caching": self.service.cache_abstraction is not None
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "processing_status": status,
                "message": "Processing status retrieved successfully"
            }
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error getting processing status: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get processing status"
            }

