#!/usr/bin/env python3
"""
Content Steward Service - Content Validation Module

Micro-module for content validation and quality metrics.
"""

from typing import Any, Dict, Optional


class ContentValidation:
    """Content validation module for Content Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def validate_content(self, content_data: bytes, content_type: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate content against policies and standards."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "validate_content_start",
            success=True,
            details={"content_type": content_type, "size": len(content_data)}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "content_validation", "read"):
                        await self.service.record_health_metric("validate_content_access_denied", 1.0, {"content_type": content_type})
                        await self.service.log_operation_with_telemetry("validate_content_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to validate content")
            
            # Basic validation checks
            if not content_data or len(content_data) == 0:
                await self.service.record_health_metric("content_validation_failed", 1.0, {"reason": "empty_content"})
                await self.service.log_operation_with_telemetry("validate_content_complete", success=False, details={"reason": "empty_content"})
                return False
            
            # Content type validation
            if not content_type or content_type.strip() == "":
                await self.service.record_health_metric("content_validation_failed", 1.0, {"reason": "invalid_content_type"})
                await self.service.log_operation_with_telemetry("validate_content_complete", success=False, details={"reason": "invalid_content_type"})
                return False
            
            # Size validation (basic check)
            max_size = 100 * 1024 * 1024  # 100MB limit
            if len(content_data) > max_size:
                await self.service.record_health_metric("content_validation_failed", 1.0, {"reason": "size_exceeded"})
                await self.service.log_operation_with_telemetry("validate_content_complete", success=False, details={"reason": "size_exceeded"})
                return False
            
            # Additional validation based on content type
            if content_type.startswith("text/"):
                # Text content validation
                try:
                    content_data.decode('utf-8')
                except UnicodeDecodeError:
                    await self.service.record_health_metric("content_validation_failed", 1.0, {"reason": "encoding_error"})
                    await self.service.log_operation_with_telemetry("validate_content_complete", success=False, details={"reason": "encoding_error"})
                    return False
            
            # Record health metric
            await self.service.record_health_metric(
                "content_validated",
                1.0,
                {"content_type": content_type, "size": len(content_data)}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "validate_content_complete",
                success=True,
                details={"content_type": content_type, "size": len(content_data)}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "validate_content")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "validate_content_complete",
                success=False,
                details={"content_type": content_type, "error": str(e)}
            )
            return False
    
    async def get_quality_metrics(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get quality metrics for content asset using Content Metadata Abstraction."""
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
                    if not await security.check_permissions(user_context, "content_validation", "read"):
                        await self.service.record_health_metric("get_quality_metrics_access_denied", 1.0, {"asset_id": asset_id})
                        await self.service.log_operation_with_telemetry("get_quality_metrics_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read quality metrics")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("get_quality_metrics_tenant_denied", 1.0, {"asset_id": asset_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_quality_metrics_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get content metadata from ArangoDB
            content_metadata = await self.service.content_metadata_abstraction.get_content_metadata(asset_id)
            
            # Get file record for size info
            file_record = await self.service.file_management_abstraction.get_file(asset_id)
            
            if content_metadata or file_record:
                # Calculate quality metrics matching original format
                file_data = file_record.get("file_content", b"") if file_record else b""
                file_size = len(file_data) if file_data else (file_record.get("file_size", 0) if file_record else 0)
                metadata_dict = content_metadata.get("metadata", {}) if content_metadata else (file_record.get("metadata", {}) if file_record else {})
                
                # Calculate quality metrics
                has_metadata = bool(metadata_dict)
                metadata_completeness = min(len(metadata_dict) / 10.0, 1.0)  # Normalized score (0-1.0)
                processing_status = metadata_dict.get("processing_result", {}).get("status", "unknown") if metadata_dict.get("processing_result") else "unknown"
                
                # Calculate quality score from available metadata (Option 1: Simple calculation)
                quality_score = self._calculate_simple_quality_score(
                    metadata_completeness=metadata_completeness,
                    has_metadata=has_metadata,
                    file_size=file_size,
                    processing_status=processing_status
                )
                
                metrics = {
                    "file_size": file_size,
                    "content_type": file_record.get("file_type") if file_record else content_metadata.get("content_type", "unknown") if content_metadata else "unknown",
                    "has_metadata": has_metadata,
                    "metadata_completeness": metadata_completeness,
                    "processing_status": processing_status,
                    "created_at": file_record.get("created_at") if file_record else content_metadata.get("created_at") if content_metadata else None,
                    "quality_score": quality_score
                }
                
                # Store metrics in local registry for backward compatibility
                self.service.quality_metrics[asset_id] = metrics
                
                # Record health metric
                await self.service.record_health_metric(
                    "quality_metrics_retrieved",
                    1.0,
                    {"asset_id": asset_id, "quality_score": quality_score}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_quality_metrics_complete",
                    success=True,
                    details={"asset_id": asset_id, "quality_score": quality_score}
                )
                
                return {
                    "asset_id": asset_id,
                    "status": "success",
                    "quality_metrics": metrics,
                    "message": "Quality metrics retrieved successfully"
                }
            else:
                # Fallback: Return error if asset not found (matching original behavior)
                await self.service.record_health_metric("quality_metrics_not_found", 1.0, {"asset_id": asset_id})
                await self.service.log_operation_with_telemetry("get_quality_metrics_complete", success=False, details={"asset_id": asset_id, "reason": "not_found"})
                return {
                    "status": "error",
                    "error": "Asset not found",
                    "message": f"Asset {asset_id} not found"
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
                "status": "error",
                "error": str(e),
                "message": "Failed to get quality metrics"
            }
    
    def _calculate_simple_quality_score(self, metadata_completeness: float, 
                                        has_metadata: bool, file_size: int,
                                        processing_status: str) -> float:
        """
        Calculate simple quality score from available metadata.
        
        This provides a meaningful quality metric without requiring parsed data.
        For full quality assessment (schema compliance, completeness, consistency),
        use DataAnalyzerService.assess_content_quality() which requires parsed_data.
        
        Args:
            metadata_completeness: Normalized metadata completeness score (0-1.0)
            has_metadata: Whether metadata exists
            file_size: File size in bytes
            processing_status: Processing status ("success", "failed", "unknown")
            
        Returns:
            Quality score (0.0-1.0)
        """
        # Base score from metadata completeness (0-1.0)
        score = min(metadata_completeness, 1.0)
        
        # Bonus for having metadata
        if has_metadata:
            score = min(score + 0.1, 1.0)
        
        # Bonus for successful processing
        if processing_status == "success":
            score = min(score + 0.1, 1.0)
        elif processing_status == "failed":
            score = max(score - 0.2, 0.0)
        
        # Penalty for empty files
        if file_size == 0:
            score = max(score - 0.3, 0.0)
        
        return round(score, 2)

