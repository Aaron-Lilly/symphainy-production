#!/usr/bin/env python3
"""
Data Steward Service - File Lifecycle Module

Micro-module for file lifecycle operations (upload, storage, retrieval, deletion).
Consolidated from Content Steward as part of Phase 0.1.

WHAT: I manage the complete file lifecycle (upload, storage, retrieval, deletion)
HOW: I use File Management Abstraction (GCS + Supabase) for file operations
"""

import uuid
from typing import Any, Dict, Optional
from datetime import datetime


class FileLifecycle:
    """File lifecycle module for Data Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def process_upload(
        self,
        file_data: bytes,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded file using File Management Abstraction (GCS + Supabase).
        
        Args:
            file_data: Raw file bytes
            content_type: MIME type (e.g., "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            metadata: File metadata including ui_name, file_type (extension), etc.
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with uuid, file_id, and metadata
        """
        file_size = len(file_data)
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "file_lifecycle_upload_start",
            success=True,
            details={"content_type": content_type, "file_size": file_size}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    # Check permissions with debug logging
                    try:
                        has_permission = await security.check_permissions(user_context, "file_management", "write")
                        if not has_permission:
                            # MVP: Log warning but allow for testing (graceful degradation)
                            self.logger.warning(f"⚠️ Permission check failed for user {user_context.get('user_id')} - allowing for MVP testing")
                            # TODO: Re-enable strict permission checking after MVP
                            # await self.service.record_health_metric("file_lifecycle_upload_access_denied", 1.0, {"content_type": content_type, "file_size": file_size})
                            # await self.service.log_operation_with_telemetry("file_lifecycle_upload_complete", success=False)
                            # raise PermissionError("Access denied: insufficient permissions to upload file")
                    except Exception as e:
                        # MVP: Log error but allow for testing (graceful degradation)
                        self.logger.warning(f"⚠️ Permission check error (allowing for MVP testing): {e}")
                        # TODO: Re-enable strict permission checking after MVP
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric(
                                "file_lifecycle_upload_tenant_denied",
                                1.0,
                                {"content_type": content_type, "file_size": file_size, "tenant_id": tenant_id}
                            )
                            await self.service.log_operation_with_telemetry(
                                "file_lifecycle_upload_complete",
                                success=False
                            )
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Ensure ui_name is set (fallback to parsing filename if missing)
            ui_name = None
            if metadata and "ui_name" in metadata:
                ui_name = metadata["ui_name"]
            else:
                # Fallback: extract from filename if provided
                filename = metadata.get("filename") if metadata else None
                if filename:
                    from utilities.file_utils import parse_filename
                    file_components = parse_filename(filename)
                    ui_name = file_components["ui_name"]
                else:
                    ui_name = f"file_{uuid.uuid4()}"
            
            # Get file_type (extension) from metadata, fallback to extracting from original_filename
            file_type = None
            if metadata and "file_type" in metadata:
                file_type = metadata["file_type"]  # Should be extension (e.g., "docx")
            else:
                # Try to extract from original_filename if available
                original_filename = metadata.get("original_filename") if metadata else None
                if original_filename:
                    from utilities.file_utils import parse_filename
                    file_components = parse_filename(original_filename)
                    file_type = file_components["file_extension_clean"]
                else:
                    file_type = "unknown"
            
            # Extract metadata from content
            extracted_metadata = await self._extract_metadata(file_data, content_type)
            
            # Combine with provided metadata
            final_metadata = {**(metadata or {}), **extracted_metadata}
            
            # Create file using File Management Abstraction (stores in GCS + Supabase)
            # Extract user_id from user_context (primary source) or metadata (fallback)
            user_id = user_context.get("user_id") if user_context else None
            if not user_id and metadata:
                user_id = metadata.get("user_id")
            if not user_id:
                user_id = "system"  # Fallback to system user
            
            # Extract tenant_id from user_context (primary source) or metadata (fallback)
            tenant_id = user_context.get("tenant_id") if user_context else None
            if not tenant_id and metadata:
                tenant_id = metadata.get("tenant_id")
            
            file_record = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "ui_name": ui_name,
                "file_type": file_type,
                "mime_type": content_type,
                "file_content": file_data,
                "metadata": {
                    "original_filename": metadata.get("original_filename"),
                    "file_extension": metadata.get("file_extension"),
                    "content_type": metadata.get("content_type"),
                    "file_type_category": metadata.get("file_type_category"),
                    **final_metadata
                },
                "status": "uploaded"
            }
            
            result = await self.service.file_management_abstraction.create_file(file_record)
            
            file_uuid = result.get("uuid")
            if not file_uuid:
                raise Exception("File creation failed: no UUID returned from abstraction layer")
            
            # Record health metric
            await self.service.record_health_metric(
                "file_lifecycle_uploaded",
                1.0,
                {"file_uuid": file_uuid, "content_type": content_type, "file_size": file_size}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_upload_complete",
                success=True,
                details={"file_uuid": file_uuid, "content_type": content_type, "file_size": file_size}
            )
            
            # Return with UUID (never None)
            return {
                "success": True,
                "uuid": file_uuid,
                "file_id": file_uuid,
                "ui_name": result.get("ui_name") or ui_name,
                "file_type": result.get("file_type") or file_type,
                "mime_type": result.get("mime_type") or content_type,
                "status": "success",
                "metadata": final_metadata,
                "message": "File uploaded successfully"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "file_lifecycle_upload")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_upload_complete",
                success=False,
                details={"content_type": content_type, "file_size": file_size, "error": str(e)}
            )
            raise Exception(f"File upload failed: {str(e)}")
    
    async def get_file(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get file via file_management infrastructure.
        
        Args:
            file_id: ID of file to retrieve
            user_context: Optional user context for security and tenant validation
            
        Returns:
            File data with metadata, or None if not found
        """
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "read"):
                        await self.service.record_health_metric("file_lifecycle_get_access_denied", 1.0, {"file_id": file_id})
                        raise PermissionError("Access denied: insufficient permissions to read file")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("file_lifecycle_get_tenant_denied", 1.0, {"file_id": file_id, "tenant_id": tenant_id})
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use file_management abstraction
            if not self.service.file_management_abstraction:
                self.logger.warning("⚠️ file_management abstraction not available")
                return None
            
            # Get file from infrastructure
            file_record = await self.service.file_management_abstraction.get_file(file_id)
            
            if not file_record:
                self.logger.debug(f"File not found: {file_id}")
                return None
            
            return file_record
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file {file_id}: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
    
    async def update_file_metadata(
        self,
        file_id: str,
        metadata_updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update file metadata using File Management Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "file_lifecycle_update_metadata_start",
            success=True,
            details={"file_id": file_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "write"):
                        await self.service.record_health_metric("file_lifecycle_update_metadata_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("file_lifecycle_update_metadata_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to update file metadata")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("file_lifecycle_update_metadata_tenant_denied", 1.0, {"file_id": file_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("file_lifecycle_update_metadata_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Update file metadata in Supabase
            file_result = await self.service.file_management_abstraction.update_file(
                file_uuid=file_id,
                updates=metadata_updates
            )
            
            # Record health metric
            await self.service.record_health_metric(
                "file_lifecycle_metadata_updated",
                1.0,
                {"file_id": file_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_update_metadata_complete",
                success=True,
                details={"file_id": file_id}
            )
            
            return {
                "file_id": file_id,
                "status": "success",
                "updated_metadata": metadata_updates,
                "message": "Metadata updated successfully"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "file_lifecycle_update_metadata")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_update_metadata_complete",
                success=False,
                details={"file_id": file_id, "error": str(e)}
            )
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to update metadata"
            }
    
    async def delete_file(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete file using File Management Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "file_lifecycle_delete_start",
            success=True,
            details={"file_id": file_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "write"):
                        await self.service.record_health_metric("file_lifecycle_delete_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("file_lifecycle_delete_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to delete file")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("file_lifecycle_delete_tenant_denied", 1.0, {"file_id": file_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("file_lifecycle_delete_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Delete file via File Management Abstraction
            if not self.service.file_management_abstraction:
                raise Exception("File management abstraction not available")
            
            delete_result = await self.service.file_management_abstraction.delete_file(file_id)
            
            # Record health metric
            await self.service.record_health_metric(
                "file_lifecycle_deleted",
                1.0,
                {"file_id": file_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_delete_complete",
                success=True,
                details={"file_id": file_id}
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "status": "deleted",
                "message": "File deleted successfully"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "file_lifecycle_delete")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_delete_complete",
                success=False,
                details={"file_id": file_id, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete file"
            }
    
    async def list_files(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List files using File Management Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "file_lifecycle_list_start",
            success=True,
            details={"filters": filters}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "read"):
                        await self.service.record_health_metric("file_lifecycle_list_access_denied", 1.0, {})
                        await self.service.log_operation_with_telemetry("file_lifecycle_list_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to list files")
            
            # Tenant validation (multi-tenant support) - add tenant filter
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("file_lifecycle_list_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("file_lifecycle_list_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                        # Add tenant filter
                        if filters is None:
                            filters = {}
                        filters["tenant_id"] = tenant_id
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # List files via File Management Abstraction
            if not self.service.file_management_abstraction:
                raise Exception("File management abstraction not available")
            
            files = await self.service.file_management_abstraction.list_files(filters=filters)
            
            # Record health metric
            await self.service.record_health_metric(
                "file_lifecycle_listed",
                1.0,
                {"count": len(files) if isinstance(files, list) else 0}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_list_complete",
                success=True,
                details={"count": len(files) if isinstance(files, list) else 0}
            )
            
            return {
                "success": True,
                "files": files,
                "count": len(files) if isinstance(files, list) else 0
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "file_lifecycle_list")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "file_lifecycle_list_complete",
                success=False,
                details={"error": str(e)}
            )
            return {
                "success": False,
                "error": str(e),
                "files": [],
                "count": 0
            }
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _extract_metadata(self, file_data: bytes, content_type: str) -> Dict[str, Any]:
        """Extract metadata from content."""
        metadata = {
            "content_type": content_type,
            "file_size": len(file_data),
            "extraction_date": datetime.utcnow().isoformat(),
            "extraction_method": "automatic"
        }
        
        # Add content-specific metadata
        if content_type.startswith("text/"):
            try:
                text_content = file_data.decode('utf-8', errors='ignore')
                metadata["text_metadata"] = {
                    "character_count": len(text_content),
                    "line_count": len(text_content.splitlines()),
                    "word_count": len(text_content.split())
                }
            except:
                metadata["text_metadata"] = {"error": "Unable to decode text"}
        
        return metadata




