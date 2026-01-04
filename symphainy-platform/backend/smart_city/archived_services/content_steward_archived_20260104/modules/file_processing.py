#!/usr/bin/env python3
"""
Content Steward Service - File Processing Module

Micro-module for file upload and processing operations using File Management (GCS + Supabase).
"""

import uuid
from typing import Any, Dict, Optional
from datetime import datetime


class FileProcessing:
    """File processing module for Content Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def process_upload(self, file_data: bytes, content_type: str, metadata: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None, workflow_id: Optional[str] = None) -> Dict[str, Any]:
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
            "process_upload_start",
            success=True,
            details={"content_type": content_type, "file_size": file_size}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                self.logger.info(f"🔍 [FILE_PROCESSING] user_context received: type={type(user_context)}, keys={list(user_context.keys()) if isinstance(user_context, dict) else 'N/A'}")
                if isinstance(user_context, dict):
                    permissions = user_context.get('permissions', [])
                    user_id = user_context.get('user_id', 'unknown')
                    self.logger.info(f"🔍 [FILE_PROCESSING] user_id={user_id}, permissions={permissions}, permissions_type={type(permissions)}")
                    
                    # If permissions list is empty or None, this is a problem
                    if not permissions:
                        self.logger.error(f"❌ [FILE_PROCESSING] user_context has no permissions! user_context: {user_context}")
                        self.logger.error(f"❌ [FILE_PROCESSING] This indicates permissions were not propagated from Universal Pillar Router")
                        # ✅ FIXED: Permission propagation is now handled in ContentJourneyOrchestrator.handle_content_upload()
                        # If permissions are still missing, fail the request (zero-trust security)
                        await self.service.record_health_metric("process_upload_missing_permissions", 1.0, {"content_type": content_type, "file_size": file_size})
                        await self.service.log_operation_with_telemetry("process_upload_complete", success=False)
                        raise PermissionError("Access denied: permissions not propagated from Universal Pillar Router")
                    else:
                        security = self.service.get_security()
                        if security:
                            # Check permissions with debug logging
                            try:
                                has_permission = await security.check_permissions(user_context, "file_management", "write")
                                self.logger.info(f"🔍 [FILE_PROCESSING] Permission check result: {has_permission}")
                                if not has_permission:
                                    self.logger.error(f"❌ [FILE_PROCESSING] Permission check failed. user_context: {user_context}")
                                    await self.service.record_health_metric("process_upload_access_denied", 1.0, {"content_type": content_type, "file_size": file_size})
                                    await self.service.log_operation_with_telemetry("process_upload_complete", success=False)
                                    raise PermissionError("Access denied: insufficient permissions to upload file")
                            except PermissionError:
                                # Re-raise PermissionError (don't catch it)
                                raise
                            except Exception as e:
                                # Log other errors but still enforce permission check
                                self.logger.error(f"❌ Permission check error: {e}")
                                raise PermissionError(f"Permission check failed: {str(e)}")
                else:
                    self.logger.error(f"❌ [FILE_PROCESSING] user_context is not a dict: {type(user_context)}")
                    # ✅ FIXED: Require proper user_context format (zero-trust security)
                    await self.service.record_health_metric("process_upload_invalid_user_context", 1.0, {"content_type": content_type, "file_size": file_size})
                    await self.service.log_operation_with_telemetry("process_upload_complete", success=False)
                    raise ValueError(f"user_context must be a dict, got {type(user_context)}")
            else:
                self.logger.error(f"❌ [FILE_PROCESSING] No user_context provided - permission check will fail")
                # ✅ FIXED: Require user_context (zero-trust security)
                await self.service.record_health_metric("process_upload_missing_user_context", 1.0, {"content_type": content_type, "file_size": file_size})
                await self.service.log_operation_with_telemetry("process_upload_complete", success=False)
                raise ValueError("user_context is required for file upload (zero-trust security)")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        # validate_tenant_access requires user_tenant_id and resource_tenant_id
                        # For file upload, user is uploading to their own tenant, so both are the same
                        # Note: validate_tenant_access is not async, returns bool directly
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("process_upload_tenant_denied", 1.0, {"content_type": content_type, "file_size": file_size, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("process_upload_complete", success=False)
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
            
            # FIX 5 & 6: Set data_classification and validate tenant access
            # Default to "client" for user uploads, "platform" for system uploads
            data_classification = metadata.get("data_classification") if metadata else None
            if not data_classification:
                # If tenant_id is present, it's client data; otherwise platform data
                data_classification = "client" if tenant_id else "platform"
            
            # FIX 6: Validate tenant access before storing (enforce tenant isolation)
            if tenant_id and user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    user_tenant_id = user_context.get("tenant_id")
                    if user_tenant_id and user_tenant_id != tenant_id:
                        # User is trying to upload to a different tenant - deny access
                        await self.service.record_health_metric("process_upload_tenant_mismatch", 1.0, {
                            "user_tenant_id": user_tenant_id,
                            "file_tenant_id": tenant_id
                        })
                        await self.service.log_operation_with_telemetry("process_upload_complete", success=False)
                        raise PermissionError(f"Tenant mismatch: user tenant {user_tenant_id} != file tenant {tenant_id}")
                    # Validate tenant access (user can only upload to their own tenant)
                    if not tenant.validate_tenant_access(user_tenant_id or tenant_id, tenant_id):
                        await self.service.record_health_metric("process_upload_tenant_denied", 1.0, {
                            "tenant_id": tenant_id
                        })
                        await self.service.log_operation_with_telemetry("process_upload_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # FIX 1: Ensure original_filename is always tracked
            original_filename = metadata.get("original_filename") if metadata else None
            if not original_filename:
                # Fallback: use filename from metadata or ui_name
                original_filename = metadata.get("filename") if metadata else ui_name
            
            file_record = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "ui_name": ui_name,  # ✅ User-friendly name
                "original_filename": original_filename,  # ✅ FIX 1: Always track original filename
                "file_type": file_type,  # ✅ Extension (not MIME type)
                "mime_type": content_type,  # ✅ MIME type separately
                "data_classification": data_classification,  # ✅ FIX 5: Always set classification
                "file_content": file_data,  # Will be stored in GCS
                "metadata": {
                    "original_filename": original_filename,  # ✅ FIX 1: Ensure this is always present
                    "file_extension": metadata.get("file_extension"),
                    "content_type": metadata.get("content_type"),
                    "file_type_category": metadata.get("file_type_category"),
                    **final_metadata
                },
                "status": "uploaded"
            }
            
            # FIX 2: Workflow orchestration - Update workflow state before upload
            conductor = None
            if workflow_id and hasattr(self.service, 'get_smart_city_api'):
                try:
                    conductor = await self.service.get_smart_city_api("Conductor")
                    if conductor:
                        await conductor.update_workflow_state(
                            workflow_id=workflow_id,
                            state_updates={"status": "uploading", "file_name": ui_name},
                            user_context=user_context
                        )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to update workflow state: {e}")
            
            result = await self.service.file_management_abstraction.create_file(file_record)
            
            file_uuid = result.get("uuid")
            if not file_uuid:
                raise Exception("File creation failed: no UUID returned from abstraction layer")
            
            # FIX 2: Workflow orchestration - Update workflow state after upload
            if conductor and workflow_id:
                try:
                    await conductor.update_workflow_state(
                        workflow_id=workflow_id,
                        state_updates={"status": "uploaded", "file_id": file_uuid},
                        user_context=user_context
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to update workflow state: {e}")
            
            # FIX 3: Event publishing - Publish file_uploaded event
            post_office = None
            if hasattr(self.service, 'get_smart_city_api'):
                try:
                    post_office = await self.service.get_smart_city_api("PostOffice")
                    if post_office:
                        await post_office.publish_event(
                            {
                                "event_type": "file_uploaded",
                                "event_data": {
                                    "file_id": file_uuid,
                                    "ui_name": ui_name,
                                    "original_filename": original_filename,
                                    "file_type": file_type,
                                    "content_type": metadata.get("content_type") if metadata else None,
                                    "data_classification": data_classification,
                                    "tenant_id": tenant_id,
                                    "workflow_id": workflow_id,
                                    "status": "uploaded"
                                }
                            },
                            user_context=user_context
                        )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to publish file_uploaded event: {e}")
            
            # Store content metadata in ArangoDB
            content_metadata = {
                "file_uuid": file_uuid,
                "content_type": metadata.get("content_type") or content_type,  # Use content_type from metadata if available
                "file_size": len(file_data),
                "metadata": final_metadata,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store content metadata (if ArangoDB available, otherwise skip for MVP)
            if self.service.content_metadata_abstraction:
                try:
                    await self.service.content_metadata_abstraction.create_content_metadata(content_metadata)
                except Exception as e:
                    # ArangoDB may not be available - log warning but don't fail the upload
                    self.service.logger.warning(
                        f"⚠️ Failed to store content metadata in ArangoDB (continuing anyway): {e}"
                    )
            
            # Process content for analysis
            processing_result = await self._process_content(file_data, content_type)
            
            # Cache processing result (if caching available)
            if self.service.cache_abstraction:
                cache_key = f"processing:{file_uuid}"
                await self.service.cache_abstraction.set_value(
                    key=cache_key,
                    value=processing_result,
                    ttl=3600  # 1 hour
                )
            
            # Record health metric
            await self.service.record_health_metric(
                "file_uploaded",
                1.0,
                {"file_uuid": file_uuid, "content_type": content_type, "file_size": file_size}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "process_upload_complete",
                success=True,
                details={"file_uuid": file_uuid, "content_type": content_type, "file_size": file_size}
            )
            
            # FIX 1 & 7: Return standardized format with file_id as primary field
            return {
                "success": True,
                "file_id": file_uuid,  # ✅ FIX 1: Primary field (standardized)
                "uuid": file_uuid,  # ✅ Backward compatibility (deprecate later)
                "ui_name": result.get("ui_name") or ui_name,  # ✅ FIX 1: User-friendly name
                "original_filename": original_filename,  # ✅ FIX 1: Original filename for UI
                "file_type": result.get("file_type") or file_type,
                "mime_type": result.get("mime_type") or content_type,
                "data_classification": data_classification,  # ✅ FIX 5: Include classification
                "tenant_id": tenant_id,  # ✅ Include tenant_id
                "data": {  # ✅ FIX 7: Standardized response format
                    "file_id": file_uuid,
                    "ui_name": result.get("ui_name") or ui_name,
                    "original_filename": original_filename,
                    "file_type": result.get("file_type") or file_type,
                    "mime_type": result.get("mime_type") or content_type,
                    "data_classification": data_classification,
                    "tenant_id": tenant_id,
                    "metadata": final_metadata,
                    "processing_result": processing_result
                },
                "metadata": {  # ✅ FIX 7: Additional metadata
                    "status": "success",
                    "message": "File processed successfully"
                }
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "process_upload")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "process_upload_complete",
                success=False,
                details={"content_type": content_type, "file_size": file_size, "error": str(e)}
            )
            # Never return file_id: None - raise exception instead
            raise Exception(f"File upload failed: {str(e)}")
    
    async def get_file_metadata(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve file metadata using File Management and Content Metadata abstractions."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_file_metadata_start",
            success=True,
            details={"file_id": file_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "read"):
                        await self.service.record_health_metric("get_file_metadata_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("get_file_metadata_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read file metadata")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("get_file_metadata_tenant_denied", 1.0, {"file_id": file_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_file_metadata_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get file from File Management Abstraction (Supabase)
            file_record = await self.service.file_management_abstraction.get_file(file_id)
            
            if not file_record:
                await self.service.record_health_metric("file_metadata_not_found", 1.0, {"file_id": file_id})
                await self.service.log_operation_with_telemetry("get_file_metadata_complete", success=False, details={"file_id": file_id, "reason": "not_found"})
                return {
                    "status": "error",
                    "error": "File not found",
                    "message": f"File {file_id} not found"
                }
            
            # Get content metadata from Content Metadata Abstraction (ArangoDB)
            content_metadata = await self.service.content_metadata_abstraction.get_content_metadata(file_id) if self.service.content_metadata_abstraction else None
            
            # Record health metric
            await self.service.record_health_metric(
                "file_metadata_retrieved",
                1.0,
                {"file_id": file_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "get_file_metadata_complete",
                success=True,
                details={"file_id": file_id}
            )
            
            return {
                "file_id": file_id,
                "metadata": file_record.get("metadata", {}),
                "content_metadata": content_metadata or {},
                "content_type": file_record.get("file_type"),
                "created_at": file_record.get("created_at"),
                "status": "success"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_file_metadata")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_file_metadata_complete",
                success=False,
                details={"file_id": file_id, "error": str(e)}
            )
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to retrieve metadata"
            }
    
    async def update_file_metadata(self, file_id: str, metadata_updates: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update file metadata using File Management and Content Metadata abstractions."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "update_file_metadata_start",
            success=True,
            details={"file_id": file_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "write"):
                        await self.service.record_health_metric("update_file_metadata_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("update_file_metadata_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to update file metadata")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            await self.service.record_health_metric("update_file_metadata_tenant_denied", 1.0, {"file_id": file_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("update_file_metadata_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Update file metadata in Supabase
            file_result = await self.service.file_management_abstraction.update_file(
                file_uuid=file_id,
                updates=metadata_updates
            )
            
            # Update content metadata in ArangoDB
            if self.service.content_metadata_abstraction:
                content_updates = {
                    "metadata": metadata_updates,
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                await self.service.content_metadata_abstraction.update_content_metadata(
                    content_id=file_id,
                    updates=content_updates
                )
            
            # Record health metric
            await self.service.record_health_metric(
                "file_metadata_updated",
                1.0,
                {"file_id": file_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "update_file_metadata_complete",
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
            await self.service.handle_error_with_audit(e, "update_file_metadata")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "update_file_metadata_complete",
                success=False,
                details={"file_id": file_id, "error": str(e)}
            )
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to update metadata"
            }
    
    async def process_file_content(self, file_id: str, processing_options: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process file content using File Management Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "process_file_content_start",
            success=True,
            details={"file_id": file_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "write"):
                        await self.service.record_health_metric("process_file_content_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("process_file_content_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to process file content")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get file from GCS via File Management Abstraction
            file_record = await self.service.file_management_abstraction.get_file(file_id)
            
            if not file_record or not file_record.get("file_content"):
                await self.service.record_health_metric("file_content_not_found", 1.0, {"file_id": file_id})
                await self.service.log_operation_with_telemetry("process_file_content_complete", success=False, details={"file_id": file_id, "reason": "not_found"})
                return {
                    "status": "error",
                    "error": "File not found or no content",
                    "message": f"File {file_id} not found or has no content"
                }
            
            file_data = file_record["file_content"]
            content_type = file_record.get("file_type", "application/octet-stream")
            
            # Process with options
            processing_result = await self._process_content(file_data, content_type, processing_options)
            
            # Update metadata with processing result
            await self.update_file_metadata(file_id, {"processing_result": processing_result}, user_context)
            
            # Record health metric
            await self.service.record_health_metric(
                "file_content_processed",
                1.0,
                {"file_id": file_id, "content_type": content_type}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "process_file_content_complete",
                success=True,
                details={"file_id": file_id, "content_type": content_type}
            )
            
            return {
                "file_id": file_id,
                "status": "success",
                "processing_result": processing_result,
                "message": "Content processed successfully"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "process_file_content")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "process_file_content_complete",
                success=False,
                details={"file_id": file_id, "error": str(e)}
            )
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process file content"
            }
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _process_content(self, file_data: bytes, content_type: str, processing_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process content with specified options."""
        processing_result = {
            "status": "processed",
            "content_type": content_type,
            "file_size": len(file_data),
            "processing_date": datetime.utcnow().isoformat(),
            "processing_options": processing_options or {}
        }
        
        # Add content-specific processing
        if content_type.startswith("text/"):
            try:
                text_content = file_data.decode('utf-8', errors='ignore')
                processing_result["text_analysis"] = {
                    "character_count": len(text_content),
                    "line_count": len(text_content.splitlines()),
                    "word_count": len(text_content.split()),
                    "has_encoding": True
                }
            except:
                processing_result["text_analysis"] = {"error": "Unable to decode text"}
        elif content_type.startswith("image/"):
            processing_result["image_analysis"] = {
                "format": content_type.split("/")[1],
                "size_bytes": len(file_data)
            }
        
        return processing_result
    
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






